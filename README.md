# Weather and Travel Flask API

A Flask application that provides weather-related endpoints to help users plan their travels. It integrates with the Open-Meteo API to fetch historical weather data and uses MongoDB for caching and metrics tracking.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Clone the Repository](#clone-the-repository)
  - [Environment Variables](#environment-variables)
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

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/weather-travel-api.git
cd weather-travel-api
