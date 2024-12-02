# Kubiya Weather and Travel Flask API

A Flask application that provides weather-related endpoints to help users plan their travels. It integrates with the Open-Meteo API to fetch historical weather data and uses MongoDB for caching and metrics tracking.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Clone the Repository](#clone-the-repository)
  - [Install Dependencies](#install-dependencies)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
  - [GET `/weather/monthly-profile`](#get-weathermonthly-profile)
  - [GET `/travel/best-month`](#get-travelbest-month)
  - [GET `/travel/compare-cities`](#get-travelcompare-cities)
  - [GET `/metrics`](#get-metrics)
- [Logging](#logging)
- [Caching Mechanism](#caching-mechanism)
- [Metrics Tracking](#metrics-tracking)

---

## Features

- **Monthly Weather Profile**: Get average minimum and maximum temperatures for a city in a specific month.
- **Best Travel Month**: Determine the best month to travel to a city based on preferred temperature ranges.
- **Compare Cities**: Compare weather data across multiple cities for a specific month.
- **Caching**: Caches geocoding and weather data to improve performance and reduce API calls.
- **Metrics Tracking**: Tracks API usage metrics like hits, errors, and response times.
- **Logging**: Logs important events and errors for debugging and monitoring.

---

## Requirements

- Python 3.7 or higher
- MongoDB instance (local or remote)
- pip (Python package installer)
- Flask
- requests
- pymongo
- python-dotenv
---

## Installation

### Clone the Repository

```bash
git clone https://github.com/UvFlint/kubiya.git
cd kubiya
```

### Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

---

## Running the Application
```bash
python main.py
```

## API Endpoints

### GET `/weather/monthly-profile`

Retrieve the average minimum and maximum temperatures for a specific city and month.

#### Query Parameters

- **`city`** (string, required): Name of the city.
- **`month`** (integer, required): Month number (1-12).

#### Example Request
```bash
curl.exe -s "http://13.60.21.244:5000/weather/monthly-profile?city=London&month=7"
```

#### Example Response
```json
{
  "city": "London",
  "max_temp_avg": 23.29,
  "min_temp_avg": 14.13,
  "month": 7
}
```

### GET `/travel/best-month`

Determine the best month to travel to a city based on preferred temperature ranges.

#### Query Parameters

- **`city`** (string, required): The name of the city for which the best travel month should be determined.
- **`min_temp`** (float, required): The preferred minimum temperature.
- **`max_temp`** (float, required): The preferred maximum temperature.

#### Example Request
```bash
curl.exe -s "http://13.60.21.244:5000/travel/best-month?city=Paris&min_temp=20&max_temp=30"
```



#### Example Response
The response will provide the city, the best month for travel, and the differences between the preferred and actual average temperatures.

```json
{
  "best_month": 7,
  "city": "Paris",
  "max_temp_diff": 3.99,
  "min_temp_diff": 4.39,
  "overall_diff": 8.38
}
```


### GET `/travel/compare-cities`

Compare weather data across multiple cities for a specific month.

#### Query Parameters

- **`cities`** (string, required): Comma-separated list of city names to compare. The number of cities must be between 2 and 5.
- **`month`** (integer, required): The month number (1-12) for which weather data should be compared.


#### Example Request
```bash
curl.exe -s "http://13.60.21.244:5000/travel/compare-cities?cities=New%20York,Los%20Angeles,Chicago&month=7"
```

#### Example Response

The response provides the average minimum and maximum temperatures for each city in the specified month.

```json
{
  "Chicago": {
    "max_temp_avg": 27.62,
    "min_temp_avg": 19.63
  },
  "Los Angeles": {
    "max_temp_avg": 30.94,
    "min_temp_avg": 17.14
  },
  "New York": {
    "max_temp_avg": 29.48,
    "min_temp_avg": 20.79
  },
  "month": 7
}
```

### GET `/metrics`

Retrieve API usage metrics, including the number of hits, errors, and response times for each endpoint.

#### Request
```bash
curl.exe -s "http://13.60.21.244:5000/metrics"
```


#### Response

The response provides detailed metrics for each API endpoint, including:

- `route_name`: The name of the route.
- `hits`: Total number of times the endpoint was accessed.
- `errors`: Total number of errors encountered.
- `avg_time`: Average response time in seconds.
- `max_time`: Maximum response time in seconds.
- `min_time`: Minimum response time in seconds.

#### Example Response

```json
{
  "routes": {
    "/travel/best-month": {
      "avg_time": 4.0583,
      "errors": 0,
      "hits": 2,
      "max_time": 6.0751,
      "min_time": 2.0416,
      "route_name": "/travel/best-month"
    },
    "/travel/compare-cities": {
      "avg_time": 1.3624,
      "errors": 3,
      "hits": 12,
      "max_time": 2.9324,
      "min_time": 0.0004,
      "route_name": "/travel/compare-cities"
    },
    "/weather/monthly-profile": {
      "avg_time": 0.1844,
      "errors": 4,
      "hits": 9,
      "max_time": 0.7247,
      "min_time": 0.0007,
      "route_name": "/weather/monthly-profile"
    }
  }
}
```


## Additional Inforamtion

### Logging
The application maintains detailed logs, including:

- API Requests and Responses: Logs each request with parameters and corresponding responses.
- Error Tracking: Captures errors with stack traces for easier debugging.
- Performance Metrics: Logs response times and other performance-related data.
- Logs are crucial for monitoring the application's health and troubleshooting issues.

### Caching Mechanism
To enhance performance and reduce external API dependency:

- Geocoding Cache: Stores latitude and longitude of cities.
- Weather Data Cache: Caches historical weather data.
- Caching is managed via MongoDB.

### Metrics Tracking
Monitors and records API usage:

- Hits and Errors: Counts successful and failed requests per endpoint.
- Response Times: Tracks average, maximum, and minimum response times.
Metrics help in understanding usage patterns and optimizing the application.