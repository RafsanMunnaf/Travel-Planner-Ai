import openai
from rich.console import Console
from rich.markdown import Markdown
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from dateutil import parser

load_dotenv()

# Set your OpenAI API key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

console = Console()

def call_openai_chat(travel_data, hotels_data, language: str = None):
    # Extract data from the travel_info dictionary
    travel_info = travel_data["travel_info"]
    destination = travel_info["to"]
    origin = travel_info["from"]
    group_size = travel_info["traveling_with"]
    trip_duration = travel_info["duration"]
    travel_dates = travel_info["when"]
    transportation = travel_info["transportation"]
    purpose = travel_info["purpose"]
    description = travel_info["descriptions of the trip"]
    
    # Parse key insights from the description to enhance personalization
    has_elderly = "parents" in group_size.lower() or "elderly" in description.lower()
    is_family = "family" in description.lower() or "parents" in group_size.lower()
    wants_cultural = "cultural" in description.lower() or "culture" in description.lower()
    wants_cuisine = "culinary" in description.lower() or "cuisine" in description.lower()
    wants_relaxation = "relaxation" in description.lower() or "relax" in description.lower()
    wants_beaches = "beaches" in description.lower() or "beach" in description.lower()
    wants_adventure = "adventure" in description.lower()
    
 #Language Update#
 ############################################################

    language = language.lower()
    supported_languages = {"english", "chinese"}
    if language not in supported_languages:
        language = "english"

    if language == "chinese":
        language_instruction = "Please use ONLY in Traditional Chinese for creating  this entire travel plan."
    else:
        language_instruction = "Please use ONLY in English for creating this entire travel plan."

