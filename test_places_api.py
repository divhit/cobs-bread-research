#!/usr/bin/env python3
"""
Test Google Places API to get actual review text.
Returns up to 5 reviews with full text, author, date, and rating.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')
GEMINI_API_KEY = os.environ.get('GOOGLE_API_KEY')

def find_place_id(query: str) -> str:
    """Find Place ID using Text Search."""
    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": PLACES_API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress"
    }

    payload = {
        "textQuery": query
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        print(f"Error finding place: {response.status_code}")
        print(response.text)
        return None

    data = response.json()
    places = data.get("places", [])

    if places:
        place = places[0]
        print(f"Found: {place.get('displayName', {}).get('text', 'Unknown')}")
        print(f"Address: {place.get('formattedAddress', 'Unknown')}")
        print(f"Place ID: {place.get('id', 'Unknown')}")
        return place.get('id')

    return None


def get_place_reviews_legacy(place_id: str, sort_by: str = "newest") -> dict:
    """
    Get place details including reviews using LEGACY API (supports newest sorting).

    Args:
        place_id: Google Place ID
        sort_by: "newest" for most recent, "most_relevant" for default sorting
    """
    # Legacy API endpoint with reviews_sort parameter
    url = "https://maps.googleapis.com/maps/api/place/details/json"

    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,rating,user_ratings_total,opening_hours,reviews",
        "reviews_sort": sort_by,
        "key": PLACES_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error getting place details: {response.status_code}")
        print(response.text)
        return None

    data = response.json()
    if data.get("status") != "OK":
        print(f"API Error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
        return None

    return data.get("result", {})


def get_place_reviews_new(place_id: str) -> dict:
    """
    Get place details using NEW API (only supports relevance sorting).
    """
    url = f"https://places.googleapis.com/v1/places/{place_id}"

    headers = {
        "X-Goog-Api-Key": PLACES_API_KEY,
        "X-Goog-FieldMask": "id,displayName,formattedAddress,nationalPhoneNumber,rating,userRatingCount,regularOpeningHours,reviews"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error getting place details: {response.status_code}")
        print(response.text)
        return None

    return response.json()


if __name__ == "__main__":
    print("=" * 70)
    print("GOOGLE PLACES API - Fetching Actual Review Text")
    print("=" * 70)

    # Step 1: Find the Place ID
    print("\n1. Finding Place ID for COBS Bread Kleinburg...")
    place_id = find_place_id("COBS Bread Kleinburg Ontario")

    if not place_id:
        print("Could not find place ID")
        exit(1)

    # Step 2: Get place details with reviews (sorted by NEWEST using Legacy API)
    print(f"\n2. Fetching NEWEST reviews using Legacy API...")
    print("-" * 70)

    data = get_place_reviews_legacy(place_id, sort_by="newest")

    if not data:
        print("Could not fetch place details")
        exit(1)

    # Display business info
    print(f"\n📍 BUSINESS INFO:")
    print(f"   Name: {data.get('name', 'N/A')}")
    print(f"   Address: {data.get('formatted_address', 'N/A')}")
    print(f"   Phone: {data.get('formatted_phone_number', 'N/A')}")
    print(f"   Rating: {data.get('rating', 'N/A')} ({data.get('user_ratings_total', 0)} reviews)")

    # Display hours
    hours = data.get('opening_hours', {}).get('weekday_text', [])
    if hours:
        print(f"\n   Hours:")
        for h in hours:
            print(f"      {h}")

    # Display reviews
    reviews = data.get('reviews', [])
    print(f"\n📝 NEWEST GOOGLE REVIEWS ({len(reviews)} returned, sorted by date):")
    print("=" * 70)

    for i, review in enumerate(reviews, 1):
        author = review.get('author_name', 'Anonymous')
        rating = review.get('rating', 'N/A')
        time = review.get('relative_time_description', 'Unknown date')
        text = review.get('text', 'No text')

        print(f"\n[{i}] ⭐ {rating}/5 - {author} ({time})")
        print(f"    \"{text}\"")
        print("-" * 70)

    # Save full response
    with open('/tmp/places_api_response.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\nFull response saved to /tmp/places_api_response.json")

    print("\n✅ Done!")
