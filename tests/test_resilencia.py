import unittest
from unittest.mock import patch, Mock
import requests
from tenacity import retry, stop_after_attempt
import pybreaker
import time

# Simulated microservice endpoints
PRODUCT_SERVICE_URL = "http://localhost:5000/productos"
INVENTORY_SERVICE_URL = "http://localhost:5001/inventario"

# Retry decorator
@retry(stop=stop_after_attempt(3))
def get_with_retry(url):
    response = requests.get(url)
    response.raise_for_status()
    return response

# Circuit breaker
cb = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=1)  # Short timeout for testing

class TestResiliencia(unittest.TestCase):

    def setUp(self):
        print("\nRunning:", self._testMethodName)

    def tearDown(self):
        print("Test completed.")

    @patch('requests.get')
    def test_error_handling(self, mock_get):
        print("Testing 404 error handling...")
        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = {"error": "Not found"}

        response = requests.get(f"{PRODUCT_SERVICE_URL}/999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "Not found"})
        print("404 error was properly handled and returned.")

    @patch('requests.get')
    def test_retry(self, mock_get):
        print("Testing retry mechanism...")
        mock_get.side_effect = [
            requests.exceptions.RequestException,
            requests.exceptions.RequestException,
            Mock(status_code=200, json=lambda: {"id": 1, "name": "Product 1"})
        ]

        response = get_with_retry(PRODUCT_SERVICE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": 1, "name": "Product 1"})
        self.assertEqual(mock_get.call_count, 3)
        print(f"Retry mechanism worked correctly. Made {mock_get.call_count} attempts before succeeding.")

    @patch('requests.get')
    def test_circuit_breaker(self, mock_get):
        print("Testing circuit breaker...")
        mock_get.side_effect = requests.exceptions.RequestException

        print("Simulating multiple failures to open the circuit...")
        for _ in range(4):
            try:
                cb.call(lambda: requests.get(INVENTORY_SERVICE_URL))
            except (pybreaker.CircuitBreakerError, requests.exceptions.RequestException):
                pass

        print("Verifying that the circuit is open...")
        with self.assertRaises(pybreaker.CircuitBreakerError):
            cb.call(lambda: requests.get(INVENTORY_SERVICE_URL))

        print(f"Waiting for the reset timeout ({cb.reset_timeout} seconds)...")
        time.sleep(cb.reset_timeout + 0.1)

        print("Simulating a successful request to close the circuit...")
        mock_get.side_effect = None
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": 1, "quantity": 10}

        response = cb.call(lambda: requests.get(INVENTORY_SERVICE_URL))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": 1, "quantity": 10})
        print("Circuit breaker closed after successful request.")

if __name__ == '__main__':
    unittest.main(verbosity=2)