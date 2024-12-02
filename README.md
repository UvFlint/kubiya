Kubiya Weather API
Kubiya.ai Home Assignment - Historical Travel Weather Analysis API

Overview
This project is a Python-based REST API that utilizes historical weather data from Open-Meteo to provide insights for travel planning. The API offers endpoints to:

Get monthly weather profiles.
Find the best travel month based on preferred temperatures.
Compare weather across multiple cities.
Retrieve metrics for API usage.
Features
Monthly Weather Profile: Get average minimum and maximum temperatures for a city in a specific month over a 6-year period.
Best Travel Month Finder: Suggest the best month to visit a city based on preferred temperature ranges.
City Weather Comparison: Compare average temperatures across multiple cities for a specific month.
Metrics: Retrieve usage statistics for all endpoints.
Technology Stack
Language: Python 3.8+
Framework: Flask
HTTP Client: requests
Database: MongoDB (for metrics storage)
Environment Variables: Managed with python-dotenv
Setup Instructions
Prerequisites
Python 3.8 or higher installed on your system.
pip package manager.
MongoDB installed and running.
Optional but Recommended: Use a virtual environment.
Installation
Clone the repository

bash
Copy code
git clone https://github.com/yourusername/kubiya-weather-api.git
cd kubiya-weather-api
Create a virtual environment

bash
Copy code
python -m venv kubiyaenv
source kubiyaenv/bin/activate  # On Windows use `kubiyaenv\Scripts\activate`
Install the required packages

bash
Copy code
pip install -r requirements.txt
requirements.txt:

Copy code
Flask
requests
pymongo
python-dotenv
Create a .env file

Create a .env file in the project root directory with the following content:

dotenv
Copy code
# MongoDB configuration
MONGO_URI=mongodb://localhost:27017/
DB_NAME=kubiaWeathreApp
METRICS_COLLECTION=metrics

# Logging configuration
LOG_LEVEL=INFO
Adjust the MongoDB connection string (MONGO_URI) if your setup is different.

Run Command
To start the API server, run the following command:

bash
Copy code
python app.py
The API will be available at http://127.0.0.1:5000.

Usage
Monthly Weather Profile
Endpoint: /weather/monthly-profile
Method: GET
Parameters:
city: Name of the city (e.g., London)
month: Month number (1-12)
Example Request:

bash
Copy code
curl "http://127.0.0.1:5000/weather/monthly-profile?city=London&month=7"
Sample Response:

json
Copy code
{
  "city": "London",
  "month": 7,
  "min_temp_avg": 14.13,
  "max_temp_avg": 23.29
}
Best Travel Month Finder
Endpoint: /travel/best-month
Method: GET
Parameters:
city: Name of the city (e.g., Paris)
min_temp: Preferred minimum temperature
max_temp: Preferred maximum temperature
Example Request:

bash
Copy code
curl "http://127.0.0.1:5000/travel/best-month?city=Paris&min_temp=15&max_temp=25"
Sample Response:

json
Copy code
{
  "city": "Paris",
  "best_month": 8,
  "min_temp_diff": 0.47,
  "max_temp_diff": 0.48,
  "overall_diff": 0.95
}
City Weather Comparison
Endpoint: /travel/compare-cities
Method: GET
Parameters:
cities: Comma-separated list of city names (2-5 cities)
month: Month number (1-12)
Example Request:

bash
Copy code
curl "http://127.0.0.1:5000/travel/compare-cities?cities=New York,Tokyo,Sydney&month=4"
Sample Response:

json
Copy code
{
  "month": 4,
  "New York": {
    "min_temp_avg": 5.72,
    "max_temp_avg": 15.26
  },
  "Tokyo": {
    "min_temp_avg": 9.57,
    "max_temp_avg": 18.58
  },
  "Sydney": {
    "min_temp_avg": 14.22,
    "max_temp_avg": 22.66
  }
}
Metrics
Endpoint: /metrics
Method: GET
Example Request:

bash
Copy code
curl "http://127.0.0.1:5000/metrics"
Sample Response:

json
Copy code
{
  "routes": {
    "/weather/monthly-profile": {
      "route_name": "/weather/monthly-profile",
      "hits": 1,
      "errors": 0,
      "avg_time": 0.9011,
      "max_time": 0.9011,
      "min_time": 0.9011
    },
    "/travel/best-month": {
      "route_name": "/travel/best-month",
      "hits": 1,
      "errors": 0,
      "avg_time": 0.6813,
      "max_time": 0.6813,
      "min_time": 0.6813
    },
    "/travel/compare-cities": {
      "route_name": "/travel/compare-cities",
      "hits": 1,
      "errors": 0,
      "avg_time": 0.3947,
      "max_time": 0.3947,
      "min_time": 0.3947
    }
  }
}
Notes
All data requests are for the period from January 1, 2018, to December 31, 2023.
The API only processes complete months; partial months are not supported.
The service uses in-memory caching to minimize redundant external API calls.
Metrics are stored in MongoDB and include hits, errors, and processing times for each endpoint.
Logging: All logs are saved in the logs/app.log file.
Error Handling
400 Bad Request: Returned when input parameters are invalid (e.g., month not in 1-12).
404 Not Found: Returned when the city is not found or no data is available for the specified month.
500 Internal Server Error: Returned when there is an issue with fetching or processing data.
Future Improvements
Implement persistent caching with a database or external caching service like Redis.
Add authentication and rate limiting.
Enhance error logging and monitoring.
Expand to support additional weather metrics like precipitation or wind speed.