##############################################################
    # Dynamically parse and format travel_dates
    try:
        dt = parser.parse(travel_dates, fuzzy=True, default=datetime.now())
        formatted_date = dt.strftime("%B %Y")
    except Exception:
        formatted_date = travel_dates 
    
    # Create a dynamic traveler profile based on the description
    traveler_profile = ""
    if is_family:
        traveler_profile += "a family group "
    if has_elderly:
        traveler_profile += "that includes elderly members requiring appropriate pacing and accessibility considerations "
    
    # Create dynamic activity preferences based on the description
    activity_preferences = []
    if wants_cultural:
        activity_preferences.append("cultural immersion and local traditions")
    if wants_cuisine:
        activity_preferences.append("local culinary experiences")
    if wants_relaxation:
        activity_preferences.append("relaxation opportunities")
    if wants_beaches:
        activity_preferences.append("beach activities")
    if wants_adventure:
        activity_preferences.append("adventure experiences")
    
    # If no specific preferences detected, use a general approach
    if not activity_preferences:
        activity_preferences = ["a diverse mix of activities including sightseeing, local experiences, and leisure time"]
    
    activity_string = ", ".join(activity_preferences[:-1])
    if len(activity_preferences) > 1:
        activity_string += f", and {activity_preferences[-1]}"
    else:
        activity_string = activity_preferences[0]
    
    # Filter hotels suitable for the destination and group
    suitable_hotels = []
    if hotels_data and "hotels" in hotels_data:
        for hotel in hotels_data["hotels"]:
            # Check if hotel is suitable based on tags and group needs
            is_suitable = True
            if has_elderly and "Facilities for disabled guests" not in hotel["tags"]:
                is_suitable = False
            if is_family and "Family rooms" not in hotel["tags"]:
                is_suitable = False
            if is_suitable:
                suitable_hotels.append({
                    "name": hotel["hotel_name"],
                    "url": hotel["hotel_url"],
                    "image": hotel["hotel_image"],
                    "price": hotel["offer_price"],
                    "tags": hotel["tags"]
                })
    
    # If no suitable hotels found, provide a fallback message
    if not suitable_hotels:
        hotel_info = "No specific hotel recommendations are available for this destination. Please choose accommodations that suit your group's needs, such as accessibility or family-friendly options."
    else:
        hotel_info = json.dumps(suitable_hotels, indent=2)
    
    # Create a dynamic system prompt based on the travel data and hotel data
    base_prompt = f"""
        You are a professional AI travel planner, inspired by Layla.ai, tasked with creating a personalized {trip_duration} travel itinerary. Your goal is to craft an engaging, narrative-style itinerary written as if by a seasoned travel editor for an online itinerary generator. The itinerary should feel immersive, practical, and tailored to the travelers' preferences, with descriptions and real-world logistics.

        Create a travel plan for travelers from {origin} to {destination} for {trip_duration}, starting {formatted_date}, for {group_size}, with the purpose to "{purpose}".

        The following description provides key information about the trip:
        "{description}"

        Based on this information, this is {traveler_profile if traveler_profile else "a group of travelers "} looking for {activity_string}. They plan to use {transportation} as their primary mode of transportation during the trip.

        **Hotel Data**:
        Below is a list of available hotels for the trip. Use this data to recommend specific accommodations, including the hotel name, URL, image link, price, and relevant features (e.g., accessibility, family-friendly). Ensure the selected hotels align with the group's needs (e.g., accessibility for elderly, family rooms for families). If no suitable hotels are available, suggest checking reputable booking platforms for accommodations that meet the group's needs.

        {hotel_info}

        **Guidelines**:
        - Use real locations, realistic logistics, and vivid descriptions to create an immersive and practical travel experience.
        - For each key location in the itinerary, recommend one hotel accommodation that best fits the group and trip purpose.
        - Under each location section, include an "Accommodations" subsection with organized hotel details:
          - Hotel name
          - URL
          - Image link
          - Price
          - Features (tags)
        - In the itinerary section, provide detailed, engaging day-by-day activities descriptions **without mentioning any prices**.
        - Ensure the pace and activities are appropriate for the traveler profile (e.g., slower pace for elderly, engaging activities for families).
        - Recommend real restaurants with local specialties and estimated price ranges.
        - Provide practical travel tips specific to {destination} for travelers from {origin}.
        - Consider seasonal factors for {formatted_date} in {destination} (e.g., cherry blossom season in Kyoto in April).
        - Include realistic travel times and logistics using {transportation}.
        - Write in a detailed, well structured narrative style that captures the experience of each day, similar to Layla.ai's engaging and user-focused tone.
        - For splurge experiences (if mentioned in the description), recommend one or two high-end activities or dining options.
        - Ensure the total estimated cost includes transportation, accommodations (using provided hotel prices), activities, and dining.

        **Response Structure**:

        ### [Dynamic Title Based on User Input]
        **Total Estimated Cost**: [Rough total for transport, accommodations, activities, and dining] (Give a short brackdown) 
        **Travel Dates**: [{formatted_date}]  
        **Group Size**: [{group_size}]  
        **Destinations**: [List key locations in {destination}]

        ---

        ### 📍 [Location Name], {destination} (Days X–Y)

        A 2–3 sentence overview of the destination's unique appeal and why it's suitable for this specific group.

        #### 🏨 Accommodations
        - **Hotel Name**: [Hotel name]
        - **URL**: [Hotel URL]
        - **Image**: [Hotel image link]
        - **Price**: [Hotel price]
        - **Features**: [Relevant hotel features]

        ---

        #### 📅 Itinerary

        **Day X: [Descriptive Day Title] – [Date]**

        Narrative description of the day's activities, accommodations, dining, and travel tips.  (give a well descriptive and extended personalized detailed plan for each days activity description)
        **Travel Time**: [Transportation details]

        (Repeat for each day with logical flow through locations and activities.)

        **Output Format**:
         Return the response as a valid JSON object following the structure below.

        

        ```json
        {{
            "trip_overview": {{
                "title": "[Dynamic Title]",
                "total_estimated_cost": "[Cost]",
                "travel_dates": "[Dates]",
                "group_size": "[Size]",
                "destinations": ["[Destination]"]
            }},
            "locations": [
                {{
                    "location": "[Location Name]",
                    "overview": "[Overview Description]"
                    "accommodations":[ 
                        {{
                            "hotel_name": "[Hotel Name]",
                            "full_hotel_name": "[Full Hotel Name]",
                            "url": "[Hotel URL]",
                            "image": "[Image URL]",
                            "price": "[Price]",
                            "features": "[Features]"
                        }},
                        ]
                    "itinerary": [
                        {{
                            "day": "[Day Number]",
                            "title": "[Day Title]",
                            "date": "[Date]",
                            "description": "[Description]",
                            "travel_time": "[Travel Time]"
                        }}
                }}
            "additional_info": [
                {{
                    "tips":"[description]"
                }}            
            ]
        }}


    """
#New system_prompt#
##################

    system_prompt =  language_instruction + "\n\n" + base_prompt

    


    # Create a user input message that summarizes the travel request
    user_input = f"""Please create a {trip_duration} itinerary for {group_size} traveling from {origin} to {destination} starting {travel_dates}. 

    The travelers have described their trip as follows:
    "{description}"
    
    They want to {purpose} and will primarily use {transportation} for getting around. Please create a personalized travel plan that meets their specific needs and interests, incorporating the provided hotel data for accommodation recommendations."""

    try:
        response = openai.ChatCompletion.create(
            model = "gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_input.strip()}
            ],
            temperature=0.7,
            max_tokens=4000  # Increased to accommodate detailed itinerary
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        console.print(f"[red]Error calling OpenAI API: {str(e)}[/red]")
        return None

