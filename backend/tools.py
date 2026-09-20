"""
Tools for the Travel Route Planning AI Agent.
Includes:
1. Tavily Search Tool (Real-time web travel search for attractions, advisories, gems)
2. Route Calculation Tool (Estimated distance, travel time by mode, intermediate waypoints)
3. Budget Estimation Tool (Itemized breakdown by travelers, days, mode, tier)
4. Itinerary Generation Tool (Synthesized day-by-day morning/afternoon/evening schedule)
"""

import os
import math
import json
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool

# ─── Known Routes & Hubs ──────────────────────────────────────────────────────
# Realistic road distances (km) for well-known corridors
KNOWN_ROUTES = {
    ("san francisco", "los angeles"): {"road": 615, "air": 543, "rail": 630},
    ("los angeles", "san francisco"): {"road": 615, "air": 543, "rail": 630},
    ("san francisco", "yosemite"): {"road": 310, "air": 240, "rail": 350},
    ("yosemite", "san francisco"): {"road": 310, "air": 240, "rail": 350},
    ("san francisco", "las vegas"): {"road": 920, "air": 670, "rail": 960},
    ("las vegas", "san francisco"): {"road": 920, "air": 670, "rail": 960},
    ("los angeles", "las vegas"): {"road": 435, "air": 370, "rail": 480},
    ("las vegas", "los angeles"): {"road": 435, "air": 370, "rail": 480},
    ("new york", "miami"): {"road": 2035, "air": 1758, "rail": 2100},
    ("miami", "new york"): {"road": 2035, "air": 1758, "rail": 2100},
    ("new york", "chicago"): {"road": 1270, "air": 1145, "rail": 1350},
    ("chicago", "new york"): {"road": 1270, "air": 1145, "rail": 1350},
    ("seattle", "vancouver"): {"road": 230, "air": 190, "rail": 250},
    ("vancouver", "seattle"): {"road": 230, "air": 190, "rail": 250},
    ("london", "paris"): {"road": 465, "air": 340, "rail": 460},
    ("paris", "london"): {"road": 465, "air": 340, "rail": 460},
    ("paris", "amsterdam"): {"road": 505, "air": 430, "rail": 510},
    ("amsterdam", "paris"): {"road": 505, "air": 430, "rail": 510},
    ("paris", "barcelona"): {"road": 1035, "air": 830, "rail": 1060},
    ("barcelona", "paris"): {"road": 1035, "air": 830, "rail": 1060},
    ("rome", "paris"): {"road": 1430, "air": 1100, "rail": 1450},
    ("paris", "rome"): {"road": 1430, "air": 1100, "rail": 1450},
    ("london", "amsterdam"): {"road": 530, "air": 360, "rail": 500},
    ("amsterdam", "london"): {"road": 530, "air": 360, "rail": 500},
    ("zurich", "zermatt"): {"road": 250, "air": 160, "rail": 230},
    ("zermatt", "zurich"): {"road": 250, "air": 160, "rail": 230},
    ("tokyo", "kyoto"): {"road": 476, "air": 370, "rail": 476},
    ("kyoto", "tokyo"): {"road": 476, "air": 370, "rail": 476},
    ("bangkok", "singapore"): {"road": 2340, "air": 1430, "rail": 2400},
    ("singapore", "bangkok"): {"road": 2340, "air": 1430, "rail": 2400},
    ("delhi", "jaipur"): {"road": 280, "air": 240, "rail": 310},
    ("jaipur", "delhi"): {"road": 280, "air": 240, "rail": 310},
    ("delhi", "goa"): {"road": 1870, "air": 1550, "rail": 1940},
    ("goa", "delhi"): {"road": 1870, "air": 1550, "rail": 1940},
    ("delhi", "mumbai"): {"road": 1410, "air": 1140, "rail": 1450},
    ("mumbai", "delhi"): {"road": 1410, "air": 1140, "rail": 1450},
    ("mumbai", "goa"): {"road": 590, "air": 440, "rail": 600},
    ("goa", "mumbai"): {"road": 590, "air": 440, "rail": 600},
}

# Coordinate fallback table
HUB_COORDINATES = {
    "san francisco": (37.7749, -122.4194), "los angeles": (34.0522, -118.2437),
    "new york": (40.7128, -74.0060), "las vegas": (36.1699, -115.1398),
    "seattle": (47.6062, -122.3321), "chicago": (41.8781, -87.6298),
    "miami": (25.7617, -80.1918), "yosemite": (37.8651, -119.5383),
    "grand canyon": (36.1069, -112.1129), "vancouver": (49.2827, -123.1207),
    "toronto": (43.6532, -79.3832), "london": (51.5074, -0.1278),
    "paris": (48.8566, 2.3522), "rome": (41.9028, 12.4964),
    "barcelona": (41.3851, 2.1734), "amsterdam": (52.3676, 4.9041),
    "berlin": (52.5200, 13.4050), "zurich": (47.3769, 8.5417),
    "zermatt": (46.0207, 7.7491), "tokyo": (35.6762, 139.6503),
    "kyoto": (35.0116, 135.7681), "bangkok": (13.7563, 100.5018),
    "singapore": (1.3521, 103.8198), "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090), "goa": (15.2993, 74.1240),
    "jaipur": (26.9124, 75.7873), "sydney": (33.8688, 151.2093),
    "dubai": (25.2048, 55.2708), "bali": (-8.4095, 115.1889),
}

