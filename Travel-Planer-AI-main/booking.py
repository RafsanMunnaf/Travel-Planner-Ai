# import requests

# # API Endpoint for searching hotels
# search_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"

# search_querystring = {
#     "query": "budapest",  # Location: Budapest
#     "filter_by_currency": "BDT",  # Currency
#     "checkin_date": "2025-10-10",  # Check-in Date
#     "checkout_date": "2025-10-15",  # Checkout Date
#     "adults_number": "2",  # Number of adults
#     "room_number": "1",  # Number of rooms
#     "order_by": "popularity",  # Sort by popularity or any other criteria
# }

# headers = {
#     "x-rapidapi-key": "0ec75bfd4bmsh619d22cc21e2e29p13405ejsn8bdaab1b2017",  # Replace with your actual key
#     "x-rapidapi-host": "booking-com15.p.rapidapi.com"
# }

# # Send GET request to the API
# response = requests.get(search_url, headers=headers, params=search_querystring)

# # Check if the request was successful
# if response.status_code == 200:
#     data = response.json()
#     hotels = data.get("data", [])

#     # Loop through each hotel and extract relevant details
#     for hotel in hotels[:5]:  # Show details for top 5 hotels
#         hotel_name = hotel.get('name', 'N/A')
#         hotel_rating = hotel.get('rating', 'N/A')
#         hotel_price = hotel.get('price', 'N/A')  # You can access more specific price info here
#         hotel_description = hotel.get('description', 'N/A')
#         hotel_link = f"https://www.booking.com/hotel/{hotel.get('hotel_id')}.html"
        
#         # If you have a discounted price, you can extract that as well
#         hotel_discounted_price = hotel.get('discounted_price', 'N/A')
#         hotel_discount_percentage = hotel.get('discount_percentage', 'N/A')

#         print(f"🏨 Hotel Name: {hotel_name}")
#         print(f"⭐ Rating: {hotel_rating}")
#         print(f"💰 Price: {hotel_price}")
#         print(f"💸 Discounted Price: {hotel_discounted_price} (Discount: {hotel_discount_percentage}%)")
#         print(f"📜 Description: {hotel_description}")
#         print(f"🔗 Link: {hotel_link}")
#         print("-" * 50)

# else:
#     print(f"Failed to fetch hotels. Status code: {response.status_code}")
#     print(response.text)



import requests

# Common Headers for the API
headers = {
    "x-rapidapi-key": "0ec75bfd4bmsh619d22cc21e2e29p13405ejsn8bdaab1b2017",  # Replace with your actual RapidAPI key
    "x-rapidapi-host": "booking-com.p.rapidapi.com"
}

# Function to fetch data from any endpoint with error handling
def fetch_data(endpoint, params=None):
    response = requests.get(endpoint, headers=headers, params=params)
    print(f"Request URL: {response.url}")  # Debugging: print the request URL
    print(f"Status Code: {response.status_code}")  # Debugging: print the status code
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        print(f"Error Response: {response.text}")  # Print error response content
        return None

# Example API calls for different endpoints

# Fetch nearby cities for a hotel (Example endpoint)
def fetch_nearby_cities():
    url = "https://booking-com.p.rapidapi.com/v1/hotels/nearby-cities"
    querystring = {"latitude":"65.9667","longitude":"-18.5333","locale":"en-gb"}
    return fetch_data(url, querystring)

# Fetch reviews filter metadata for a hotel (Example endpoint)
def fetch_reviews_filter_metadata(hotel_id):
    url = "https://booking-com.p.rapidapi.com/v1/hotels/reviews-filter-metadata"
    querystring = {"hotel_id": hotel_id, "locale": "en-gb"}
    return fetch_data(url, querystring)

# Main function to fetch hotel details
def fetch_hotel_details(hotel_id):
    hotel_details = {}

    # Example fetching different endpoints for the hotel
    hotel_details["nearby_cities"] = fetch_nearby_cities()
    hotel_details["reviews_filter_metadata"] = fetch_reviews_filter_metadata(hotel_id)
    # Add other functions like fetch_review_scores, fetch_room_list, etc.

    return hotel_details

# Example to fetch hotel data for a specific hotel_id
hotel_id = 1676161  # Example hotel ID
hotel_details = fetch_hotel_details(hotel_id)

# Print the fetched details
if hotel_details:
    for key, value in hotel_details.items():
        print(f"{key}: {value}")
else:
    print("Failed to fetch hotel details.")










# import requests

# url = "https://booking-com.p.rapidapi.com/v1/hotels/search"

# querystring = {
#     "children_ages": "5,0",
#     "filter_by_currency": "AED",
#     "checkout_date": "2025-10-14",
#     "checkin_date": "2025-10-13",
#     "page_number": "0",
#     "adults_number": "2",
#     "units": "metric",
#     "dest_id": "-553173",
#     "locale": "en-gb",
#     "categories_filter_ids": "class::2,class::4,free_cancellation::1",
#     "dest_type": "city",
#     "include_adjacency": "true",
#     "order_by": "popularity",
#     "children_number": "2",
#     "room_number": "1"
# }

# headers = {
#     "x-rapidapi-key": "0ec75bfd4bmsh619d22cc21e2e29p13405ejsn8bdaab1b2017",  # Replace with your actual RapidAPI key
#     "x-rapidapi-host": "booking-com.p.rapidapi.com"
# }

# response = requests.get(url, headers=headers, params=querystring)

# # Assuming response is in JSON format
# data = response.json()

# # Extract hotel data
# if 'result' in data:  # If the result key exists in the response
#     hotels = data['result']
#     for hotel in hotels:
#         hotel_name = hotel.get('hotel_name', 'N/A')
#         price = hotel.get('price', {}).get('currency', 'N/A') + " " + str(hotel.get('price', {}).get('value', 'N/A'))
#         review_score = hotel.get('review_score', 'N/A')
#         hotel_url = hotel.get('url', 'N/A')
#         address = hotel.get('address', 'N/A')
#         hotel_class = hotel.get('class', 'N/A')
        
#         # Main image URL
#         main_photo_url = hotel.get('main_photo_url', 'N/A')

#         # Print hotel details
#         print(f"Hotel Name: {hotel_name}")
#         print(f"Price: {price}")
#         print(f"Review Score: {review_score}")
#         print(f"Hotel URL: {hotel_url}")
#         print(f"Address: {address}")
#         print(f"Hotel Class: {hotel_class}")
#         print(f"Main Photo: {main_photo_url}")
#         print("-" * 50)
# else:
#     print("No hotels found or incorrect response.")

