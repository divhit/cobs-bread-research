#!/usr/bin/env python3
"""
Test Google Search Grounding for COBS Bread review insights.
Uses Gemini 2.5 Flash with Google Search grounding via REST API.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get('GOOGLE_API_KEY')
MODEL_ID = "gemini-2.5-flash"

def get_review_insights_search_grounding(location: str):
    """
    Get comprehensive review insights using Google Search grounding only.
    """

    prompt = f"""
Search the web thoroughly for ALL reviews and feedback about COBS Bread bakery in {location}.

I need you to find and analyze reviews from:
- Google Reviews / Google Maps reviews
- Yelp reviews
- TripAdvisor reviews
- Facebook reviews
- UberEats / DoorDash reviews
- Reddit discussions
- Local food blogs
- Any other review platforms

For this bakery, provide:

## 1. BUSINESS DETAILS
- Full address
- Phone number
- Hours of operation
- Overall ratings from each platform found

## 2. DETAILED REVIEW ANALYSIS

### What Customers LOVE (with specific quotes if available):
- Most praised bread products
- Most praised pastries/sweets
- Service quality mentions
- Staff mentions by name if any
- Atmosphere comments
- Value/pricing perceptions

### What Customers COMPLAIN About (with specific quotes if available):
- Products that received negative feedback
- Service issues
- Pricing complaints
- Quality inconsistency issues
- Any recurring problems

### Specific Products Mentioned:
- List every product mentioned in reviews (breads, pastries, sandwiches, etc.)
- Note whether feedback was positive or negative for each

## 3. REVIEW STATISTICS
- Total reviews found across all platforms
- Rating breakdown by platform
- Date range of reviews analyzed

## 4. KEY THEMES & PATTERNS
- What makes customers return?
- What drives negative reviews?
- Any seasonal patterns?
- Comparison to competitors mentioned?

Be extremely thorough. Search multiple sources. Quote actual reviews where possible.
Cite which platform each piece of information comes from.
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={API_KEY}"

    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }],
        "tools": [
            {"googleSearch": {}}
        ]
    }

    print(f"Querying Google Search grounding for COBS Bread in {location}...")
    print("=" * 70)

    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=90
    )

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

    data = response.json()

    # Extract text response
    text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response")

    print("\n🔍 GOOGLE SEARCH GROUNDING RESULTS\n")
    print(text)

    # Extract grounding metadata
    print("\n" + "=" * 70)
    print("📚 GROUNDING SOURCES:")

    grounding = data.get("candidates", [{}])[0].get("groundingMetadata", {})

    if grounding:
        # Search queries used
        queries = grounding.get("webSearchQueries", [])
        if queries:
            print(f"\n  Search Queries Used:")
            for q in queries:
                print(f"    - {q}")

        # Grounding chunks (sources)
        chunks = grounding.get("groundingChunks", [])
        if chunks:
            print(f"\n  Sources ({len(chunks)} total):")
            for i, chunk in enumerate(chunks[:15]):  # Show first 15
                web_data = chunk.get("web", {})
                if web_data:
                    print(f"    [{i+1}] {web_data.get('title', 'N/A')}")
                    print(f"        {web_data.get('uri', 'N/A')}")
    else:
        print("  No grounding metadata in response")

    # Save full response
    with open('/tmp/search_grounding_response.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n  Full response saved to /tmp/search_grounding_response.json")

    return data


if __name__ == "__main__":
    location = "Kleinburg, Ontario, Canada"

    print("\n" + "=" * 80)
    print("GOOGLE SEARCH GROUNDING TEST - COBS Bread Reviews")
    print("=" * 80)

    result = get_review_insights_search_grounding(location)

    print("\n\n✅ Test complete!")
