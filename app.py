from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import plotly.graph_objs as go
import folium
from sklearn.cluster import KMeans



app = Flask(__name__, static_url_path='/static')

# Google Maps API Key
google_maps_api_key = "Google-Maps-API"

# OpenWeatherMap API Key
openweathermap_api_key = "OpenWeatherMap-API"


# Function to fetch weather data
def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweathermap_api_key}&units=metric"
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
def get_traffic_data(origin, destination):
    base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
    params = {
        'origins': origin,
        'destinations': destination,
        'key': google_maps_api_key,
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
                'congestion_level': data['rows'][0]['elements'][0].get('duration_in_traffic', 'N/A')
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

    traffic_data = get_traffic_data(origin, destination)
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
        return data
    else:
        print("Error:", response.status_code)
        return None

# Function to display public transit data
def display_public_transit_data(public_transit_data):
    if public_transit_data:
        print("\nPublic Transit Data:")
        for route in public_transit_data['routes']:
            print(f"Transit Route: {route['summary']}")
            for step in route['legs'][0]['steps']:
                if 'transit_details' in step:
                    transit_details = step['transit_details']
                    print(f"Take {transit_details['line']['name']} {transit_details['headsign']} from {transit_details['departure_stop']['name']} to {transit_details['arrival_stop']['name']}")

# Function to generate graphs
def generate_graphs():
    # Load the train dataset
    train_df = pd.read_csv("data/train_philadelphia.csv")

    # Select only numeric columns for correlation analysis
    numeric_columns = train_df.select_dtypes(include=['int64', 'float64'])

    # Calculate correlation matrix
    correlation_matrix = numeric_columns.corr()

    # Correlation Analysis
    plt.figure(figsize=(12, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix')
    plt.savefig('static/correlation_matrix.png')  # Save the graph to the static directory
    plt.close()  # Close the plot to prevent it from displaying on the webpage

    # Feature Distribution
    features_of_interest = ['TotalTimeStopped_p50', 'TimeFromFirstStop_p50', 'DistanceToFirstStop_p50']
    train_df[features_of_interest].hist(bins=20, figsize=(12, 6))
    plt.suptitle('Feature Distribution')
    plt.savefig('static/feature_distribution.png')  # Save the graph to the static directory
    plt.close()  # Close the plot to prevent it from displaying on the webpage

    # Temporal Analysis - Hourly Traffic Patterns
    hourly_traffic = train_df.groupby('Hour')['TotalTimeStopped_p50'].mean()
    plt.figure(figsize=(12, 6))
    hourly_traffic.plot(kind='bar', color='skyblue')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Average Total Time Stopped (p50)')
    plt.title('Hourly Traffic Patterns')
    plt.savefig('static/hourly_traffic_patterns.png')  # Save the graph to the static directory
    plt.close()  # Close the plot to prevent it from displaying on the webpage

    # Monthly Traffic Patterns
    monthly_traffic = train_df.groupby('Month')['TotalTimeStopped_p50'].mean()
    plt.figure(figsize=(12, 6))
    monthly_traffic.plot(kind='line', marker='o', color='orange')
    plt.xlabel('Month')
    plt.ylabel('Average Total Time Stopped (p50)')
    plt.title('Monthly Traffic Patterns')
    plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.savefig('static/monthly_traffic.png')  # Save the graph to the static directory
    plt.close()  # Close the plot to prevent it from displaying on the webpage

    # Extract latitude and longitude data
    X = train_df[['Latitude', 'Longitude']]

    # Perform K-means clustering
    kmeans = KMeans(n_clusters=100, random_state=42)
    train_df['cluster'] = kmeans.fit_predict(X)

    # Create a Folium map centered around Philadelphia
    m = folium.Map(location=[39.9526, -75.1652], zoom_start=11)

    # Plot clusters on the map
    for cluster in train_df['cluster'].unique():
        cluster_df = train_df[train_df['cluster'] == cluster]
        cluster_center = cluster_df[['Latitude', 'Longitude']].mean().values.tolist()
        folium.Marker(location=cluster_center,
                      icon=None,
                      popup=f'Cluster {cluster}',
                      tooltip=f'Cluster {cluster}').add_to(m)

    # Save the map as an HTML file with minimal HTML and asset compression
    m.save('clustered_traffic_map.html', close_file=False)

    # Load the merged dataset
    merged_df = pd.read_csv("data/merged_traffic_weather_data.csv")

    # Sample a subset of the data(e.g.,10%)
    merged_df_sample = merged_df.sample(frac=0.1, random_state=42)

    # Select relevant columns for analysis
    columns_of_interest = ['actual_mean_temp', 'average_precipitation', 'TotalTimeStopped_p20',
                           'DistanceToFirstStop_p80']
    analysis_df = merged_df[columns_of_interest]

    # Calculate correlations
    correlation_matrix = analysis_df.corr()

    # Visualizecorrelationsusingaheatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('CorrelationMatrixofWeatherVariablesandTrafficMetrics')
    plt.xlabel('Variables')
    plt.ylabel('Variables')
    plt.savefig('static/traffic-weather.png')
    plt.close()

    # Line plot of Traffic Metrics OverTime
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=merged_df_sample, x='Month', y='TotalTimeStopped_p20', label='TotalTimeStopped_p20')
    sns.lineplot(data=merged_df_sample, x='Month', y='DistanceToFirstStop_p80', label='DistanceToFirstStop_p80')
    plt.title('TrafficMetricsOverTime')
    plt.xlabel('Month')
    plt.ylabel('Value')
    plt.legend()
    plt.savefig('static/traffic-weather2.png')
    plt.close()

    # Scatter plot with Regression Line
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=merged_df_sample, x='actual_mean_temp', y='TotalTimeStopped_p20')
    sns.regplot(data=merged_df_sample, x='actual_mean_temp', y='TotalTimeStopped_p20', scatter=False, color='red')
    plt.title('Scatter Plot of actual_mean_temp vs.TotalTimeStopped_p20')
    plt.xlabel('ActualMeanTemperature')
    plt.ylabel('TotalTimeStopped(p20)')
    plt.savefig('static/traffic-weather3.png')
    plt.close()

    # Histograms of Weather Variables
    plt.figure(figsize=(10, 6))
    plt.subplot(1, 2, 1)
    sns.histplot(merged_df_sample['actual_mean_temp'], bins=20, kde=True, color='skyblue')
    plt.title('Histogram of Actual Mean Temperature')
    plt.xlabel('ActualMeanTemperature')

    plt.subplot(1, 2, 2)
    sns.histplot(merged_df_sample['average_precipitation'], bins=20, kde=True, color='salmon')
    plt.title('Histogram of Average Precipitation')
    plt.xlabel('AveragePrecipitation')
    plt.tight_layout()
    plt.savefig('static/traffic-weather4.png')
    plt.close()


# Function to generate hourly traffic data
def generate_hourly_traffic_data():
    # Load the train dataset
    train_df = pd.read_csv("data/merged_traffic_weather_data.csv")
    # Temporal Analysis
    hourly_traffic = train_df.groupby('Hour')['TotalTimeStopped_p50'].mean()

    # Create Plotly bar chart data
    data = [go.Bar(
                x=hourly_traffic.index,
                y=hourly_traffic.values,
                marker=dict(color='rgba(55, 128, 191, 0.7)')
        )]

    layout = go.Layout(
        title='Hourly Traffic Patterns',
        xaxis=dict(title='Hour of the Day'),
        yaxis=dict(title='Average Total Time Stopped (p50)'),
    )

    # Convert Plotly chart data to JSON
    hourly_traffic_json = {'data': data, 'layout': layout}

    return hourly_traffic_json



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/realtime')
def realtime():
    return render_template('index.html')

@app.route('/historical-insights')
def historical_insights():
    # Generate hourly traffic data
    hourly_traffic_json = generate_hourly_traffic_data()

    return render_template('historical_insights.html', hourly_traffic_json=hourly_traffic_json)

@app.route('/clustered-traffic-map')
def clustered_traffic_map():
    return render_template('clustered_traffic_map.html')

@app.route('/insights', methods=['POST'])
def insights():
    # Ensure POST method
    if request.method == 'POST':
        city = "Philadelphia"  # Default city for weather data
        weather_data = get_weather_data(city)

        origin = request.form.get('origin')
        destination = request.form.get('destination')
        desired_arrival_time_str = request.form.get('desired_arrival_time')
        public_transit_data = get_public_transit_data(origin, destination)
        display_public_transit_data(public_transit_data)

        # Additional validation for origin and destination
        if not origin:
            return jsonify({'error': f'Invalid input, Please enter the correct origin.', 'invalid_input': 'origin'}), 400
        elif not destination:
            return jsonify({'error': f'Invalid input, Please enter the correct destination.', 'invalid_input': 'destination'}), 400

        # Check if origin, destination, and desired_arrival_time are provided
        if not all([origin, destination, desired_arrival_time_str]):
            error_message = 'Missing form data'
            return jsonify({'error': error_message}), 400

        # Check if desired_arrival_time is in the future
        try:
            desired_arrival_time = datetime.fromisoformat(desired_arrival_time_str)
            if desired_arrival_time < datetime.now():
                error_message = 'Arrival date and time must be in the future'
                return jsonify({'error': error_message}), 400
        except ValueError:
            error_message = 'Invalid datetime format'
            return jsonify({'error': error_message}), 400

        traffic_data = get_traffic_data(origin, destination)
        if traffic_data is None:
            return jsonify({'error': 'Failed to retrieve traffic data'}), 500

        alternative_routes = get_alternative_routes(origin, destination)
        if alternative_routes is None:
            return jsonify({'error': 'Failed to retrieve alternative routes'}), 500

        traffic_incidents = get_traffic_incidents(origin)
        if traffic_incidents is None:
            return jsonify({'error': 'Failed to retrieve traffic incidents'}), 500

        optimal_departure_time = suggest_optimal_departure_time(origin, destination, desired_arrival_time)

        public_transit_data = get_public_transit_data(origin, destination)
        if public_transit_data is None:
            return jsonify({'error': 'Failed to retrieve public transit data'}), 500

        # Return JSON data to the client
        insights_data = {
            'weather_data': weather_data,
            'traffic_data': traffic_data,
            'alternative_routes': alternative_routes,
            'traffic_incidents': traffic_incidents,
            'optimal_departure_time': optimal_departure_time,
            'public_transit_data': public_transit_data
        }
        return jsonify(insights_data)

    # Handle invalid request method
    return jsonify({'error': 'Invalid request method'}), 405


if __name__ == "__main__":
    app.run(debug=True)