# ─── Well-known scenic stops for popular corridors ──────────────────────────
ROUTE_STOPS_DB = {
    ("san francisco", "los angeles"): [
        {"name": "Santa Cruz & Monterey Bay", "description": "Coastal boardwalk town with world-class aquarium and stunning bay views. Stop for fresh clam chowder.", "recommended_time_spent": "1.5-2 hours", "highlights": ["Monterey Bay Aquarium", "Cannery Row", "Pacific Ocean boardwalk"]},
        {"name": "Big Sur & Bixby Creek Bridge", "description": "One of the most dramatic stretches of coastline in the world. The iconic Bixby Bridge is a must-photograph landmark.", "recommended_time_spent": "1-2 hours", "highlights": ["Bixby Creek Bridge", "McWay Falls", "Pfeiffer Beach"]},
        {"name": "San Luis Obispo & Paso Robles", "description": "Charming college town with vibrant downtown and nearby premium wine country. Great for a lunch break.", "recommended_time_spent": "1-1.5 hours", "highlights": ["Downtown SLO", "Paso Robles wineries", "Bubblegum Alley"]},
        {"name": "Santa Barbara", "description": "The American Riviera — Spanish colonial architecture, pristine beaches, and upscale waterfront dining.", "recommended_time_spent": "1.5-2 hours", "highlights": ["Stearns Wharf", "State Street", "Santa Barbara Mission"]},
    ],
    ("los angeles", "san francisco"): [
        {"name": "Santa Barbara", "description": "The American Riviera — Spanish colonial architecture, pristine beaches, and upscale waterfront dining.", "recommended_time_spent": "1.5-2 hours", "highlights": ["Stearns Wharf", "State Street", "Mission"]},
        {"name": "San Luis Obispo", "description": "Vibrant college town with charming downtown, farm-to-table restaurants, and nearby Hearst Castle.", "recommended_time_spent": "1-1.5 hours", "highlights": ["Hearst Castle (nearby)", "Downtown SLO", "Local wine"]},
        {"name": "Big Sur", "description": "Dramatic Pacific coastline with towering redwoods and the iconic Bixby Bridge.", "recommended_time_spent": "1-2 hours", "highlights": ["Bixby Creek Bridge", "McWay Falls", "Julia Pfeiffer Burns SP"]},
    ],
    ("tokyo", "kyoto"): [
        {"name": "Mt. Fuji Views (Shizuoka / Shin-Fuji Station)", "description": "Stunning views of Mount Fuji from the Shinkansen. Alight at Shin-Fuji for the best lakeside vantage point.", "recommended_time_spent": "30-45 mins (photo stop)", "highlights": ["Mt. Fuji panorama", "Lake Kawaguchiko nearby", "Ekiben bento boxes"]},
        {"name": "Nagoya", "description": "Japan's industrial heartbeat with Nagoya Castle and the famous miso katsu. A worthwhile stopover.", "recommended_time_spent": "2-3 hours", "highlights": ["Nagoya Castle", "Atsuta Shrine", "Miso katsu & hitsumabushi"]},
    ],
    ("delhi", "jaipur"): [
        {"name": "Neemrana Fort Palace", "description": "15th-century heritage fort converted into a stunning palace hotel. Perfect for a scenic tea break on route.", "recommended_time_spent": "1-1.5 hours", "highlights": ["Fort Palace architecture", "Zip-lining", "Royal courtyard chai"]},
    ],
    ("delhi", "goa"): [
        {"name": "Jaipur (Pink City)", "description": "The gateway to Rajasthan with Amber Fort, Hawa Mahal, and vibrant bazaars.", "recommended_time_spent": "Full day recommended", "highlights": ["Amber Fort", "Hawa Mahal", "Johari Bazaar"]},
        {"name": "Udaipur (City of Lakes)", "description": "Romantic lakeside city with ornate palaces and boat rides on Lake Pichola.", "recommended_time_spent": "Full day recommended", "highlights": ["Lake Pichola", "City Palace", "Jagdish Temple"]},
    ],
    ("mumbai", "goa"): [
        {"name": "Lonavala & Khandala", "description": "Scenic hill stations in the Western Ghats with waterfalls and misty mountain views.", "recommended_time_spent": "1-2 hours", "highlights": ["Bhushi Dam", "Tiger's Leap", "Chikki sweet shops"]},
        {"name": "Kolhapur", "description": "Known for the Mahalaxmi Temple and fiery Kolhapuri cuisine — a foodie's detour.", "recommended_time_spent": "1.5-2 hours", "highlights": ["Mahalaxmi Temple", "Kolhapuri misal pav", "Rankala Lake"]},
    ],
    ("zurich", "zermatt"): [
        {"name": "Bern (Swiss Capital)", "description": "UNESCO-listed medieval old town with the famous Bear Park and Zytglogge clock tower.", "recommended_time_spent": "1.5-2 hours", "highlights": ["Old Town (Altstadt)", "Bear Park", "Swiss Parliament views"]},
        {"name": "Visp (Gateway to Zermatt)", "description": "Charming Valais town where you transfer to the scenic Matterhorn Gotthard railway.", "recommended_time_spent": "30-45 mins", "highlights": ["Railway transfer", "Alpine valley views", "Local Valais wine"]},
    ],
    ("london", "paris"): [
        {"name": "Canterbury", "description": "Historic cathedral city and UNESCO World Heritage Site — a quintessential English stopover.", "recommended_time_spent": "1.5-2 hours", "highlights": ["Canterbury Cathedral", "Medieval streets", "Traditional cream tea"]},
    ],
}

