"""
Location service module.

Provides geocoding (structured and freeform addresses), Haversine distance
calculation, geographic midpoint computation, and Google Places searches
for suggesting safe, balanced meeting locations between renter and vendor.
"""

import math
import googlemaps
from flask import current_app


class LocationService:
    """Business logic for geocoding, distance, midpoint, and places.

    Uses the Google Maps API for geocoding and places lookups. Distance
    and midpoint calculations use the Haversine formula.
    """

    @staticmethod
    def _get_gmaps_client():
        """Create a Google Maps API client.

        Returns:
            A ``googlemaps.Client`` instance.

        Raises:
            ValueError: If the Google Maps API key is not configured.
        """
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
    def geocode_freeform(address):
        """Convert a full address string to (lat, lng). Returns None on failure."""
        if not address:
            return None
        client = LocationService._get_gmaps_client()
        results = client.geocode(address)
        if not results:
            return None
        loc = results[0]['geometry']['location']
        return (loc['lat'], loc['lng'])

    @staticmethod
    def haversine_distance(lat1, lng1, lat2, lng2):
        """Calculate the great-circle distance in miles between two points.

        Uses the Haversine formula with Earth's radius of 3958.8 miles.

        Args:
            lat1: Latitude of the first point (degrees).
            lng1: Longitude of the first point (degrees).
            lat2: Latitude of the second point (degrees).
            lng2: Longitude of the second point (degrees).

        Returns:
            Distance in miles as a float.
        """
        R = 3958.8  # Earth radius in miles
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlng / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    @staticmethod
    def compute_midpoint(lat1, lng1, lat2, lng2):
        """Compute the geographic midpoint between two points.

        Uses the spherical midpoint formula for accuracy on a globe.

        Args:
            lat1: Latitude of the first point (degrees).
            lng1: Longitude of the first point (degrees).
            lat2: Latitude of the second point (degrees).
            lng2: Longitude of the second point (degrees).

        Returns:
            Tuple of (latitude, longitude) in degrees.
        """
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
        """Find safe public meeting places near a point using Google Places.

        Searches for places of specified types (libraries, parks, police
        stations, etc.) within the given radius, deduplicates by place_id,
        and sorts by distance from the center point.

        Args:
            lat: Latitude of the search center (degrees).
            lng: Longitude of the search center (degrees).
            radius_meters: Search radius in meters (default 5000).
            place_types: List of Google place types to search for.
                Defaults to ['library', 'park', 'police', 'fire_station', 'post_office'].

        Returns:
            List of dicts with name, address, lat, lng, place_type, place_id,
            sorted by distance from the center point.
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

    @staticmethod
    def find_balanced_meeting_places(renter_lat, renter_lng, vendor_lat, vendor_lng, max_results=8):
        """Find meeting locations that are fair for both renter and vendor.

        Searches near the midpoint between both parties, then scores and
        filters results based on distance balance (similar travel for each
        party), proximity to the midpoint, and detour distance. Falls back
        to the full unfiltered list if fewer than 3 places pass the balance
        criteria.

        Args:
            renter_lat: Renter's latitude (degrees).
            renter_lng: Renter's longitude (degrees).
            vendor_lat: Vendor's latitude (degrees).
            vendor_lng: Vendor's longitude (degrees).
            max_results: Maximum number of suggestions to return (default 8).

        Returns:
            List of place dicts with additional distance metrics:
            renter_distance_miles, vendor_distance_miles, midpoint_distance_miles,
            distance_imbalance_miles, total_party_distance_miles, detour_distance_miles.
        """
        mid_lat, mid_lng = LocationService.compute_midpoint(
            renter_lat, renter_lng, vendor_lat, vendor_lng
        )
        all_places = LocationService.find_nearby_places(mid_lat, mid_lng, radius_meters=7000)

        if not all_places:
            return []

        renter_vendor_distance = LocationService.haversine_distance(
            renter_lat, renter_lng, vendor_lat, vendor_lng
        )

        scored = []
        for place in all_places:
            renter_distance = LocationService.haversine_distance(
                renter_lat, renter_lng, place['lat'], place['lng']
            )
            vendor_distance = LocationService.haversine_distance(
                vendor_lat, vendor_lng, place['lat'], place['lng']
            )
            midpoint_distance = LocationService.haversine_distance(
                mid_lat, mid_lng, place['lat'], place['lng']
            )
            total_party_distance = renter_distance + vendor_distance
            # "Between-ness": lower detour means the place lies closer to the
            # path between renter and vendor, not off to one side.
            detour_distance = max(0.0, total_party_distance - renter_vendor_distance)

            scored.append({
                **place,
                'renter_distance_miles': round(renter_distance, 2),
                'vendor_distance_miles': round(vendor_distance, 2),
                'midpoint_distance_miles': round(midpoint_distance, 2),
                'distance_imbalance_miles': round(abs(renter_distance - vendor_distance), 2),
                'total_party_distance_miles': round(total_party_distance, 2),
                'detour_distance_miles': round(detour_distance, 2),
            })

        max_each_party_distance = max(6.0, renter_vendor_distance * 0.8 + 2.0)
        max_midpoint_distance = max(4.0, renter_vendor_distance * 0.7 + 2.0)

        balanced_pool = [
            place for place in scored
            if place['renter_distance_miles'] <= max_each_party_distance
            and place['vendor_distance_miles'] <= max_each_party_distance
            and place['midpoint_distance_miles'] <= max_midpoint_distance
        ]

        pool = balanced_pool if len(balanced_pool) >= 3 else scored
        pool.sort(
            key=lambda place: (
                place['detour_distance_miles'],
                place['total_party_distance_miles'],
                place['midpoint_distance_miles'],
                place['distance_imbalance_miles'],
            )
        )

        return pool[:max_results]
