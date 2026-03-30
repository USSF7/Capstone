import math
import googlemaps
from flask import current_app


class LocationService:
    """Service layer for geocoding, distance, midpoint, and places."""

    @staticmethod
    def _get_gmaps_client():
        api_key = current_app.config['GOOGLE_MAPS_API_KEY']
        if not api_key:
            raise ValueError("Google Maps API key is not configured")
        return googlemaps.Client(key=api_key)

    @staticmethod
    def geocode_address(street_address, city, state, zip_code):
        """Convert address fields to (lat, lng) tuple. Returns None on failure."""
        address_str = f"{street_address}, {city}, {state} {zip_code}"
        client = LocationService._get_gmaps_client()
        results = client.geocode(address_str)
        if not results:
            return None
        loc = results[0]['geometry']['location']
        return (loc['lat'], loc['lng'])

    @staticmethod
    def haversine_distance(lat1, lng1, lat2, lng2):
        """Distance in miles between two points."""
        R = 3958.8  # Earth radius in miles
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlng / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    @staticmethod
    def compute_midpoint(lat1, lng1, lat2, lng2):
        """Geographic midpoint between two points. Returns (lat, lng)."""
        lat1_r, lng1_r = math.radians(lat1), math.radians(lng1)
        lat2_r, lng2_r = math.radians(lat2), math.radians(lng2)
        x = math.cos(lat2_r) * math.cos(lng2_r - lng1_r)
        y = math.cos(lat2_r) * math.sin(lng2_r - lng1_r)
        mid_lat = math.atan2(
            math.sin(lat1_r) + math.sin(lat2_r),
            math.sqrt((math.cos(lat1_r) + x) ** 2 + y ** 2)
        )
        mid_lng = lng1_r + math.atan2(y, math.cos(lat1_r) + x)
        return (math.degrees(mid_lat), math.degrees(mid_lng))

    @staticmethod
    def find_nearby_places(lat, lng, radius_meters=5000, place_types=None):
        """Find safe public meeting places near a point.
        Returns list of dicts: {name, address, lat, lng, place_type, place_id}.
        """
        if place_types is None:
            place_types = ['library', 'park', 'police', 'fire_station', 'post_office']
        client = LocationService._get_gmaps_client()
        results = []
        seen_ids = set()
        for ptype in place_types:
            places = client.places_nearby(
                location=(lat, lng),
                radius=radius_meters,
                type=ptype
            )
            for place in places.get('results', []):
                pid = place['place_id']
                if pid not in seen_ids:
                    seen_ids.add(pid)
                    loc = place['geometry']['location']
                    results.append({
                        'name': place['name'],
                        'address': place.get('vicinity', ''),
                        'lat': loc['lat'],
                        'lng': loc['lng'],
                        'place_type': ptype,
                        'place_id': pid,
                    })
        results.sort(key=lambda p: LocationService.haversine_distance(lat, lng, p['lat'], p['lng']))
        return results
