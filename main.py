import os
import logging
from flask import Flask, request, jsonify
import requests
import statistics
import time
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Ensure the logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Get logging level from environment variable or default to INFO
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

# MongoDB Setup
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'kubiaWeathreApp')
METRICS_COLLECTION = os.getenv('METRICS_COLLECTION', 'metrics')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
metrics_collection = db[METRICS_COLLECTION]

# In-memory cache
weather_cache = {}
geocode_cache = {}

START_DATE = "2018-01-01"
END_DATE = "2023-12-31"


def track_metrics(route, elapsed_time, error_occurred):
    try:
        # Update metrics in MongoDB
        metrics_collection.update_one(
            {'_id': route},
            {
                '$inc': {
                    'hits': 1,
                    'errors': int(error_occurred),
                    'total_time': elapsed_time
                },
                '$min': {'min_time': elapsed_time},
                '$max': {'max_time': elapsed_time},
                '$setOnInsert': {'route_name': route}
            },
            upsert=True
        )
        logging.info(f"Route {route} processed in {elapsed_time:.4f} seconds")
    except Exception as e:
        logging.exception(f"Failed to track metrics for route {route}: {e}")


def get_lat_lon(city):
    if city in geocode_cache:
        logging.debug(f"Geocode cache hit for city: {city}")
        return geocode_cache[city]

    logging.info(f"Fetching geocode data for city: {city}")
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f"Failed to fetch geocode data for city: {city}")
        raise ValueError("Geocoding API request failed.")

    data = response.json()

    if not data.get("results"):
        logging.error(f"City '{city}' not found in geocoding API.")
        raise ValueError(f"City '{city}' not found.")

    lat = data["results"][0]["latitude"]
    lon = data["results"][0]["longitude"]
    geocode_cache[city] = (lat, lon)
    logging.debug(f"Geocode data for city '{city}': lat={lat}, lon={lon}")
    return lat, lon


def get_weather_data(city, month):
    cache_key = f"{city}_{month}"
    if cache_key in weather_cache:
        logging.debug(f"Weather cache hit for key: {cache_key}")
        return weather_cache[cache_key]

    lat, lon = get_lat_lon(city)
    logging.info(f"Fetching weather data for city: {city}, month: {month}")
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
        f"&start_date={START_DATE}&end_date={END_DATE}"
        f"&daily=temperature_2m_min,temperature_2m_max&timezone=UTC"
    )
    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f"Failed to fetch weather data for city: {city}")
        raise ValueError("Weather API request failed.")

    data = response.json()

    if "daily" not in data:
        logging.error(f"Weather data not available for city: {city}")
        raise ValueError("Weather data not available.")

    dates = data["daily"]["time"]
    min_temps = data["daily"]["temperature_2m_min"]
    max_temps = data["daily"]["temperature_2m_max"]

    min_temps_month = [
        temp for date, temp in zip(dates, min_temps) if int(date.split("-")[1]) == month
    ]
    max_temps_month = [
        temp for date, temp in zip(dates, max_temps) if int(date.split("-")[1]) == month
    ]

    if not min_temps_month or not max_temps_month:
        logging.warning(f"No data for city: {city}, month: {month}")
        raise ValueError("No data for the specified month.")

    min_temp_avg = round(statistics.mean(min_temps_month), 2)
    max_temp_avg = round(statistics.mean(max_temps_month), 2)

    weather_cache[cache_key] = (min_temp_avg, max_temp_avg)
    logging.debug(f"Weather data for {city}, month {month}: min_avg={min_temp_avg}, max_avg={max_temp_avg}")
    return min_temp_avg, max_temp_avg


@app.route("/weather/monthly-profile", methods=["GET"])
def monthly_weather_profile():
    route = "/weather/monthly-profile"
    start_time = time.perf_counter()
    error_occurred = False

    try:
        city = request.args.get("city")
        month = request.args.get("month")

        if not city or not month:
            logging.error("Missing required parameters: city or month.")
            raise ValueError("City and month parameters are required.")

        month = int(month)

        if not 1 <= month <= 12:
            logging.error(f"Invalid month value: {month}")
            raise ValueError("Invalid month. Month must be between 1 and 12.")

        min_temp_avg, max_temp_avg = get_weather_data(city, month)
        response = {
            "city": city,
            "month": month,
            "min_temp_avg": min_temp_avg,
            "max_temp_avg": max_temp_avg,
        }
        logging.info(f"Monthly profile for city: {city}, month: {month} computed successfully.")
        return jsonify(response)
    except Exception as e:
        error_occurred = True
        logging.exception(f"Error in monthly_weather_profile: {e}")
        return jsonify({"error": str(e)}), 400
    finally:
        elapsed_time = time.perf_counter() - start_time
        track_metrics(route, elapsed_time, error_occurred)


