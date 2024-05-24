import unittest
from app import app

class TestAppIntegration(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Traffic Insights', response.data)

    def test_realtime_page(self):
        response = self.app.get('/realtime')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Real-Time Traffic Insights', response.data)

    def test_historical_insights_page(self):
        response = self.app.get('/historical-insights')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Historical Traffic Insights', response.data)

    def test_insights_post_request(self):
        # Simulate a POST request to the insights endpoint
        response = self.app.post('/insights', data={
            'origin': 'Stanley Park',
            'destination': 'White Rock',
            'desired_arrival_time': '2024-05-14 12:00:00'  # Example datetime format
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'weather_data', response.data)
        self.assertIn(b'traffic_data', response.data)
        self.assertIn(b'alternative_routes', response.data)
        self.assertIn(b'traffic_incidents', response.data)
        self.assertIn(b'optimal_departure_time', response.data)
        self.assertIn(b'public_transit_data', response.data)

if __name__ == '__main__':
    unittest.main()