# ─── Destination-specific attractions and food ─────────────────────────────
DESTINATION_ATTRACTIONS = {
    "los angeles": [
        {"name": "Griffith Observatory & Hollywood Sign", "category": "Iconic Landmark", "description": "Panoramic views of LA and the Hollywood Sign. Free admission, stunning at sunset.", "best_time_to_visit": "Late Afternoon / Sunset", "estimated_entry_cost": "Free", "tags": ["Iconic", "Photography", "Views"]},
        {"name": "Santa Monica Pier & Venice Beach", "category": "Beach & Entertainment", "description": "Iconic boardwalk with rides, street performers, Muscle Beach, and vibrant Venice canals.", "best_time_to_visit": "Morning to Afternoon", "estimated_entry_cost": "Free", "tags": ["Beach", "Entertainment", "Boardwalk"]},
        {"name": "The Getty Center", "category": "Art & Architecture", "description": "World-class art museum with stunning architecture by Richard Meier. Free entry, gorgeous gardens.", "best_time_to_visit": "Morning", "estimated_entry_cost": "Free (parking $20)", "tags": ["Art", "Architecture", "Gardens"]},
        {"name": "Grand Central Market (Downtown LA)", "category": "Food & Culture", "description": "Historic food hall since 1917, packed with diverse vendors — tacos, ramen, Thai, and artisanal coffee.", "best_time_to_visit": "Lunch (11 AM - 2 PM)", "estimated_entry_cost": "Free entry", "tags": ["Food", "Culture", "Historic"]},
    ],
    "san francisco": [
        {"name": "Golden Gate Bridge & Battery Spencer", "category": "Iconic Landmark", "description": "Walk or bike across the 1.7-mile suspension bridge. Battery Spencer offers the best photo angle.", "best_time_to_visit": "Early Morning (fog clears)", "estimated_entry_cost": "Free", "tags": ["Iconic", "Photography", "Outdoors"]},
        {"name": "Alcatraz Island", "category": "Historic Site", "description": "Former federal penitentiary on an island in the bay. Audio tour is outstanding. Book 2-3 weeks ahead.", "best_time_to_visit": "Morning ferry", "estimated_entry_cost": "$42/adult", "tags": ["History", "Unique", "Must-Book"]},
        {"name": "Fisherman's Wharf & Pier 39", "category": "Waterfront", "description": "Sea lions, sourdough bread bowls, crab stands, and bay views. Touristy but essential.", "best_time_to_visit": "Lunchtime", "estimated_entry_cost": "Free", "tags": ["Seafood", "Waterfront", "Family"]},
    ],
    "kyoto": [
        {"name": "Fushimi Inari Shrine (千本鳥居)", "category": "Sacred Shrine", "description": "Thousands of vermillion torii gates winding up a mountainside. Kyoto's most photographed site.", "best_time_to_visit": "Early Morning (6-7 AM) to avoid crowds", "estimated_entry_cost": "Free", "tags": ["Shrine", "Photography", "Iconic"]},
        {"name": "Arashiyama Bamboo Grove", "category": "Natural Wonder", "description": "Towering bamboo stalks creating an ethereal green corridor. Combine with Tenryu-ji Temple next door.", "best_time_to_visit": "Early Morning", "estimated_entry_cost": "Free (temple: ¥500)", "tags": ["Nature", "Photography", "Peaceful"]},
        {"name": "Kinkaku-ji (Golden Pavilion)", "category": "Temple", "description": "Gold-leaf covered Zen temple reflecting in its mirror pond. One of Japan's most iconic images.", "best_time_to_visit": "Morning", "estimated_entry_cost": "¥400 (~$3)", "tags": ["Temple", "Architecture", "Historic"]},
        {"name": "Nishiki Market (京の台所)", "category": "Food Market", "description": "Kyoto's Kitchen — a narrow 5-block market with 100+ vendors selling pickles, matcha sweets, fresh tofu, and street snacks.", "best_time_to_visit": "Late Morning (10-12 PM)", "estimated_entry_cost": "Free entry", "tags": ["Food", "Market", "Culture"]},
    ],
    "paris": [
        {"name": "Eiffel Tower & Champ de Mars", "category": "Iconic Landmark", "description": "324-meter iron lattice tower. Book summit tickets in advance. Best at dusk when lights sparkle.", "best_time_to_visit": "Sunset / Evening", "estimated_entry_cost": "€26 (summit)", "tags": ["Iconic", "Photography", "Views"]},
        {"name": "Louvre Museum", "category": "World-Class Museum", "description": "World's largest art museum housing the Mona Lisa, Venus de Milo, and 35,000+ works. Budget 3-4 hours minimum.", "best_time_to_visit": "Wednesday/Friday evening (open late)", "estimated_entry_cost": "€17", "tags": ["Art", "History", "Culture"]},
        {"name": "Montmartre & Sacré-Cœur", "category": "Historic Quarter", "description": "Bohemian hilltop village with cobblestone streets, artist studios, and panoramic Paris views from the basilica steps.", "best_time_to_visit": "Morning", "estimated_entry_cost": "Free", "tags": ["Culture", "Art", "Views"]},
    ],
    "tokyo": [
        {"name": "Senso-ji Temple (浅草寺)", "category": "Historic Temple", "description": "Tokyo's oldest Buddhist temple in Asakusa. Walk through Kaminarimon gate and Nakamise shopping street.", "best_time_to_visit": "Early Morning (before 8 AM)", "estimated_entry_cost": "Free", "tags": ["Temple", "Culture", "Shopping"]},
        {"name": "Shibuya Crossing & Shibuya Sky", "category": "Iconic Urban", "description": "World's busiest pedestrian scramble. Shibuya Sky rooftop offers 360° views from the 46th floor.", "best_time_to_visit": "Evening", "estimated_entry_cost": "¥2000 (~$14) for Sky", "tags": ["Urban", "Photography", "Iconic"]},
        {"name": "Tsukiji Outer Market", "category": "Food Market", "description": "Tokyo's legendary seafood market. Try fresh sushi, tamagoyaki (rolled omelette), and seasonal seafood.", "best_time_to_visit": "Morning (7-10 AM)", "estimated_entry_cost": "Free entry", "tags": ["Food", "Seafood", "Market"]},
    ],
    "jaipur": [
        {"name": "Amber Fort (Amer Fort)", "category": "Royal Fortress", "description": "Magnificent hilltop fort with intricate mirror work, elephant rides, and sweeping Aravalli views.", "best_time_to_visit": "Morning (8-11 AM)", "estimated_entry_cost": "₹500 (~$6)", "tags": ["Fort", "History", "Architecture"]},
        {"name": "Hawa Mahal (Palace of Winds)", "category": "Iconic Architecture", "description": "Pink sandstone honeycomb facade with 953 tiny windows. Best photographed from the street-side cafe opposite.", "best_time_to_visit": "Morning (for lighting)", "estimated_entry_cost": "₹200 (~$2.50)", "tags": ["Iconic", "Photography", "Architecture"]},
        {"name": "Johari Bazaar & Bapu Bazaar", "category": "Traditional Market", "description": "Bustling lanes selling gemstones, lac bangles, block-printed textiles, and Rajasthani mojari sandals.", "best_time_to_visit": "Late Afternoon / Evening", "estimated_entry_cost": "Free", "tags": ["Shopping", "Culture", "Handicrafts"]},
    ],
    "goa": [
        {"name": "Calangute & Baga Beach", "category": "Beach & Nightlife", "description": "Goa's most popular beach strip with shacks, water sports, and legendary Saturday Night Market nearby.", "best_time_to_visit": "Sunset", "estimated_entry_cost": "Free", "tags": ["Beach", "Nightlife", "Water Sports"]},
        {"name": "Old Goa Churches (Basilica of Bom Jesus)", "category": "UNESCO Heritage", "description": "16th-century Portuguese churches housing the relics of St. Francis Xavier. UNESCO World Heritage Site.", "best_time_to_visit": "Morning", "estimated_entry_cost": "Free", "tags": ["Heritage", "Architecture", "History"]},
        {"name": "Dudhsagar Falls", "category": "Nature & Adventure", "description": "Spectacular 310m four-tiered waterfall on the Goa-Karnataka border. Accessed by jeep safari through jungle.", "best_time_to_visit": "Monsoon Season (Jun-Sep)", "estimated_entry_cost": "₹400 + Jeep ₹2500 shared", "tags": ["Waterfall", "Adventure", "Nature"]},
    ],
}

