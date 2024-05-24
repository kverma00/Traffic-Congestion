# test_app.py

import unittest
from app import get_weather_data, get_traffic_data, get_alternative_routes, get_traffic_incidents, \
    suggest_optimal_departure_time, get_public_transit_data
from datetime import datetime, timedelta

class TestAppFunctions(unittest.TestCase):

    def test_get_weather_data(self):
        # Test case for get_weather_data function
        # Positive test case with a valid city
        city = "Philadelphia"
        weather_data = get_weather_data(city)
        self.assertIsNotNone(weather_data)

        # Negative test case with an invalid city
        city = "InvalidCity"
        weather_data = get_weather_data(city)
        self.assertIsNone(weather_data)

    def test_get_traffic_data(self):
        # Test case for get_traffic_data function
        # Positive test case with valid origin and destination
        origin = "Liberty Bell"
        destination = "Franklin Square"
        traffic_data = get_traffic_data(origin, destination)
        self.assertIsNotNone(traffic_data)

        # Negative test case with invalid origin and destination
        origin = "InvalidAddress"
        destination = "InvalidAddress"
        traffic_data = get_traffic_data(origin, destination)
        self.assertIsNone(traffic_data)

    def test_get_alternative_routes(self):
        # Test case for get_alternative_routes function
        # Positive test case with valid origin and destination
        origin = "Liberty Bell"
        destination = "Franklin Square"
        alternative_routes = get_alternative_routes(origin, destination)
        self.assertIsNotNone(alternative_routes, [])

        # Negative test case with invalid origin and destination
        origin = "InvalidAddress"
        destination = "InvalidAddress"
        alternative_routes = get_alternative_routes(origin, destination)
        self.assertIsNotNone(alternative_routes, [])

    def test_get_traffic_incidents(self):
        # Test case for get_traffic_incidents function
        # Positive test case with valid location
        location = "Liberty Bell"
        traffic_incidents = get_traffic_incidents(location)
        self.assertIsNotNone(traffic_incidents, [])

        # Negative test case with invalid location
        location = "InvalidAddress"
        traffic_incidents = get_traffic_incidents(location)
        self.assertIsNotNone(traffic_incidents, [])

    def test_suggest_optimal_departure_time(self):
        # Test case for suggest_optimal_departure_time function
        # Positive test case with valid origin, destination, and desired arrival time
        origin = "Liberty Bell"
        destination = "Franklin Square"
        desired_arrival_time = datetime.now() + timedelta(hours=1)
        optimal_departure_time = suggest_optimal_departure_time(origin, destination, desired_arrival_time)
        self.assertIsNotNone(optimal_departure_time)

        # Negative test case with invalid origin, destination, and desired arrival time
        origin = "InvalidAddress"
        destination = "InvalidAddress"
        desired_arrival_time = "InvalidDateTime"
        optimal_departure_time = suggest_optimal_departure_time(origin, destination, desired_arrival_time)
        self.assertIsNone(optimal_departure_time)

    def test_get_public_transit_data(self):
        # Test case for get_public_transit_data function
        # Positive test case with valid origin and destination
        origin = "Liberty Bell"
        destination = "Franklin Square"
        public_transit_data = get_public_transit_data(origin, destination)
        self.assertIsNotNone(public_transit_data,'NOT_FOUND')

        # Negative test case with invalid origin and destination
        origin = "InvalidAddress"
        destination = "InvalidAddress"
        public_transit_data = get_public_transit_data(origin, destination)
        self.assertIsNotNone(public_transit_data,'NOT_FOUND')

    def test_get_alternative_routes_no_routes_found(self):
        # Test case for get_alternative_routes function when no routes are found
        # Negative test case when no alternative routes are found
        origin = "InvalidOrigin"
        destination = "InvalidDestination"
        alternative_routes = get_alternative_routes(origin, destination)
        self.assertEqual(alternative_routes, [])

    def test_get_traffic_incidents_no_incidents_found(self):
        # Test case for get_traffic_incidents function when no incidents are found
        # Negative test case when no traffic incidents are found
        location = "InvalidLocation"
        traffic_incidents = get_traffic_incidents(location)
        self.assertEqual(traffic_incidents, [])

    def test_suggest_optimal_departure_time_invalid_inputs(self):
        # Test case for suggest_optimal_departure_time function with invalid inputs
        # Negative test case with invalid origin, destination, and desired arrival time
        origin = "InvalidAddress"
        destination = "InvalidAddress"
        desired_arrival_time = "InvalidDateTime"
        optimal_departure_time = suggest_optimal_departure_time(origin, destination, desired_arrival_time)
        self.assertIsNone(optimal_departure_time)


    def test_optimal_departure_time_with_future_arrival(self):
        # Test case to verify optimal departure time calculation with a future arrival time
        origin = "Liberty Bell"
        destination = "Franklin Square"
        desired_arrival_time = datetime.now() + timedelta(days=1)
        optimal_departure_time = suggest_optimal_departure_time(origin, destination, desired_arrival_time)
        self.assertIsNotNone(optimal_departure_time)

    def test_no_alternative_routes_for_straight_path(self):
        # Test case to verify behavior when there are no alternative routes for a straight path
        origin = "City Hall"
        destination = "Philadelphia Museum of Art"
        alternative_routes = get_alternative_routes(origin, destination)
        self.assertEqual(len(alternative_routes), 0)

    def test_traffic_incidents_in_remote_location(self):
        # Test case to ensure traffic incidents retrieval works for a remote location
        location = "Mount Everest"
        traffic_incidents = get_traffic_incidents(location)
        self.assertIsNotNone(traffic_incidents)


if __name__ == '__main__':
    unittest.main()
