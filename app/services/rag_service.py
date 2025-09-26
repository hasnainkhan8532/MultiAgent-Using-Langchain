"""
RAG (Retrieval Augmented Generation) service using LangChain
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.llms import GooglePalm
from langchain.prompts import PromptTemplate
import chromadb
from chromadb.config import Settings
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for document processing and retrieval"""
    
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vectorstore = None
        self.qa_chain = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize ChromaDB vector store"""
        try:
            # Initialize ChromaDB client
            chroma_client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create or get collection
            self.collection = chroma_client.get_or_create_collection(
                name="multitool_documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Initialize LangChain vectorstore
            self.vectorstore = Chroma(
                client=chroma_client,
                collection_name="multitool_documents",
                embedding_function=self.embeddings
            )
            
            logger.info("Vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]], client_id: int) -> List[str]:
        """
        Add documents to the vector store
        
        Args:
            documents: List of document dictionaries
            client_id: Client ID for organization
        
        Returns:
            List of document IDs
        """
        try:
            # Convert to LangChain documents
            langchain_docs = []
            doc_ids = []
            
            for doc in documents:
                # Split text into chunks
                chunks = self.text_splitter.split_text(doc['content'])
                
                for i, chunk in enumerate(chunks):
                    doc_id = str(uuid.uuid4())
                    doc_ids.append(doc_id)
                    
                    langchain_doc = Document(
                        page_content=chunk,
                        metadata={
                            'client_id': client_id,
                            'source_id': doc.get('source_id'),
                            'source_type': doc.get('source_type', 'unknown'),
                            'title': doc.get('title', ''),
                            'chunk_index': i,
                            'doc_id': doc_id
                        }
                    )
                    langchain_docs.append(langchain_doc)
            
            # Add to vector store
            if langchain_docs:
                self.vectorstore.add_documents(langchain_docs)
                logger.info(f"Added {len(langchain_docs)} document chunks to vector store")
            
            return doc_ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def search_documents(self, query: str, client_id: int, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            client_id: Client ID to filter results
            k: Number of results to return
        
        Returns:
            List of relevant document chunks
        """
        try:
            # Search with metadata filter
            results = self.vectorstore.similarity_search(
                query,
                k=k,
                filter={"client_id": client_id}
            )
            
            # Convert to dictionary format
            search_results = []
            for doc in results:
                search_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': getattr(doc, 'score', 0.0)
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def setup_qa_chain(self, gemini_api_key: str):
        """Setup QA chain with Gemini"""
        try:
            # Initialize Gemini LLM
            llm = GooglePalm(
                google_api_key=gemini_api_key,
                temperature=0.1,
                max_output_tokens=1024
            )
            
            # Create prompt template
            prompt_template = """
            Use the following pieces of context to answer the question at the end.
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            
            Context:
            {context}
            
            Question: {question}
            
            Answer: Provide a comprehensive and helpful answer based on the context provided.
            """
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(
                    search_kwargs={"k": 5, "filter": {"client_id": client_id}}
                ),
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True
            )
            
            logger.info("QA chain setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up QA chain: {str(e)}")
            raise
    
    def query(self, question: str, client_id: int) -> Dict[str, Any]:
        """
        Query the RAG system
        
        Args:
            question: Question to ask
            client_id: Client ID for context
        
        Returns:
            Dictionary with answer and sources
        """
        try:
            if not self.qa_chain:
                raise ValueError("QA chain not initialized. Call setup_qa_chain first.")
            
            # Update retriever filter for client
            self.qa_chain.retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 5, "filter": {"client_id": client_id}}
            )
            
            # Query the chain
            result = self.qa_chain({"query": question})
            
            return {
                'answer': result['result'],
                'sources': [
                    {
                        'content': doc.page_content,
                        'metadata': doc.metadata
                    }
                    for doc in result['source_documents']
                ],
                'question': question
            }
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {str(e)}")
            return {
                'answer': f"Error processing query: {str(e)}",
                'sources': [],
                'question': question
            }
    
    def get_client_documents(self, client_id: int) -> List[Dict[str, Any]]:
        """Get all documents for a client"""
        try:
            # Get all documents for client
            results = self.vectorstore.similarity_search(
                "",
                k=1000,  # Large number to get all
                filter={"client_id": client_id}
            )
            
            # Group by source
            sources = {}
            for doc in results:
                source_id = doc.metadata.get('source_id', 'unknown')
                if source_id not in sources:
                    sources[source_id] = {
                        'source_id': source_id,
                        'source_type': doc.metadata.get('source_type', 'unknown'),
                        'title': doc.metadata.get('title', ''),
                        'chunks': []
                    }
                
                sources[source_id]['chunks'].append({
                    'content': doc.page_content,
                    'chunk_index': doc.metadata.get('chunk_index', 0),
                    'metadata': doc.metadata
                })
            
            return list(sources.values())
            
        except Exception as e:
            logger.error(f"Error getting client documents: {str(e)}")
            return []
    
    def delete_client_documents(self, client_id: int) -> bool:
        """Delete all documents for a client"""
        try:
            # Get all document IDs for client
            results = self.vectorstore.similarity_search(
                "",
                k=1000,
                filter={"client_id": client_id}
            )
            
            # Extract document IDs
            doc_ids = [doc.metadata.get('doc_id') for doc in results if doc.metadata.get('doc_id')]
            
            # Delete from vector store
            if doc_ids:
                self.vectorstore.delete(doc_ids)
                logger.info(f"Deleted {len(doc_ids)} documents for client {client_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting client documents: {str(e)}")
            return False
