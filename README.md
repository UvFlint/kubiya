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
- [Examples](#examples)
- [Logging](#logging)
- [Caching Mechanism](#caching-mechanism)
- [Metrics Tracking](#metrics-tracking)
- [License](#license)

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

#### Response

```json
{
  "city": "London",
  "month": 5,
  "min_temp_avg": 10.5,
  "max_temp_avg": 18.2
}
```

### GET `/travel/best-month`

Determine the best month to travel to a city based on preferred temperature ranges.

#### Query Parameters

- **`city`** (string, required): The name of the city for which the best travel month should be determined.
- **`min_temp`** (float, required): The preferred minimum temperature.
- **`max_temp`** (float, required): The preferred maximum temperature.

#### Response

The response will provide the city, the best month for travel, and the differences between the preferred and actual average temperatures.

```json
{
  "city": "Paris",
  "best_month": 6,
  "min_temp_diff": 0.3,
  "max_temp_diff": 0.5,
  "overall_diff": 0.8
}
```


### GET `/travel/compare-cities`

Compare weather data across multiple cities for a specific month.

#### Query Parameters

- **`cities`** (string, required): Comma-separated list of city names to compare. The number of cities must be between 2 and 5.
- **`month`** (integer, required): The month number (1-12) for which weather data should be compared.

#### Response

The response provides the average minimum and maximum temperatures for each city in the specified month.

```json
{
  "month": 7,
  "New York": {
    "min_temp_avg": 20.1,
    "max_temp_avg": 29.4
  },
  "Los Angeles": {
    "min_temp_avg": 18.5,
    "max_temp_avg": 25.0
  }
}
```