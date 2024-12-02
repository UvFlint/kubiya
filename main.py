import os
import logging
import statistics
import time
import asyncio

from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from asgiref.wsgi import WsgiToAsgi  # Import WsgiToAsgi

from utils import WeatherAppException

# Load environment variables
load_dotenv()

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Logging configuration
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
DB_NAME = os.getenv('DB_NAME', 'kubiya')

try:
    client = AsyncIOMotorClient(MONGO_URI)
    logging.info("Connected to MongoDB successfully.")
except Exception as e:
    logging.info(f"Failed to connect to MongoDB: {str(e)}")

db = client[DB_NAME]
metrics_collection = db["metrics"]
metrics_objectID = ObjectId("674d77e62034f74473b1e65f")
cache_collection = db["cache"]

START_DATE = "2018-01-01"
END_DATE = "2023-12-31"

async def check_cache(cache_type, city, month=None):
    try:
        filter_query = {"cache_type": cache_type, "city": city}
        if month is not None:
            filter_query["month"] = month
        result = await cache_collection.find_one(filter_query)
        if not result:
            return False
        return result
    except Exception as e:
        logging.exception(f"Couldn't get cache from mongodb - {str(e)}")

async def track_metrics(route, elapsed_time, error_occurred):
    try:
        filter_query = {"_id": metrics_objectID}
        update_query = {
            "$inc": {
                f"{route}.hits": 1,
                f"{route}.errors": int(error_occurred),
            },
            "$min": {f"{route}.min_time": elapsed_time},
            "$max": {f"{route}.max_time": elapsed_time},
            "$push": {f"{route}.times": elapsed_time},
            "$setOnInsert": {f"{route}.route_name": route}
        }

        await metrics_collection.update_one(
            filter_query,
            update_query,
            upsert=True
        )
        logging.info(f"Route {route} processed in {elapsed_time:.2f} seconds")
    except Exception as e:
        logging.exception(f"Failed to track metrics for route {route}: {e}")


async def get_lat_lon(city):
    cache_temp = await check_cache("geocode", city)
    if cache_temp:
        logging.debug(f"Geocode cache hit for city: {city}")
        return (cache_temp["lat"], cache_temp["lon"])

    logging.info(f"Fetching geocode data for city: {city}")
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, verify=False)

    if response.status_code != 200:
        logging.error(f"Failed to fetch geocode data for city: {city}")
        raise WeatherAppException("Geocoding API request failed.")

    data = response.json()

    if not data.get("results"):
        logging.error(f"City '{city}' not found in open-meteo geocoding API.")
        raise WeatherAppException(f"City '{city}' not found.")

    lat = data["results"][0]["latitude"]
    lon = data["results"][0]["longitude"]
    await insert_geocode(city, lat, lon)
    logging.debug(f"Geocode data for city '{city}': lat={lat}, lon={lon}")
    return lat, lon


async def insert_geocode(city, lat, lon):
    try:
        await cache_collection.insert_one({
            "cache_type": "geocode",
            "city": city,
            "lat": lat,
            "lon": lon
        })
    except Exception as e:
        logging.exception(f"Error occurred while inserting city geocode - {str(e)}")


async def get_weather_data(city, month):
    weather_cache_temp = await check_cache("weather", city, month)
    if weather_cache_temp:
        logging.debug(f"Weather cache hit for city and month: {city}-{month}")
        return (weather_cache_temp["min_temp_avg"], weather_cache_temp["max_temp_avg"])

    lat, lon = await get_lat_lon(city)
    logging.info(f"Fetching weather data for city: {city}, month: {month}")

    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={START_DATE}&end_date={END_DATE}"
        f"&daily=temperature_2m_min,temperature_2m_max&timezone=UTC"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url, verify=False)

    if response.status_code != 200:
        logging.error(f"Failed to fetch weather data for city: {city}")
        raise WeatherAppException("Weather API request failed.")

    data = response.json()

    if "daily" not in data:
        logging.error(f"Weather data not available for city: {city}")
        raise WeatherAppException("Weather data not available.")

    dates = data["daily"]["time"]
    min_temps = data["daily"]["temperature_2m_min"]
    max_temps = data["daily"]["temperature_2m_max"]

    min_temps_month = []
    for date, temp in zip(dates, min_temps):
        if int(date.split("-")[1]) == month:
            min_temps_month.append(temp)

    max_temps_month = []
    for date, temp in zip(dates, max_temps):
        if int(date.split("-")[1]) == month:
            max_temps_month.append(temp)

    if not min_temps_month or not max_temps_month:
        logging.warning(f"No data for city: {city}, month: {month}")
        raise WeatherAppException("No data for the specified month.")

    min_temp_avg = round(statistics.mean(min_temps_month), 2)
    max_temp_avg = round(statistics.mean(max_temps_month), 2)

    await insert_weather(city, month, min_temp_avg, max_temp_avg)
    logging.debug(
        f"Weather data for {city}, month {month}: "
        f"min_avg={min_temp_avg}, max_avg={max_temp_avg}"
    )
    return min_temp_avg, max_temp_avg

