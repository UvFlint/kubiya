import requests
import random
import time

BASE_URL = "http://13.60.52.33:5000" # or http://localhost:5000 to test locally

CITIES = [
    'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
    'London', 'Paris', 'Tokyo', 'Sydney', 'Moscow', 'Berlin',
    'Toronto', 'Beijing', 'Dubai', 'Sao Paulo'
]

total_tests = 0
passed_tests = 0
failed_tests = 0

def assert_response(condition, test_name, error_message=""):
    global passed_tests, failed_tests
    if condition:
        print(f"✔️  {test_name}: Passed")
        passed_tests += 1
    else:
        print(f"❌  {test_name}: Failed - {error_message}")
        failed_tests += 1

def test_weather_monthly_profile():
    global total_tests
    print("Testing /weather/monthly-profile")
    for i in range(5):
        total_tests += 1
        test_name = f"Test {i+1}: Valid request"
        city = random.choice(CITIES)
        month = random.randint(1, 12)
        params = {'city': city, 'month': month}
        try:
            response = requests.get(f"{BASE_URL}/weather/monthly-profile", params=params)
            response_json = response.json()
            condition = response.status_code == 200 and 'min_temp_avg' in response_json and 'max_temp_avg' in response_json
            assert_response(condition, test_name)
        except Exception as e:
            assert_response(False, test_name, error_message=str(e))
        time.sleep(0.5) 


    print("\nTesting error handling for /weather/monthly-profile")
    error_tests = [
        {'month': 5}, 
        {'city': 'New York'}, 
        {'city': 'New York', 'month': 13}, 
    ]
    for i, params in enumerate(error_tests, start=1):
        total_tests += 1
        test_name = f"Error Test {i}: Invalid parameters"
        try:
            response = requests.get(f"{BASE_URL}/weather/monthly-profile", params=params)
            response_json = response.json()
            condition = response.status_code == 400 and 'error' in response_json
            assert_response(condition, test_name)
        except Exception as e:
            assert_response(False, test_name, error_message=str(e))

def test_travel_best_month():
    global total_tests
    print("\nTesting /travel/best-month")
    for i in range(5):
        total_tests += 1
        test_name = f"Test {i+1}: Valid request"
        city = random.choice(CITIES)
        min_temp = round(random.uniform(-10, 25), 2)
        max_temp = round(random.uniform(min_temp, min_temp + 15), 2) 
        params = {'city': city, 'min_temp': min_temp, 'max_temp': max_temp}
        try:
            response = requests.get(f"{BASE_URL}/travel/best-month", params=params)
            response_json = response.json()
            condition = response.status_code == 200 and 'best_month' in response_json
            assert_response(condition, test_name)
        except Exception as e:
            assert_response(False, test_name, error_message=str(e))
        time.sleep(0.5)

 
    print("\nTesting error handling for /travel/best-month")
    error_tests = [
        {'city': 'London', 'min_temp': 15},
        {'city': 'London', 'max_temp': 25}, 
        {'min_temp': 15, 'max_temp': 25}, 
    ]
    for i, params in enumerate(error_tests, start=1):
        total_tests += 1
        test_name = f"Error Test {i}: Invalid parameters"
        try:
            response = requests.get(f"{BASE_URL}/travel/best-month", params=params)
            response_json = response.json()
            condition = response.status_code == 400 and 'error' in response_json
            assert_response(condition, test_name)
        except Exception as e:
            assert_response(False, test_name, error_message=str(e))

def test_travel_compare_cities():
    global total_tests
    print("\nTesting /travel/compare-cities")
    for i in range(5):
        total_tests += 1
        test_name = f"Test {i+1}: Valid request"
        num_cities = random.randint(2, 5)
        selected_cities = random.sample(CITIES, num_cities)
        month = random.randint(1, 12)
        cities_param = ','.join(selected_cities)
        params = {'cities': cities_param, 'month': month}
        try:
            response = requests.get(f"{BASE_URL}/travel/compare-cities", params=params)
            response_json = response.json()
            condition = response.status_code == 200 and all(city in response_json for city in selected_cities)
            assert_response(condition, test_name)
        except Exception as e:
            assert_response(False, test_name, error_message=str(e))
        time.sleep(0.5)


    print("\nTesting error handling for /travel/compare-cities")
    error_tests = [
        {'cities': ','.join(random.sample(CITIES, 6)), 'month': 5},  
        {'cities': 'New York,London', 'month': 13},  
        {'cities': 'New York', 'month': 5}, 
    ]
    for i, params in enumerate(error_tests, start=1):
        total_tests += 1
        test_name = f"Error Test {i}: Invalid parameters"
        try:
            response = requests.get(f"{BASE_URL}/travel/compare-cities", params=params)
            response_json = response.json()
            condition = response.status_code == 400 and 'error' in response_json
            assert_response(condition, test_name)
        except Exception as e:
            assert_response(False, test_name, error_message=str(e))

def test_metrics():
    global total_tests
    print("\nTesting /metrics")
    total_tests += 1
    test_name = "Test 1: Retrieve metrics"
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        response_json = response.json()
        condition = response.status_code == 200 and 'routes' in response_json
        assert_response(condition, test_name)
    except Exception as e:
        assert_response(False, test_name, error_message=str(e))

def main():
    print("Starting tests...\n")
    test_weather_monthly_profile()
    test_travel_best_month()
    test_travel_compare_cities()
    test_metrics()
    print("\nTests completed.\n")
    print("Test Summary:")
    print(f"Total Tests Run: {total_tests}")
    print(f"Tests Passed: {passed_tests}")
    print(f"Tests Failed: {failed_tests}")
    score = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"Score: {score:.2f}%")

if __name__ == "__main__":
    main()