DESTINATION_FOOD = {
    "los angeles": [
        {"name": "Grand Central Market", "type": "Food Hall", "description": "Downtown LA's legendary food hall since 1917 — tacos from Tacos Tumbras a Tomas, egg sandwiches from Eggslut, Thai from Sticky Rice.", "highlight_dish_or_experience": "Fairfax-style pastrami sandwich & handmade pupusas", "price_level": "$$"},
        {"name": "Howlin' Ray's Hot Chicken", "type": "Iconic Eatery", "description": "Nashville-style hot chicken that's become an LA institution. Expect a queue — it's worth every minute.", "highlight_dish_or_experience": "The 'Howlin' spice-level fried chicken sandwich", "price_level": "$$"},
        {"name": "Bestia (Arts District)", "type": "Fine Dining", "description": "Industrial-chic Italian powerhouse in the Arts District. Handmade pastas and wood-fired dishes.", "highlight_dish_or_experience": "Spaghetti Rustichella & bone marrow", "price_level": "$$$$"},
    ],
    "kyoto": [
        {"name": "Nishiki Market Food Walk", "type": "Street Food", "description": "Kyoto's 400-year-old kitchen — sample fresh yuba (tofu skin), matcha dango, pickled vegetables, and grilled mochi.", "highlight_dish_or_experience": "Fresh yuba (tofu skin) & matcha warabi mochi", "price_level": "$"},
        {"name": "Menbakaichidai (Fire Ramen)", "type": "Iconic Ramen", "description": "The chef dramatically sets your ramen on fire tableside with green onion oil. A viral Kyoto experience.", "highlight_dish_or_experience": "Fire Ramen (negi soba) — the flaming spectacle", "price_level": "$$"},
        {"name": "Gion Karyo (祇園花郎)", "type": "Traditional Kaiseki", "description": "Multi-course seasonal kaiseki dinner in Gion's geisha district. Elegant presentation of Kyoto's culinary heritage.", "highlight_dish_or_experience": "7-course kaiseki with seasonal ingredients", "price_level": "$$$$"},
    ],
    "paris": [
        {"name": "L'As du Fallafel (Le Marais)", "type": "Street Food Legend", "description": "The best falafel in Paris (and possibly Europe). Crispy exterior, fluffy interior, dripping with tahini and hot sauce.", "highlight_dish_or_experience": "Falafel special with all toppings — eat standing", "price_level": "$"},
        {"name": "Café de Flore (Saint-Germain)", "type": "Historic Café", "description": "Legendary literary café where Sartre and de Beauvoir wrote. Classic French café crème and croque-monsieur.", "highlight_dish_or_experience": "Café crème & croque-monsieur on the terrace", "price_level": "$$$"},
    ],
    "tokyo": [
        {"name": "Ichiran Ramen (Shibuya)", "type": "Solo Ramen", "description": "Customizable tonkotsu ramen in individual booths. Choose noodle firmness, broth richness, and spice level on a form.", "highlight_dish_or_experience": "Original Tonkotsu with extra chashu & nitamago egg", "price_level": "$$"},
        {"name": "Tsukiji Outer Market Sushi", "type": "Fresh Sushi", "description": "Ultra-fresh sushi at dawn from the legendary market. Try omakase at one of the tiny counter-only shops.", "highlight_dish_or_experience": "Omakase (chef's choice) — otoro, uni, ikura", "price_level": "$$$"},
    ],
    "jaipur": [
        {"name": "Lassiwala (MI Road)", "type": "Iconic Drink Shop", "description": "Since 1944, this tiny roadside stall serves Jaipur's famous thick, creamy lassi in clay kulhad cups.", "highlight_dish_or_experience": "Fresh mango lassi in kulhad — arrive before noon", "price_level": "$"},
        {"name": "Rawat Mishthan Bhandar", "type": "Sweets & Snacks", "description": "Legendary pyaaz kachori (onion stuffed pastry) served with tangy chutney. Always bustling.", "highlight_dish_or_experience": "Pyaaz Kachori & Mawa Kachori for breakfast", "price_level": "$"},
    ],
    "goa": [
        {"name": "Vinayak Family Restaurant (Assagao)", "type": "Local Goan", "description": "Authentic family-run Goan eatery serving prawn curry rice, pork vindaloo, and fresh kingfish recheado.", "highlight_dish_or_experience": "Goan fish thali with sol kadhi & prawn balchão", "price_level": "$"},
        {"name": "Gunpowder (Assagao)", "type": "South Indian Fusion", "description": "Eclectic South Indian dishes in a charming Portuguese villa setting with fairy lights.", "highlight_dish_or_experience": "Appam with stew & Malabar prawn curry", "price_level": "$$"},
    ],
}