@app.route("/travel/best-month", methods=["GET"])
def best_travel_month():
    route = "/travel/best-month"
    start_time = time.perf_counter()
    error_occurred = False

    try:
        city = request.args.get("city")
        min_temp = request.args.get("min_temp")
        max_temp = request.args.get("max_temp")

        if not city or min_temp is None or max_temp is None:
            logging.error("Missing required parameters: city, min_temp, or max_temp.")
            raise ValueError("City, min_temp, and max_temp parameters are required.")

        min_temp = float(min_temp)
        max_temp = float(max_temp)
        logging.info(f"Calculating best travel month for city: {city} with preferred temps: min={min_temp}, max={max_temp}")

        results = []
        for month in range(1, 13):
            min_avg, max_avg = get_weather_data(city, month)
            results.append((month, min_avg, max_avg))

        diffs = []
        for month, min_avg, max_avg in results:
            min_diff = abs(min_temp - min_avg)
            max_diff = abs(max_temp - max_avg)
            overall_diff = min_diff + max_diff
            diffs.append((overall_diff, month, min_diff, max_diff))

        best = min(diffs, key=lambda x: x[0])
        response = {
            "city": city,
            "best_month": best[1],
            "min_temp_diff": round(best[2], 2),
            "max_temp_diff": round(best[3], 2),
            "overall_diff": round(best[0], 2),
        }
        logging.info(f"Best travel month for city: {city} is month: {best[1]}")
        return jsonify(response)
    except Exception as e:
        error_occurred = True
        logging.exception(f"Error in best_travel_month: {e}")
        return jsonify({"error": str(e)}), 400
    finally:
        elapsed_time = time.perf_counter() - start_time
        track_metrics(route, elapsed_time, error_occurred)


@app.route("/travel/compare-cities", methods=["GET"])
def compare_cities():
    route = "/travel/compare-cities"
    start_time = time.perf_counter()
    error_occurred = False

    try:
        cities = request.args.get("cities")
        month = request.args.get("month")

        if not cities or not month:
            logging.error("Missing required parameters: cities or month.")
            raise ValueError("Cities and month parameters are required.")

        month = int(month)
        if not 1 <= month <= 12:
            logging.error(f"Invalid month value: {month}")
            raise ValueError("Invalid month. Month must be between 1 and 12.")

        city_list = [city.strip() for city in cities.split(",")]
        if not 2 <= len(city_list) <= 5:
            logging.error(f"Invalid number of cities: {len(city_list)}")
            raise ValueError("Number of cities must be between 2 and 5.")

        logging.info(f"Comparing cities: {city_list} for month: {month}")
        response = {"month": month}
        for city in city_list:
            min_avg, max_avg = get_weather_data(city, month)
            response[city] = {
                "min_temp_avg": min_avg,
                "max_temp_avg": max_avg,
            }
            logging.debug(f"Added weather data for city: {city}")

        logging.info(f"City comparison for month: {month} completed successfully.")
        return jsonify(response)
    except Exception as e:
        error_occurred = True
        logging.exception(f"Error in compare_cities: {e}")
        return jsonify({"error": str(e)}), 400
    finally:
        elapsed_time = time.perf_counter() - start_time
        track_metrics(route, elapsed_time, error_occurred)


@app.route("/metrics", methods=["GET"])
def get_metrics():
    response = {"routes": {}}
    try:
        for doc in metrics_collection.find():
            route = doc['_id']
            hits = doc.get('hits', 0)
            errors = doc.get('errors', 0)
            total_time = doc.get('total_time', 0.0)
            min_time = doc.get('min_time', 0.0)
            max_time = doc.get('max_time', 0.0)
            avg_time = round(total_time / hits, 4) if hits > 0 else 0.0
            response["routes"][route] = {
                "route_name": doc.get('route_name', route),
                "hits": hits,
                "errors": errors,
                "avg_time": avg_time,
                "max_time": round(max_time, 4),
                "min_time": round(min_time, 4),
            }
        logging.info("Metrics retrieved successfully.")
        return jsonify(response)
    except Exception as e:
        logging.exception(f"Error retrieving metrics: {e}")
        return jsonify({"error": "Failed to retrieve metrics"}), 500


if __name__ == "__main__":
    logging.info("Starting Flask app...")
    app.run(debug=True)