if __name__ == "__main__":
    # Sample travel data
    travel_data = {
        "travel_info": {
            "from": "New York, USA",
            "to": "India",
            "traveling_with": "2 people (couple)",
            "when": "April 2025",
            "duration": "10 days",
            "purpose": "experience traditional indian culture",
            "transportation": "public transport and walking",
            "descriptions of the trip": "This is a dream honeymoon trip to India for a young couple interested in traditional indian culture, temples, gardens, and authentic cuisine. They want a mix of guided tours and independent exploration. They're physically active and enjoy walking, but also want some relaxation time. Budget is mid-range with one or two splurge experiences."
        },
        "status": "complete",
        "missing_info": [],
        "confirmed": True
    }

    # Sample hotel data (provided in the query)
    hotels_data = {
        "hotels": [
            {
                "hotel_name": "FabHotel Prime Kzar Corporate - Nr Sealdah Station",
                "hotel_url": "https://www.booking.com/hotel/in/collection-o-76383-kzar-corporate.html",
                "hotel_image": "https://cf.bstatic.com/xdata/images/hotel/max500/413258478.jpg?k=21e03396904bb72a00bca705af1c6613fdf7b03ca97c8c7b431fc1545b9513e2&o=",
                "offer_price": "US$104",
                "tags": "Non-smoking rooms, CCTV in common areas, Restaurant, Garden, Fire extinguishers, CCTV outside property, 24-hour front desk, Lift"
            },
            {
                "hotel_name": "Treebo Royal Orbit",
                "hotel_url": "https://www.booking.com/hotel/in/treebo-trend-royal-orbit-kolkata.html",
                "hotel_image": "https://cf.bstatic.com/xdata/images/hotel/max500/508641446.jpg?k=caaa749a516bd1d3a0ffaee0ee68b33dc98757547992733563fe371f3509a911&o=",
                "offer_price": "US$106",
                "tags": "Free WiFi, Non-smoking rooms, Room service, WiFi available in all areas, Family rooms"
            },
            {
                "hotel_name": "Pikchik's nest",
                "hotel_url": "https://www.booking.com/hotel/in/pikchiks-nest.html",
                "hotel_image": "https://cf.bstatic.com/xdata/images/hotel/max500/652890011.jpg?k=b93ab5e9bdbcb0a572d385f577ea0037b5b61d4cd122f9fe804250aac939111c&o=",
                "offer_price": "US$316",
                "tags": "Non-smoking throughout, Air conditioning, Swimming pool, Free parking, Private parking, Swimming Pool"
            },
            {
                "hotel_name": "Novotel Kolkata Hotel and Residences",
                "hotel_url": "https://www.booking.com/hotel/in/novotel-kolkata.html",
                "hotel_image": "https://cf.bstatic.com/xdata/images/hotel/max500/680587633.jpg?k=b18e8e5ddc85bdf72ca99b7843f8f4d5616925a42cf61645ce32345e61a343fb&o=",
                "offer_price": "US$318",
                "tags": "1 swimming pool, Free WiFi, Non-smoking rooms, Fitness centre, Room service, Airport shuttle, Restaurant, Private parking, Facilities for disabled guests, WiFi available in all areas, Free parking, Spa and wellness centre, Family rooms, Pets allowed"
            },
            {
                "hotel_name": "Hyatt Regency Kolkata",
                "hotel_url": "https://www.booking.com/hotel/in/hyatt-regency.html",
                "hotel_image": "https://cf.bstatic.com/xdata/images/hotel/max500/582239935.jpg?k=b76c8c5ceb1118062d45a6084413bc874c2065eb2bab3720d4d8b6148355e01b&o=",
                "offer_price": "US$1,993",
                "tags": "1 swimming pool, Free WiFi, Non-smoking rooms, Fitness centre, Room service, Airport shuttle, Restaurant, Facilities for disabled guests, WiFi available in all areas, Private parking, Free parking, Spa and wellness centre, Family rooms, Pets allowed"
            }
        ]
    }

    language = "chinese"

    itinerary = call_openai_chat(travel_data, hotels_data, language)
    if itinerary:
        console.print(Markdown(itinerary))