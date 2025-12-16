#!/usr/bin/env python3
"""Test the full integration of Places API + Search Grounding."""

import os
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

# Import functions directly (avoid Flask import issues)
import requests

GROUNDING_MODEL = "gemini-2.5-flash"

def find_place_id(query: str) -> str:
    api_key = os.environ.get('GOOGLE_PLACES_API_KEY')
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress"
    }
    response = requests.post(url, json={"textQuery": query}, headers=headers, timeout=30)
    if response.status_code == 200:
        places = response.json().get("places", [])
        if places:
            return places[0].get('id')
    return None

def fetch_google_reviews(location: str) -> dict:
    api_key = os.environ.get('GOOGLE_PLACES_API_KEY')
    place_id = find_place_id(f"COBS Bread {location}")
    if not place_id:
        return {'success': False, 'error': 'Could not find place'}

    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,rating,user_ratings_total,reviews",
        "reviews_sort": "newest",
        "key": api_key
    }
    response = requests.get(url, params=params, timeout=30)
    data = response.json()
    if data.get("status") != "OK":
        return {'success': False, 'error': data.get('status')}

    result = data.get("result", {})
    reviews = []
    for r in result.get("reviews", []):
        reviews.append({
            'author': r.get('author_name', 'Anonymous'),
            'rating': r.get('rating', 'N/A'),
            'time': r.get('relative_time_description', 'Unknown'),
            'text': r.get('text', '')
        })
    return {
        'success': True,
        'rating': result.get('rating'),
        'total_reviews': result.get('user_ratings_total'),
        'reviews': reviews
    }

def fetch_search_insights(location: str) -> dict:
    api_key = os.environ.get('GOOGLE_API_KEY')
    prompt = f"Search for reviews of COBS Bread bakery in {location}. Find ratings and feedback from Yelp, UberEats, Reddit, etc."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GROUNDING_MODEL}:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "tools": [{"googleSearch": {}}]
    }
    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=90)
    if response.status_code != 200:
        return {'success': False, 'error': f'API error: {response.status_code}'}

    data = response.json()
    text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    return {'success': True, 'insights': text[:1000] + "..."}  # Truncate for display


if __name__ == "__main__":
    location = "Kleinburg, Ontario"

    print("=" * 70)
    print("TESTING FULL INTEGRATION")
    print("=" * 70)

    # Test 1: Google Reviews
    print("\n1️⃣  GOOGLE REVIEWS (Places API - Newest):")
    print("-" * 50)
    reviews = fetch_google_reviews(location)
    if reviews['success']:
        print(f"   Rating: {reviews['rating']}/5 ({reviews['total_reviews']} total)")
        print(f"   Got {len(reviews['reviews'])} newest reviews:")
        for r in reviews['reviews']:
            print(f"   - {r['author']} ({r['time']}): {r['rating']}⭐ - {r['text'][:80]}...")
    else:
        print(f"   ❌ Failed: {reviews['error']}")

    # Test 2: Search Grounding
    print("\n2️⃣  SEARCH GROUNDING (Multi-platform):")
    print("-" * 50)
    insights = fetch_search_insights(location)
    if insights['success']:
        print(f"   ✅ Got insights:")
        print(f"   {insights['insights'][:500]}...")
    else:
        print(f"   ❌ Failed: {insights['error']}")

    print("\n" + "=" * 70)
    print("✅ Integration test complete!")
    print("=" * 70)
