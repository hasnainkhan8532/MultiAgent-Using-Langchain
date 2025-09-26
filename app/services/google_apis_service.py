"""
Google APIs service for Places, Maps, and other Google services
"""

from googlemaps import Client as GoogleMapsClient
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GoogleAPIsService:
    """Google APIs service for various Google services"""
    
    def __init__(self, api_key: str, places_api_key: str = None, maps_api_key: str = None):
        self.api_key = api_key
        self.places_api_key = places_api_key or api_key
        self.maps_api_key = maps_api_key or api_key
        
        # Initialize Google Maps client
        self.maps_client = GoogleMapsClient(key=self.maps_api_key)
        
        # Initialize Google Places API
        self.places_service = build('places', 'v1', developerKey=self.places_api_key)
    
    def search_places(self, query: str, location: str = None, radius: int = 50000) -> List[Dict[str, Any]]:
        """
        Search for places using Google Places API
        
        Args:
            query: Search query
            location: Location bias (lat,lng)
            radius: Search radius in meters
        
        Returns:
            List of place information
        """
        try:
            # Use Google Maps client for place search
            places_result = self.maps_client.places(
                query=query,
                location=location,
                radius=radius
            )
            
            places = []
            for place in places_result.get('results', []):
                place_info = {
                    'place_id': place.get('place_id'),
                    'name': place.get('name'),
                    'formatted_address': place.get('formatted_address'),
                    'geometry': place.get('geometry'),
                    'rating': place.get('rating'),
                    'price_level': place.get('price_level'),
                    'types': place.get('types', []),
                    'business_status': place.get('business_status'),
                    'photos': place.get('photos', [])
                }
                places.append(place_info)
            
            return places
            
        except Exception as e:
            logger.error(f"Error searching places: {str(e)}")
            return []
    
    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a place
        
        Args:
            place_id: Google Place ID
        
        Returns:
            Detailed place information
        """
        try:
            # Get place details using Google Maps client
            place_details = self.maps_client.place(
                place_id=place_id,
                fields=['name', 'formatted_address', 'geometry', 'rating', 'price_level',
                       'types', 'business_status', 'photos', 'reviews', 'opening_hours',
                       'website', 'formatted_phone_number', 'international_phone_number']
            )
            
            return place_details.get('result', {})
            
        except Exception as e:
            logger.error(f"Error getting place details: {str(e)}")
            return {}
    
    def get_nearby_places(self, location: str, place_type: str = None, 
                         radius: int = 5000) -> List[Dict[str, Any]]:
        """
        Get nearby places
        
        Args:
            location: Location (lat,lng)
            place_type: Type of place to search for
            radius: Search radius in meters
        
        Returns:
            List of nearby places
        """
        try:
            nearby_result = self.maps_client.places_nearby(
                location=location,
                radius=radius,
                type=place_type
            )
            
            places = []
            for place in nearby_result.get('results', []):
                place_info = {
                    'place_id': place.get('place_id'),
                    'name': place.get('name'),
                    'formatted_address': place.get('formatted_address'),
                    'geometry': place.get('geometry'),
                    'rating': place.get('rating'),
                    'price_level': place.get('price_level'),
                    'types': place.get('types', []),
                    'business_status': place.get('business_status')
                }
                places.append(place_info)
            
            return places
            
        except Exception as e:
            logger.error(f"Error getting nearby places: {str(e)}")
            return []
    
    def geocode_address(self, address: str) -> Dict[str, Any]:
        """
        Geocode an address to get coordinates
        
        Args:
            address: Address to geocode
        
        Returns:
            Geocoding result with coordinates
        """
        try:
            geocode_result = self.maps_client.geocode(address)
            
            if geocode_result:
                result = geocode_result[0]
                return {
                    'formatted_address': result.get('formatted_address'),
                    'geometry': result.get('geometry'),
                    'place_id': result.get('place_id'),
                    'types': result.get('types', []),
                    'address_components': result.get('address_components', [])
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error geocoding address: {str(e)}")
            return {}
    
    def reverse_geocode(self, lat: float, lng: float) -> Dict[str, Any]:
        """
        Reverse geocode coordinates to get address
        
        Args:
            lat: Latitude
            lng: Longitude
        
        Returns:
            Reverse geocoding result
        """
        try:
            reverse_geocode_result = self.maps_client.reverse_geocode((lat, lng))
            
            if reverse_geocode_result:
                result = reverse_geocode_result[0]
                return {
                    'formatted_address': result.get('formatted_address'),
                    'geometry': result.get('geometry'),
                    'place_id': result.get('place_id'),
                    'types': result.get('types', []),
                    'address_components': result.get('address_components', [])
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error reverse geocoding: {str(e)}")
            return {}
    
    def get_directions(self, origin: str, destination: str, 
                      mode: str = "driving") -> Dict[str, Any]:
        """
        Get directions between two points
        
        Args:
            origin: Starting point
            destination: Destination point
            mode: Travel mode (driving, walking, bicycling, transit)
        
        Returns:
            Directions result
        """
        try:
            directions_result = self.maps_client.directions(
                origin=origin,
                destination=destination,
                mode=mode
            )
            
            if directions_result:
                route = directions_result[0]
                return {
                    'summary': route.get('summary'),
                    'legs': route.get('legs', []),
                    'overview_polyline': route.get('overview_polyline'),
                    'warnings': route.get('warnings', []),
                    'waypoint_order': route.get('waypoint_order', [])
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting directions: {str(e)}")
            return {}
    
    def analyze_business_location(self, business_address: str) -> Dict[str, Any]:
        """
        Analyze business location for market insights
        
        Args:
            business_address: Business address
        
        Returns:
            Location analysis results
        """
        try:
            # Geocode the business address
            geocode_result = self.geocode_address(business_address)
            
            if not geocode_result:
                return {"error": "Could not geocode business address"}
            
            location = geocode_result.get('geometry', {}).get('location', {})
            lat = location.get('lat')
            lng = location.get('lng')
            
            if not lat or not lng:
                return {"error": "Invalid coordinates"}
            
            # Get nearby businesses
            nearby_businesses = self.get_nearby_places(
                f"{lat},{lng}",
                radius=1000
            )
            
            # Get nearby restaurants
            nearby_restaurants = self.get_nearby_places(
                f"{lat},{lng}",
                place_type="restaurant",
                radius=500
            )
            
            # Get nearby shopping
            nearby_shopping = self.get_nearby_places(
                f"{lat},{lng}",
                place_type="shopping_mall",
                radius=1000
            )
            
            # Analyze competition
            competition_analysis = self._analyze_competition(nearby_businesses)
            
            return {
                'business_location': geocode_result,
                'nearby_businesses': nearby_businesses[:10],  # Top 10
                'nearby_restaurants': nearby_restaurants[:5],  # Top 5
                'nearby_shopping': nearby_shopping[:5],  # Top 5
                'competition_analysis': competition_analysis,
                'location_insights': self._generate_location_insights(
                    geocode_result, nearby_businesses
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing business location: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_competition(self, nearby_businesses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze competition from nearby businesses"""
        if not nearby_businesses:
            return {}
        
        # Count business types
        business_types = {}
        total_rating = 0
        rated_businesses = 0
        
        for business in nearby_businesses:
            types = business.get('types', [])
            for business_type in types:
                business_types[business_type] = business_types.get(business_type, 0) + 1
            
            rating = business.get('rating')
            if rating:
                total_rating += rating
                rated_businesses += 1
        
        avg_rating = total_rating / rated_businesses if rated_businesses > 0 else 0
        
        return {
            'total_nearby_businesses': len(nearby_businesses),
            'business_type_distribution': business_types,
            'average_rating': round(avg_rating, 2),
            'rated_businesses': rated_businesses
        }
    
    def _generate_location_insights(self, geocode_result: Dict[str, Any], 
                                  nearby_businesses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate location insights"""
        address_components = geocode_result.get('address_components', [])
        
        # Extract location details
        city = None
        state = None
        country = None
        
        for component in address_components:
            types = component.get('types', [])
            if 'locality' in types:
                city = component.get('long_name')
            elif 'administrative_area_level_1' in types:
                state = component.get('long_name')
            elif 'country' in types:
                country = component.get('long_name')
        
        return {
            'city': city,
            'state': state,
            'country': country,
            'business_density': len(nearby_businesses),
            'location_type': self._determine_location_type(nearby_businesses)
        }
    
    def _determine_location_type(self, nearby_businesses: List[Dict[str, Any]]) -> str:
        """Determine the type of location based on nearby businesses"""
        if not nearby_businesses:
            return "unknown"
        
        # Count different types of businesses
        business_types = {}
        for business in nearby_businesses:
            types = business.get('types', [])
            for business_type in types:
                business_types[business_type] = business_types.get(business_type, 0) + 1
        
        # Determine location type based on most common business types
        if 'shopping_mall' in business_types or 'store' in business_types:
            return "commercial"
        elif 'restaurant' in business_types or 'food' in business_types:
            return "dining"
        elif 'hospital' in business_types or 'health' in business_types:
            return "healthcare"
        elif 'school' in business_types or 'university' in business_types:
            return "educational"
        else:
            return "mixed"
