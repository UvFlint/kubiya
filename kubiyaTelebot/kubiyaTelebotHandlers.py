import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from kubiyaTelebotConstants import (
    MP_CITY, MP_MONTH,
    BTM_CITY, BTM_MIN_TEMP, BTM_MAX_TEMP,
    CC_CITIES, CC_MONTH
)
from kubiyaTelebotAPI import (
    get_monthly_weather_profile,
    get_best_travel_month,
    compare_cities,
    get_metrics as api_get_metrics
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Kubiya Weather Bot! 🌦️\n\n"
        "Use /monthly_profile to get the monthly weather profile of a city.\n"
        "Use /best_travel_month to find the best month to travel to a city.\n"
        "Use /compare_cities to compare weather conditions of multiple cities.\n"
        "Use /metrics to get API metrics.\n"
        "Use /help to see this message again."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n"
        "/monthly_profile - Get the monthly weather profile of a city.\n"
        "/best_travel_month - Find the best month to travel to a city.\n"
        "/compare_cities - Compare weather conditions of multiple cities.\n"
        "/metrics - Get API metrics.\n"
        "/cancel - Cancel the current operation."
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Operation cancelled.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def monthly_profile_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter the city:")
    return MP_CITY

async def monthly_profile_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    context.user_data['city'] = city
    await update.message.reply_text("Please enter the month (1-12):")
    return MP_MONTH

async def monthly_profile_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    month = update.message.text.strip()
    city = context.user_data['city']
    try:
        data = await get_monthly_weather_profile(city, month)
        formatted_data = f"Monthly Weather Profile for {city} in month {month}:\n{data}"
        await update.message.reply_text(formatted_data)
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
    return ConversationHandler.END

async def best_travel_month_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter the city:")
    return BTM_CITY

async def best_travel_month_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    context.user_data['city'] = city
    await update.message.reply_text("Please enter the minimum temperature:")
    return BTM_MIN_TEMP

async def best_travel_month_min_temp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    min_temp = update.message.text.strip()
    context.user_data['min_temp'] = min_temp
    await update.message.reply_text("Please enter the maximum temperature:")
    return BTM_MAX_TEMP

async def best_travel_month_max_temp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    max_temp = update.message.text.strip()
    city = context.user_data['city']
    min_temp = context.user_data['min_temp']
    try:
        data = await get_best_travel_month(city, min_temp, max_temp)
        formatted_data = f"Best travel month for {city} between {min_temp}°C and {max_temp}°C:\n{data}"
        await update.message.reply_text(formatted_data)
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
    return ConversationHandler.END

async def compare_cities_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter the cities (separated by commas):")
    return CC_CITIES

async def compare_cities_cities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cities = update.message.text.strip()
    context.user_data['cities'] = cities
    await update.message.reply_text("Please enter the month (1-12):")
    return CC_MONTH

async def compare_cities_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    month = update.message.text.strip()
    cities = context.user_data['cities']
    try:
        data = await compare_cities(cities, month)
        formatted_data = f"Comparison of cities {cities} in month {month}:\n{data}"
        await update.message.reply_text(formatted_data)
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
    return ConversationHandler.END

async def metrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await api_get_metrics()
        await update.message.reply_text(f"Metrics:\n{data}")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