# ─── Destination-specific itinerary details ─────────────────────────────────
DESTINATION_ITINERARIES = {
    "los angeles": [
        {"theme": "Hollywood, Griffith & Downtown Discovery", "morning": ("Hollywood Boulevard & Walk of Fame", "Walk the star-studded boulevard, photograph the TCL Chinese Theatre, and catch views of the Hollywood Sign from Hollywood & Highland."), "afternoon": ("Griffith Observatory & Hike", "Hike to Griffith Observatory for panoramic LA views. Free planetarium shows. The sunset from here is legendary."), "evening": ("Downtown LA & Grand Central Market", "Explore DTLA's arts district, grab dinner at Grand Central Market, and stroll the illuminated Walt Disney Concert Hall.")},
        {"theme": "Santa Monica, Venice Beach & Coastal Vibes", "morning": ("Santa Monica Pier & Third Street Promenade", "Ride the iconic Ferris wheel, walk the pier, then browse Third Street Promenade's boutiques and street performers."), "afternoon": ("Venice Beach & Abbot Kinney Blvd", "Soak in Venice Beach's boardwalk culture — street art, Muscle Beach, skate park. Then stroll Abbot Kinney for cafes and design shops."), "evening": ("Sunset at Malibu Beach", "Drive PCH north to Malibu for golden hour at El Matador Beach. Dinner at a seafood shack overlooking the Pacific.")},
        {"theme": "Museums, Art & Culture Day", "morning": ("The Getty Center", "World-class art museum with free admission. Stunning hilltop architecture and manicured gardens with city views."), "afternoon": ("LACMA & La Brea Tar Pits", "See Chris Burden's iconic 'Urban Light' installation. Explore Ice Age fossils at the adjacent La Brea Tar Pits."), "evening": ("Koreatown BBQ & Nightlife", "Feast on Korean BBQ at Park's BBQ or Kang Ho-dong Baekjeong. Finish with karaoke or a rooftop bar.")},
        {"theme": "Theme Parks & Family Fun", "morning": ("Universal Studios Hollywood", "Movie-magic theme park — Wizarding World of Harry Potter, Studio Tour, and Jurassic World ride. Arrive at opening."), "afternoon": ("CityWalk & Lunch", "Universal CityWalk for dining and shopping. Try Voodoo Doughnut or Buca di Beppo."), "evening": ("Burbank & Studio Views", "Drive through Burbank — spot major studio lots (Warner Bros, Disney). Evening dinner in Toluca Lake.")},
        {"theme": "Day Trip: Pacific Coast Highway & Beaches", "morning": ("PCH Drive to Huntington Beach", "Cruise down the Pacific Coast Highway — windows down, ocean views. Stop at Huntington Beach (Surf City USA)."), "afternoon": ("Laguna Beach Art Walk", "Charming coastal art colony with galleries, tide pools, and crystal-clear coves. Grab fish tacos at a beachside shack."), "evening": ("Sunset from Dana Point Harbor", "Watch sailboats return to harbor at golden hour. Seafood dinner with Pacific panorama.")},
        {"theme": "Departure Day & Final Stops", "morning": ("Runyon Canyon Morning Hike", "Popular 3.5-mile trail above Hollywood with sweeping city-to-ocean views. The Instagram-famous LA hike."), "afternoon": ("Last-Minute Shopping & The Grove", "Browse The Grove & Original Farmers Market (since 1934) for souvenirs, gourmet treats, and artisan goods."), "evening": ("Farewell Dinner at Sunset Strip", "Final dinner on the Sunset Strip. Toast to the trip at a rooftop restaurant with city lights twinkling below.")}
    ],
    "kyoto": [
        {"theme": "Iconic Shrines & Eastern Hills", "morning": ("Fushimi Inari Shrine (千本鳥居)", "Arrive early (6-7 AM) to walk through thousands of vermillion torii gates with minimal crowds. The full hike takes 2 hours."), "afternoon": ("Kiyomizu-dera Temple & Higashiyama", "Iconic wooden stage with forest views. Walk the charming Ninenzaka and Sannenzaka cobblestone lanes lined with shops."), "evening": ("Gion Geisha District Evening Walk", "Stroll the lantern-lit streets of Gion hoping to spot a maiko (apprentice geisha). Dinner at a traditional izakaya.")},
        {"theme": "Bamboo Groves & Western Kyoto", "morning": ("Arashiyama Bamboo Grove & Tenryu-ji Temple", "Walk through the ethereal bamboo forest. Visit Tenryu-ji's stunning Zen garden (UNESCO site)."), "afternoon": ("Iwatayama Monkey Park & Togetsukyo Bridge", "Climb to the monkey park for panoramic views and friendly macaques. Cross the famous wooden bridge."), "evening": ("Traditional Kaiseki Dinner", "Experience a multi-course kaiseki dinner — seasonal Kyoto ingredients artfully presented in a traditional tatami room.")},
        {"theme": "Golden Temples & Zen Gardens", "morning": ("Kinkaku-ji (Golden Pavilion)", "Gold-leaf Zen temple reflecting in its mirror pond. One of Japan's most photographed sights. Arrive at 9 AM opening."), "afternoon": ("Ryoan-ji Rock Garden & Ninna-ji", "Contemplate the 15-stone Zen rock garden — a masterpiece of minimalism. Nearby Ninna-ji has beautiful pagoda grounds."), "evening": ("Nishiki Market & Pontocho Alley", "Browse Kyoto's Kitchen for street snacks, then dine along the atmospheric Pontocho narrow alley above the Kamo River.")},
        {"theme": "Tea Culture, Matcha & Artisan Day", "morning": ("Uji — Matcha Capital of Japan", "Day-trip to nearby Uji: visit Byodo-in Temple (the ¥10 coin image) and taste the world's finest matcha at Nakamura Tokichi."), "afternoon": ("Tea Ceremony Experience", "Participate in an authentic chado tea ceremony. Learn the ritual of whisking, serving, and appreciating matcha."), "evening": ("Kyoto Station & Ramen Street", "End at Kyoto Station's underground Ramen Street — pick from 8+ regional ramen styles under one roof.")},
    ],
    "tokyo": [
        {"theme": "Asakusa, Temples & Traditional Tokyo", "morning": ("Senso-ji Temple & Nakamise Street", "Tokyo's oldest temple. Walk through the iconic Kaminarimon gate, browse Nakamise for traditional snacks and souvenirs."), "afternoon": ("Ueno Park & National Museum", "Vast park with Tokyo National Museum, Ameya-Yokocho market, and seasonal cherry blossoms / autumn foliage."), "evening": ("Akihabara Electric Town", "Neon-lit tech and anime district. Browse retro game shops, maid cafes, and multi-floor electronics stores.")},
        {"theme": "Shibuya, Harajuku & Youth Culture", "morning": ("Meiji Shrine & Yoyogi Park", "Serene forest shrine dedicated to Emperor Meiji. Enter through massive torii gates, then picnic in Yoyogi Park."), "afternoon": ("Harajuku — Takeshita Street & Omotesando", "Teen fashion capital (Takeshita) meets luxury boulevard (Omotesando). Grab a rainbow cotton candy or soufflé pancake."), "evening": ("Shibuya Crossing & Shibuya Sky", "Experience the world's busiest crossing. Ride to Shibuya Sky's rooftop for 360° night views of illuminated Tokyo.")},
    ],
}