async def insert_weather(city, month, min_temp_avg, max_temp_avg):
    try:
        await cache_collection.insert_one({
            "cache_type": "weather",
            "city": city,
            "month": month,
            "min_temp_avg": min_temp_avg,
            "max_temp_avg": max_temp_avg
        })
    except Exception as e:
        logging.exception(f"Error occurred while inserting city and month weather - {str(e)}")

@app.route("/weather/monthly-profile", methods=["GET"])
async def monthly_weather_profile():
    route = "/weather/monthly-profile"
    start_time = time.perf_counter()
    error_occurred = False

    try:
        city = request.args.get("city")
        month = request.args.get("month")

        if not city or not month:
            logging.error("Missing required parameters: city or month.")
            raise WeatherAppException("City and month parameters are required.")

        month = int(month)

        if not 1 <= month <= 12:
            logging.error(f"Invalid month value: {month}")
            raise WeatherAppException("Invalid month. Month must be between 1 and 12.")

        min_temp_avg, max_temp_avg = await get_weather_data(city, month)
        response = {
            "city": city,
            "month": month,
            "min_temp_avg": min_temp_avg,
            "max_temp_avg": max_temp_avg,
        }
        logging.info(
            f"Monthly profile for city: {city}, month: {month} computed successfully."
        )
        return jsonify(response)
    except Exception as e:
        error_occurred = True
        logging.exception(f"Error in monthly_weather_profile: {e}")
        return jsonify({"error": str(e)}), 400
    finally:
        elapsed_time = time.perf_counter() - start_time
        await track_metrics(route, elapsed_time, error_occurred)


@app.route("/travel/best-month", methods=["GET"])
async def best_travel_month():
    route = "/travel/best-month"
    start_time = time.perf_counter()
    error_occurred = False

    try:
        city = request.args.get("city")
        min_temp = request.args.get("min_temp")
        max_temp = request.args.get("max_temp")

        if not city or min_temp is None or max_temp is None:
            logging.error("Missing required parameters: city, min_temp, or max_temp.")
            raise WeatherAppException(
                "City, min_temp, and max_temp parameters are required."
            )

        min_temp = float(min_temp)
        max_temp = float(max_temp)
        logging.info(
            f"Calculating best travel month for city: {city} with preferred temps: "
            f"min={min_temp}, max={max_temp}"
        )

        results = []
        for month in range(1, 13):
            min_avg, max_avg = await get_weather_data(city, month)
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
        await track_metrics(route, elapsed_time, error_occurred)


@app.route("/travel/compare-cities", methods=["GET"])
async def compare_cities():
    route = "/travel/compare-cities"
    start_time = time.perf_counter()
    error_occurred = False

    try:
        cities = request.args.get("cities")
        month = request.args.get("month")

        if not cities or not month:
            logging.error("Missing required parameters: cities or month.")
            raise WeatherAppException("Cities and month parameters are required.")

        month = int(month)
        if not 1 <= month <= 12:
            logging.error(f"Invalid month value: {month}")
            raise WeatherAppException("Invalid month. Month must be between 1 and 12.")

        city_list = [city.strip() for city in cities.split(",")]
        if not 2 <= len(city_list) <= 5:
            logging.error(f"Invalid number of cities: {len(city_list)}")
            raise WeatherAppException("Number of cities must be between 2 and 5.")

        logging.info(f"Comparing cities: {city_list} for month: {month}")
        response = {"month": month}
        for city in city_list:
            min_avg, max_avg = await get_weather_data(city, month)
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
        await track_metrics(route, elapsed_time, error_occurred)


@app.route("/metrics", methods=["GET"])
async def get_metrics():
    response = {"routes": {}}
    try:
        docs = metrics_collection.find()

        async for doc in docs:
            for route, data in doc.items():
                if route == "_id":
                    continue

                hits = data.get("hits", 0)
                errors = data.get("errors", 0)
                times = data.get("times", [])

                total_time = sum(times)
                min_time = min(times) if times else 0.0
                max_time = max(times) if times else 0.0
                avg_time = round(total_time / hits, 4) if hits > 0 else 0.0

                response["routes"][route] = {
                    "route_name": data.get("route_name", route),
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
    logging.info("Starting Flask app with Uvicorn...")
    import uvicorn
    uvicorn.run(asgi_app, host="0.0.0.0", port=5000, log_level="info")