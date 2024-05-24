import requests
from datetime import datetime, timedelta

# Google Maps API Key
google_maps_api_key = "AIzaSyCC3YfyfxWnejuFxTjN2smhzMoFftz3-YI"

# OpenWeatherMap API Key
openweathermap_api_key = "381af21f0b8fa0449d4fe4d6b49ae5ed"


# Function to fetch weather data
def get_weather_data(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        weather_data = {
            "temperature": data["main"]["temp"],
            "weather_conditions": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "humidity": data["main"]["humidity"],
            "visibility": data.get("visibility", "N/A"),
            "sunrise": datetime.utcfromtimestamp(data["sys"]["sunrise"]).strftime('%Y-%m-%d %H:%M:%S'),
            "sunset": datetime.utcfromtimestamp(data["sys"]["sunset"]).strftime('%Y-%m-%d %H:%M:%S')
        }
        return weather_data
    else:
        print(f"Error: Unable to fetch weather data for {city}")
        return None


# Function to fetch real-time traffic data
def get_traffic_data(origin, destination, api_key):
    base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
    params = {
        'origins': origin,
        'destinations': destination,
        'key': api_key,
        'traffic_model': 'best_guess',
        'departure_time': 'now'
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        try:
            traffic_info = {
                'origin': origin,
                'destination': destination,
                'distance': data['rows'][0]['elements'][0]['distance']['text'],
                'duration': data['rows'][0]['elements'][0]['duration']['text'],
                'duration_in_traffic': data['rows'][0]['elements'][0].get('duration_in_traffic', 'N/A'),
                'congestion_level': data['rows'][0]['elements'][0].get('congestion_level', 'N/A')
            }
            return traffic_info
        except KeyError:
            print("Error: Invalid address or no route found.")
            return None
    else:
        print("Error:", response.status_code)
        return None


# Function to fetch alternative routes
def get_alternative_routes(origin, destination):
    base_url = 'https://maps.googleapis.com/maps/api/directions/json?'

    params = {
        'origin': origin,
        'destination': destination,
        'key': google_maps_api_key,
        'alternatives': 'true',  # Request alternative routes
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        routes = []
        for route in data['routes']:
            route_info = {
                'distance': route['legs'][0]['distance']['text'],
                'duration': route['legs'][0]['duration']['text'],
            }
            routes.append(route_info)
        return routes
    else:
        print("Error:", response.status_code)
        return None


# Function to fetch traffic incidents
def get_traffic_incidents(location):
    base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'

    params = {
        'location': location,
        'radius': '10000',  # Search within a radius of 10 km
        'type': 'traffic',
        'key': google_maps_api_key,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        incidents = []
        for result in data.get('results', []):
            incident_info = {
                'name': result['name'],
                'location': result['vicinity'],
            }
            incidents.append(incident_info)
        return incidents
    else:
        print("Error:", response.status_code)
        return None


# Function to suggest optimal departure time
def suggest_optimal_departure_time(origin, destination, desired_arrival_time):
    current_time = datetime.now()

    traffic_data = get_traffic_data(origin, destination, google_maps_api_key)
    if traffic_data:
        duration_in_traffic = traffic_data['duration_in_traffic']
        if duration_in_traffic != 'N/A':
            travel_time = timedelta(seconds=duration_in_traffic['value'])
            optimal_departure_time = desired_arrival_time - travel_time
            return optimal_departure_time
    return None


# Function to fetch public transit data
def get_public_transit_data(origin, destination):
    base_url = 'https://maps.googleapis.com/maps/api/directions/json?'

    params = {
        'origin': origin,
        'destination': destination,
        'key': google_maps_api_key,
        'mode': 'transit',  # Specify transit mode
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        transit_info = {
            'routes': data['routes']
        }
        return transit_info
    else:
        print("Error:", response.status_code)
        return None


# Function to collect weather, traffic, alternative route, and optimal departure time insights
def collect_insights():
    city = "Philadelphia"
    weather_data = get_weather_data(city, openweathermap_api_key)
    if weather_data:
        print("Weather Data:")
        for key, value in weather_data.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print()

    origin = input("Enter the origin address: ")
    if not origin:
        print("Error: Origin address cannot be empty.")
        return None

    destination = input("Enter the destination address: ")
    if not destination:
        print("Error: Destination address cannot be empty.")
        return None

    traffic_data = get_traffic_data(origin, destination, google_maps_api_key)
    if traffic_data:
        print("Traffic Data:")
        for key, value in traffic_data.items():
            print(f"{key.capitalize()}: {value}")
    else:
        print("Failed to fetch traffic data.")
        return None

    alternative_routes = get_alternative_routes(origin, destination)
    if alternative_routes:
        print("\nAlternative Routes:")
        for i, route in enumerate(alternative_routes, start=1):
            print(f"Route {i}: Distance - {route['distance']}, Duration - {route['duration']}")

    traffic_incidents = get_traffic_incidents(origin)
    if traffic_incidents:
        print("\nTraffic Incidents:")
        for incident in traffic_incidents:
            print(f"Name: {incident['name']}, Location: {incident['location']}")
    else:
        print("No traffic incidents found for the specified location.")

    desired_arrival_time_str = input("Enter your desired arrival time (YYYY-MM-DD HH:MM:SS): ")
    if not desired_arrival_time_str:
        print("Error: Desired arrival time cannot be empty.")
        return None

    try:
        desired_arrival_time = datetime.strptime(desired_arrival_time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("Error: Invalid format for desired arrival time. Please use YYYY-MM-DD HH:MM:SS format.")
        return None

    optimal_departure_time = suggest_optimal_departure_time(origin, destination, desired_arrival_time)
    if optimal_departure_time:
        print("\nSuggested Optimal Departure Time:", optimal_departure_time.strftime('%Y-%m-%d %H:%M:%S'))
    else:
        print("\nUnable to suggest optimal departure time.")

    # Get public transit data
    public_transit_data = get_public_transit_data(origin, destination)
    if public_transit_data:
        print("\nPublic Transit Data:")
        for route in public_transit_data['routes']:
            print(f"Transit Route: {route['summary']}")
            for step in route['legs'][0]['steps']:
                if 'transit_details' in step:
                    transit_details = step['transit_details']
                    print(
                        f"Take {transit_details['line']['name']} {transit_details['headsign']} from {transit_details['departure_stop']['name']} to {transit_details['arrival_stop']['name']}")

    return {
        "weather_data": weather_data,
        "traffic_data": traffic_data,
        "alternative_routes": alternative_routes,
        "traffic_incidents": traffic_incidents,
        "public_transit_data": public_transit_data,
        "optimal_departure_time": optimal_departure_time
    }


if __name__ == "__main__":
    philadelphia_insights = collect_insights()
    # print(philadelphia_insights)
