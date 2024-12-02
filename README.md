# kubiya
Kubiya.ai Home Assignment - Historical Travel Weather Analysis API


*Overview*
This project is a Python-based REST API that utilizes historical weather data from Open-Meteo to provide insights for travel planning. The API offers endpoints to get monthly weather profiles, find the best travel month based on preferred temperatures, compare weather across multiple cities, and retrieve metrics for the API usage.

Features
Monthly Weather Profile: Get average minimum and maximum temperatures for a city in a specific month over a 6-year period.
Best Travel Month Finder: Suggest the best month to visit a city based on preferred temperature ranges.
City Weather Comparison: Compare average temperatures across multiple cities for a specific month.
Metrics: Retrieve usage statistics for all endpoints.
Technology Stack
Language: Python 3.8+
Framework: FastAPI
HTTP Client: httpx (for asynchronous requests)
Setup Instructions
Prerequisites
Python 3.8 or higher installed on your system.
pip package manager.
Installation
Clone the repository


git clone https://github.com/yourusername/python-weather-api.git
cd python-weather-api
Create a virtual environment (optional but recommended)


python -m venv kubiyaenv
source kubiyaenv/bin/activate  # On Windows use `kubiyaenv\Scripts\activate`


*Install the required packages*
pip install -r requirements.txt
requirements.txt:
Flask
httpx

Run Command
To start the API server, run the following command:
uvicorn main:app --reload

The API will be available at http://127.0.0.1:8000.
Usage
Monthly Weather Profile
Endpoint: /weather/monthly-profile
Method: GET
Parameters:
city: Name of the city (e.g., London)
month: Month number (1-12)



curl "http://127.0.0.1:8000/weather/monthly-profile?city=London&month=7"
Best Travel Month Finder
Endpoint: /travel/best-month
Method: GET
Parameters:
city: Name of the city (e.g., Paris)
min_temp: Preferred minimum temperature
max_temp: Preferred maximum temperature



curl "http://127.0.0.1:8000/travel/best-month?city=Paris&min_temp=15&max_temp=25"
City Weather Comparison
Endpoint: /travel/compare-cities
Method: GET
Parameters:
cities: Comma-separated list of city names (2-5 cities)
month: Month number (1-12)



curl "http://127.0.0.1:8000/travel/compare-cities?cities=New York,Tokyo,Sydney&month=4"
Metrics
Endpoint: /metrics
Method: GET



curl "http://127.0.0.1:8000/metrics"
Notes
All data requests are for the period from January 1, 2018, to December 31, 2023.
The API only processes complete months; partial months are not supported.
The service uses in-memory caching to minimize redundant external API calls.
Metrics are tracked in-memory and include hits, errors, and processing times for each endpoint.
Error Handling
400 Bad Request: Returned when input parameters are invalid (e.g., month not in 1-12).
404 Not Found: Returned when the city is not found or no data is available for the specified month.
500 Internal Server Error: Returned when there is an issue with fetching or processing data.
Future Improvements
Implement persistent caching with a database or external caching service like Redis.
Add authentication and rate limiting.
Enhance error logging and monitoring.
Expand to support additional weather metrics like precipitation or wind speed.