def _find_route_key(origin: str, destination: str):
    """Try to match input city strings to known route keys."""
    orig = origin.lower().strip()
    dest = destination.lower().strip()
    for (k1, k2), data in KNOWN_ROUTES.items():
        if k1 in orig and k2 in dest:
            return data
    return None


def _find_hub_coord(city: str):
    """Find coordinate for a city string."""
    c = city.lower().strip()
    for name, coords in HUB_COORDINATES.items():
        if name in c:
            return coords
    return None


def _estimate_distance_km(origin: str, destination: str) -> dict:
    """Returns realistic distance estimates using known routes or Haversine fallback."""
    known = _find_route_key(origin, destination)
    if known:
        return known

    coord1 = _find_hub_coord(origin)
    coord2 = _find_hub_coord(destination)
    if coord1 and coord2:
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        r = 6371
        air_dist = round(r * c, 1)
        road_dist = round(air_dist * 1.3, 1)  # Road winding factor
        rail_dist = round(air_dist * 1.2, 1)
        return {"road": max(30, road_dist), "air": max(25, air_dist), "rail": max(28, rail_dist)}

    seed = abs(hash(f"{origin.lower()}->{destination.lower()}")) % 600 + 150
    return {"road": float(seed), "air": round(seed * 0.78), "rail": round(seed * 0.95)}


def _get_dest_key(destination: str) -> str:
    """Normalize destination to match our database keys."""
    d = destination.lower().strip()
    for key in DESTINATION_ATTRACTIONS.keys():
        if key in d or d in key:
            return key
    # Try partial match
    for key in DESTINATION_ATTRACTIONS.keys():
        if key.split()[0] in d or d.split(",")[0].strip().lower() == key:
            return key
    return ""


@tool
def search_travel_info(query: str) -> str:
    """
    Search the web in real-time via Tavily for current travel information,
    attractions, local dining, events, route conditions, or travel advisories.
    Use this tool to find up-to-date and specific destination details.
    """
    tavily_key = os.environ.get("TAVILY_API_KEY", "").strip()

    if not tavily_key or tavily_key == "your_tavily_api_key_here":
        return json.dumps({
            "status": "simulated_info",
            "note": "TAVILY_API_KEY not configured. Using curated travel knowledge base.",
            "results": [
                {
                    "title": f"Travel guide: {query}",
                    "content": f"Popular destinations matching '{query}' feature must-see landmarks, diverse culinary scenes, vibrant local culture, and scenic viewpoints. Check seasonal timings and book popular experiences in advance.",
                    "url": "https://travel-guide.example.com"
                }
            ]
        })

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=tavily_key)
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=5,
            include_answer=True
        )

        extracted = []
        if response.get("answer"):
            extracted.append({"answer": response["answer"]})

        for r in response.get("results", []):
            extracted.append({
                "title": r.get("title", ""),
                "content": r.get("content", "")[:400],
                "url": r.get("url", "")
            })

        return json.dumps({"status": "live_tavily_search", "results": extracted})
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Tavily search failed: {str(e)}",
            "fallback": f"General travel recommendations for: {query}"
        })


