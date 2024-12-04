import httpx

API_BASE_URL = "http://13.60.52.33:5000"

async def get_monthly_weather_profile(city, month):
    url = f"{API_BASE_URL}/weather/monthly-profile"
    params = {'city': city, 'month': month}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

async def get_best_travel_month(city, min_temp, max_temp):
    url = f"{API_BASE_URL}/travel/best-month"
    params = {'city': city, 'min_temp': min_temp, 'max_temp': max_temp}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

async def compare_cities(cities, month):
    url = f"{API_BASE_URL}/travel/compare-cities"
    params = {'cities': cities, 'month': month}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

async def get_metrics():
    url = f"{API_BASE_URL}/metrics"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
