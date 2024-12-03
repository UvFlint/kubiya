import logging
import time
from flask import request, jsonify
from utils import WeatherAppException
from config import app
import services 
from services import track_metrics 

@app.route("/weather/monthly-profile", methods=["GET"])
async def monthly_weather_profile():
    route = "/weather/monthly-profile"
    start_time = time.perf_counter()
    error_occurred = False

    try:
        city = request.args.get("city")
        month = request.args.get("month")

        response = await services.monthly_weather_profile_service(city, month)
        logging.info(f"Monthly profile for city: {city}, month: {month} computed successfully.")
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

        response = await services.best_travel_month_service(city, min_temp, max_temp)
        logging.info(f"Best travel month for city: {city} is month: {response['best_month']}")
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

        response = await services.compare_cities_service(cities, month)
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
    try:
        response = await services.retrieve_metrics()
        logging.info("Metrics retrieved successfully.")
        return jsonify(response)
    except Exception as e:
        logging.exception(f"Error in get_metrics: {e}")
        return jsonify({"error": str(e)}), 500