@tool
def calculate_route_details(origin: str, destination: str, travel_mode: str) -> str:
    """
    Calculate estimated route distance, travel duration by travel mode (car, bike, bus, train, flight),
    and provide realistic intermediate scenic stops along the journey.
    Clearly marks calculations as algorithmic estimates.
    """
    mode = travel_mode.lower().strip()
    distances = _estimate_distance_km(origin, destination)

    # Speed profiles (km/h) — realistic average highway/rail/air speeds
    speed_profiles = {
        "car": {"speed": 90, "overhead_hours": 0.5, "desc": "Highway driving with brief rest stops"},
        "bike": {"speed": 20, "overhead_hours": 1.0, "desc": "Bicycle touring with regular rest stops"},
        "bus": {"speed": 60, "overhead_hours": 0.75, "desc": "Intercity bus transit with scheduled stops"},
        "train": {"speed": 130, "overhead_hours": 0.25, "desc": "Express / high-speed rail"},
        "flight": {"speed": 800, "overhead_hours": 2.5, "desc": "Flight including airport check-in & boarding"}
    }

    # Special train speeds for known high-speed rail corridors
    fast_train_corridors = {"tokyo", "kyoto", "osaka", "london", "paris", "amsterdam", "zurich"}
    orig_lower = origin.lower()
    dest_lower = destination.lower()
    is_hsr = any(c in orig_lower for c in fast_train_corridors) and any(c in dest_lower for c in fast_train_corridors)

    profile = speed_profiles.get(mode, speed_profiles["car"])

    if mode == "flight":
        flight_dist = distances["air"]
        travel_hours = (flight_dist / profile["speed"]) + profile["overhead_hours"]
        dist_display = f"{int(flight_dist)} km (air distance)"
    elif mode == "train":
        rail_dist = distances.get("rail", distances["road"])
        train_speed = 250 if is_hsr else profile["speed"]  # Shinkansen/TGV speed
        travel_hours = (rail_dist / train_speed) + profile["overhead_hours"]
        dist_display = f"{int(rail_dist)} km (rail corridor)"
    else:
        road_dist = distances["road"]
        travel_hours = (road_dist / profile["speed"]) + profile["overhead_hours"]
        dist_display = f"{int(road_dist)} km"

    hours = int(travel_hours)
    minutes = int((travel_hours - hours) * 60)
    duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

    # Lookup real scenic stops or generate sensible ones
    route_key_fwd = None
    for (k1, k2) in ROUTE_STOPS_DB.keys():
        if k1 in orig_lower and k2 in dest_lower:
            route_key_fwd = (k1, k2)
            break

    if route_key_fwd:
        stops = ROUTE_STOPS_DB[route_key_fwd]
    else:
        road_dist = distances["road"]
        stops = []
        if road_dist > 150:
            stops.append({
                "name": f"Rest Stop & Scenic Viewpoint (midway)",
                "description": f"Recommended break point roughly halfway between {origin} and {destination}. Stretch, refuel, grab local snacks.",
                "recommended_time_spent": "30-45 mins",
                "highlights": ["Photo opportunity", "Local refreshments", "Clean rest facilities"]
            })
        if road_dist > 500:
            stops.append({
                "name": f"Regional Town Stopover",
                "description": f"A charming town along the route ideal for lunch, local market browsing, and cultural exploration.",
                "recommended_time_spent": "1-2 hours",
                "highlights": ["Local cuisine", "Town center walk", "Regional specialties"]
            })

    # Build legs
    legs = []
    locations = [origin] + [s["name"] for s in stops] + [destination]
    num_legs = len(locations) - 1
    road_dist = distances["road"]
    for i in range(num_legs):
        leg_dist = round(road_dist / num_legs)
        leg_time = max(1, hours // num_legs) if hours > 0 else 1
        legs.append({
            "from_location": locations[i],
            "to_location": locations[i + 1],
            "transport_mode": mode,
            "estimated_distance": f"{leg_dist} km",
            "estimated_duration": f"{leg_time}h",
            "scenic_rating": "Very High" if i == 0 else "High",
            "transit_tips": f"Check road conditions before departure." if mode in ["car", "bike"] else "Arrive 15 mins before departure."
        })

    for s in stops:
        s["location_type"] = "intermediate_stop"

    result = {
        "summary": f"Estimated journey from {origin} to {destination} via {mode.capitalize()}",
        "total_estimated_distance": dist_display,
        "total_estimated_duration": duration_str,
        "transport_mode": mode,
        "is_estimated": True,
        "estimation_disclaimer": (
            "Distances and travel times are estimates based on standard routes and average speeds. "
            "Actual times depend on traffic, weather, stops, and road conditions."
        ),
        "stops": stops,
        "legs": legs
    }

    return json.dumps(result)


@tool
def estimate_trip_budget(
    total_budget: float,
    travelers: int,
    duration_days: int,
    travel_mode: str,
    destination: str
) -> str:
    """
    Produce an itemized budget breakdown (transport, lodging, dining, activities, contingency)
    customized to traveler count, trip length, destination, and budget tier.
    """
    travelers = max(1, travelers)
    duration_days = max(1, duration_days)
    per_person = total_budget / travelers
    daily_per_person = per_person / duration_days

    # Determine budget tier
    if daily_per_person < 50:
        tier = "Shoestring / Ultra-Budget"
    elif daily_per_person < 100:
        tier = "Budget-Friendly Backpacker"
    elif daily_per_person < 200:
        tier = "Comfortable Mid-Range"
    elif daily_per_person < 400:
        tier = "Premium Comfort"
    else:
        tier = "Luxury / High-End"

    # Adjust percentages by travel mode
    if travel_mode.lower() in ["flight"]:
        transport_pct = 0.35
        lodging_pct = 0.28
        food_pct = 0.18
        activities_pct = 0.12
        buffer_pct = 0.07
    elif travel_mode.lower() in ["train"]:
        transport_pct = 0.25
        lodging_pct = 0.32
        food_pct = 0.22
        activities_pct = 0.14
        buffer_pct = 0.07
    elif travel_mode.lower() in ["bike"]:
        transport_pct = 0.10
        lodging_pct = 0.38
        food_pct = 0.28
        activities_pct = 0.15
        buffer_pct = 0.09
    else:  # car, bus
        transport_pct = 0.22
        lodging_pct = 0.33
        food_pct = 0.24
        activities_pct = 0.13
        buffer_pct = 0.08

    food_daily = round((total_budget * food_pct) / (duration_days * travelers), 1)

    categories = [
        {
            "category": "Accommodation & Lodging",
            "allocated_amount": round(total_budget * lodging_pct, 2),
            "percentage": round(lodging_pct * 100),
            "icon": "Hotel",
            "description": f"~${round(total_budget * lodging_pct / duration_days)}/night for {travelers} traveler{'s' if travelers > 1 else ''} across {duration_days} nights."
        },
        {
            "category": "Transportation & Fuel/Transit",
            "allocated_amount": round(total_budget * transport_pct, 2),
            "percentage": round(transport_pct * 100),
            "icon": "Car",
            "description": f"{'Fuel, tolls & parking' if travel_mode.lower() in ['car', 'bike'] else 'Tickets, fares & local transit'} for the entire trip."
        },
        {
            "category": "Food & Local Dining",
            "allocated_amount": round(total_budget * food_pct, 2),
            "percentage": round(food_pct * 100),
            "icon": "Utensils",
            "description": f"~${food_daily}/day/person covering breakfast, lunch, dinner, and snacks."
        },
        {
            "category": "Sightseeing & Experiences",
            "allocated_amount": round(total_budget * activities_pct, 2),
            "percentage": round(activities_pct * 100),
            "icon": "Ticket",
            "description": f"Entry tickets, guided tours, equipment rentals, and experience bookings."
        },
        {
            "category": "Contingency & Souvenirs",
            "allocated_amount": round(total_budget * buffer_pct, 2),
            "percentage": round(buffer_pct * 100),
            "icon": "ShieldAlert",
            "description": f"Emergency buffer, SIM/data, tips, and personal shopping."
        }
    ]

    tips = [
        f"Book accommodation with free breakfast to save ~${food_daily}/day on morning meals.",
        "Pre-book major attraction tickets online for 10-20% discounts and skip-the-line access.",
        f"For {travel_mode} travel: {'use fuel price comparison apps and pack snacks to reduce roadside spending' if travel_mode.lower() in ['car'] else 'book advance tickets for best rates'}.",
        f"Set aside {round(buffer_pct*100)}% (${round(total_budget * buffer_pct)}) as emergency buffer — don't touch it unless truly needed.",
        f"Use public transit or walk for local sightseeing in {destination} to cut daily transport costs."
    ]

    result = {
        "total_budget": total_budget,
        "per_person_budget": round(per_person, 2),
        "daily_per_person": round(daily_per_person, 2),
        "budget_tier": tier,
        "categories": categories,
        "saving_tips": tips,
        "estimation_disclaimer": "Budget allocations are estimated benchmarks based on average regional costs. Actual spending varies by season, booking timing, and personal choices."
    }

    return json.dumps(result)


@tool
def generate_day_wise_itinerary(
    destination: str,
    days: int,
    interests: List[str],
    travel_mode: str
) -> str:
    """
    Synthesizes a day-by-day structured itinerary covering Morning, Afternoon, and Evening slots,
    with real destination-specific activities tailored to traveler interests and travel mode.
    """
    days = max(1, min(days, 14))
    interests_str = ", ".join(interests) if interests else "general sightseeing, culture, food"
    dest_key = _get_dest_key(destination)

    # Get destination-specific itinerary if available
    known_days = DESTINATION_ITINERARIES.get(dest_key, [])

    # Generic themes as fallback for days beyond our database
    generic_themes = [
        ("Arrival & Iconic Landmarks", "Visit the most iconic landmark", "Explore the city center and local markets", "Evening stroll along the main promenade, dinner at a local favorite"),
        ("Cultural Deep Dive & Heritage", "Morning heritage site or museum visit", "Afternoon walking tour through historic district", "Traditional local cuisine dinner with live cultural performance"),
        ("Nature, Trails & Outdoor Adventure", f"Morning nature hike or scenic walk focused on {interests[0] if interests else 'nature'}", "Afternoon picnic at a scenic viewpoint or lakeside", "Sunset photography session, dinner at a countryside restaurant"),
        ("Local Food Trail & Markets", "Morning food market walk — taste local breakfast staples and street snacks", "Afternoon cooking class or food tour with a local guide", "Evening food crawl through the most popular dining street"),
        ("Off-the-Beaten-Path & Hidden Gems", "Morning visit to a lesser-known neighborhood or artisan workshop", f"Afternoon exploration tailored to your interests: {interests_str}", "Evening at a rooftop bar or local live music venue"),
        ("Relaxation & Shopping Day", "Sleep in, late brunch at a popular local café", "Afternoon shopping for souvenirs, local crafts, and specialties", "Farewell dinner at a top-rated restaurant"),
        ("Day Trip & Excursion", "Full-day excursion to a nearby town, national park, or coastline", "Lunch at a regional specialty restaurant en route", "Return evening, light dinner, trip reflection"),
    ]

    itinerary_days = []
    for d in range(1, days + 1):
        if d <= len(known_days):
            kd = known_days[d - 1]
            itinerary_days.append({
                "day_number": d,
                "title": f"Day {d}: {kd['theme']}",
                "theme": kd["theme"],
                "morning": {
                    "time_slot": "Morning (08:30 - 12:00)",
                    "title": kd["morning"][0],
                    "description": kd["morning"][1],
                    "location": destination,
                    "estimated_duration": "3-3.5 hours",
                    "approximate_cost": "Free - $20",
                    "is_tavily_sourced": False
                },
                "afternoon": {
                    "time_slot": "Afternoon (13:00 - 17:00)",
                    "title": kd["afternoon"][0],
                    "description": kd["afternoon"][1],
                    "location": destination,
                    "estimated_duration": "3-4 hours",
                    "approximate_cost": "$10 - $40",
                    "is_tavily_sourced": False
                },
                "evening": {
                    "time_slot": "Evening (18:00 - 21:30)",
                    "title": kd["evening"][0],
                    "description": kd["evening"][1],
                    "location": destination,
                    "estimated_duration": "2.5-3 hours",
                    "approximate_cost": "$20 - $60",
                    "is_tavily_sourced": False
                },
                "stay_recommendation": f"Well-located hotel or guesthouse in central {destination}.",
                "local_transport_tip": f"Best explored on foot and local transit today."
            })
        else:
            g = generic_themes[(d - 1) % len(generic_themes)]
            itinerary_days.append({
                "day_number": d,
                "title": f"Day {d}: {g[0]}",
                "theme": g[0],
                "morning": {
                    "time_slot": "Morning (08:30 - 12:00)",
                    "title": g[0] + " — Morning",
                    "description": g[1],
                    "location": destination,
                    "estimated_duration": "3 hours",
                    "approximate_cost": "Varies",
                    "is_tavily_sourced": False
                },
                "afternoon": {
                    "time_slot": "Afternoon (13:00 - 17:00)",
                    "title": g[0] + " — Afternoon",
                    "description": g[2],
                    "location": destination,
                    "estimated_duration": "3-4 hours",
                    "approximate_cost": "Varies",
                    "is_tavily_sourced": False
                },
                "evening": {
                    "time_slot": "Evening (18:00 - 21:30)",
                    "title": g[0] + " — Evening",
                    "description": g[3],
                    "location": destination,
                    "estimated_duration": "2.5-3 hours",
                    "approximate_cost": "Varies",
                    "is_tavily_sourced": False
                },
                "stay_recommendation": f"Comfortable accommodation in {destination}.",
                "local_transport_tip": f"Use local transit or {travel_mode} for getting around."
            })

    return json.dumps({
        "destination": destination,
        "total_days": days,
        "days": itinerary_days
    })


# Export list of agent tools
TRAVEL_AGENT_TOOLS = [
    search_travel_info,
    calculate_route_details,
    estimate_trip_budget,
    generate_day_wise_itinerary
]
