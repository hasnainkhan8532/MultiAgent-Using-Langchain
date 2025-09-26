"""
Web scraping service with multiple strategies
"""

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from playwright.async_api import async_playwright
from typing import Dict, List, Optional, Any
import json
import time
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)


class WebScraper:
    """Multi-strategy web scraper"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.get('user_agent', 'MultiToolAPI/1.0')
        })
    
    async def scrape_website(self, url: str, strategy: str = "auto") -> Dict[str, Any]:
        """
        Scrape website using specified strategy
        
        Args:
            url: Website URL to scrape
            strategy: Scraping strategy ('requests', 'selenium', 'playwright', 'auto')
        
        Returns:
            Dictionary containing scraped data
        """
        try:
            if strategy == "auto":
                strategy = await self._detect_best_strategy(url)
            
            if strategy == "requests":
                return await self._scrape_with_requests(url)
            elif strategy == "selenium":
                return await self._scrape_with_selenium(url)
            elif strategy == "playwright":
                return await self._scrape_with_playwright(url)
            else:
                raise ValueError(f"Unknown scraping strategy: {strategy}")
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {"error": str(e), "url": url}
    
    async def _detect_best_strategy(self, url: str) -> str:
        """Detect best scraping strategy for URL"""
        try:
            # Try simple request first
            response = self.session.head(url, timeout=10)
            if response.status_code == 200:
                return "requests"
        except:
            pass
        
        # Default to playwright for complex sites
        return "playwright"
    
    async def _scrape_with_requests(self, url: str) -> Dict[str, Any]:
        """Scrape using requests and BeautifulSoup"""
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic information
        data = {
            "url": url,
            "title": soup.title.string if soup.title else "",
            "meta_description": self._get_meta_content(soup, 'description'),
            "meta_keywords": self._get_meta_content(soup, 'keywords'),
            "headings": self._extract_headings(soup),
            "links": self._extract_links(soup, url),
            "images": self._extract_images(soup, url),
            "text_content": self._extract_text_content(soup),
            "forms": self._extract_forms(soup),
            "tables": self._extract_tables(soup),
            "scripts": self._extract_scripts(soup),
            "styles": self._extract_styles(soup),
            "raw_html": str(soup),
            "scraping_method": "requests"
        }
        
        return data
    
    async def _scrape_with_selenium(self, url: str) -> Dict[str, Any]:
        """Scrape using Selenium WebDriver"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-agent={self.config.get("user_agent", "MultiToolAPI/1.0")}')
        
        driver = webdriver.Chrome(options=options)
        
        try:
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source and parse
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            data = {
                "url": url,
                "title": driver.title,
                "meta_description": self._get_meta_content(soup, 'description'),
                "meta_keywords": self._get_meta_content(soup, 'keywords'),
                "headings": self._extract_headings(soup),
                "links": self._extract_links(soup, url),
                "images": self._extract_images(soup, url),
                "text_content": self._extract_text_content(soup),
                "forms": self._extract_forms(soup),
                "tables": self._extract_tables(soup),
                "scripts": self._extract_scripts(soup),
                "styles": self._extract_styles(soup),
                "raw_html": driver.page_source,
                "scraping_method": "selenium"
            }
            
            return data
            
        finally:
            driver.quit()
    
    async def _scrape_with_playwright(self, url: str) -> Dict[str, Any]:
        """Scrape using Playwright"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until='networkidle')
                
                # Get page content
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                data = {
                    "url": url,
                    "title": await page.title(),
                    "meta_description": self._get_meta_content(soup, 'description'),
                    "meta_keywords": self._get_meta_content(soup, 'keywords'),
                    "headings": self._extract_headings(soup),
                    "links": self._extract_links(soup, url),
                    "images": self._extract_images(soup, url),
                    "text_content": self._extract_text_content(soup),
                    "forms": self._extract_forms(soup),
                    "tables": self._extract_tables(soup),
                    "scripts": self._extract_scripts(soup),
                    "styles": self._extract_styles(soup),
                    "raw_html": content,
                    "scraping_method": "playwright"
                }
                
                return data
                
            finally:
                await browser.close()
    
    def _get_meta_content(self, soup: BeautifulSoup, name: str) -> str:
        """Extract meta content by name"""
        meta = soup.find('meta', attrs={'name': name})
        return meta.get('content', '') if meta else ''
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all headings"""
        headings = []
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                headings.append({
                    'level': i,
                    'text': heading.get_text().strip(),
                    'id': heading.get('id', ''),
                    'class': heading.get('class', [])
                })
        return headings
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            links.append({
                'text': link.get_text().strip(),
                'href': href,
                'absolute_url': absolute_url,
                'title': link.get('title', ''),
                'target': link.get('target', '')
            })
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all images"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                absolute_url = urljoin(base_url, src)
                images.append({
                    'src': src,
                    'absolute_url': absolute_url,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', '')
                })
        return images
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all forms"""
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'id': form.get('id', ''),
                'class': form.get('class', []),
                'inputs': []
            }
            
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                input_data = {
                    'type': input_tag.get('type', input_tag.name),
                    'name': input_tag.get('name', ''),
                    'id': input_tag.get('id', ''),
                    'placeholder': input_tag.get('placeholder', ''),
                    'required': input_tag.has_attr('required')
                }
                form_data['inputs'].append(input_data)
            
            forms.append(form_data)
        
        return forms
    
    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all tables"""
        tables = []
        for table in soup.find_all('table'):
            table_data = {
                'id': table.get('id', ''),
                'class': table.get('class', []),
                'rows': []
            }
            
            for row in table.find_all('tr'):
                row_data = []
                for cell in row.find_all(['td', 'th']):
                    row_data.append(cell.get_text().strip())
                table_data['rows'].append(row_data)
            
            tables.append(table_data)
        
        return tables
    
    def _extract_scripts(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all scripts"""
        scripts = []
        for script in soup.find_all('script'):
            if script.string:
                scripts.append({
                    'type': script.get('type', 'text/javascript'),
                    'src': script.get('src', ''),
                    'content': script.string.strip()
                })
        return scripts
    
    def _extract_styles(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all styles"""
        styles = []
        for style in soup.find_all(['style', 'link']):
            if style.name == 'style':
                styles.append({
                    'type': 'inline',
                    'content': style.string.strip() if style.string else ''
                })
            elif style.name == 'link' and style.get('rel') == ['stylesheet']:
                styles.append({
                    'type': 'external',
                    'href': style.get('href', ''),
                    'media': style.get('media', 'all')
                })
        return styles
