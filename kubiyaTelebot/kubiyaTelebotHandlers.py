
import logging
from telegram import (
    Update,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
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

CITIES = [
    'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
    'London', 'Paris', 'Tokyo', 'Sydney', 'Moscow', 'Berlin',
    'Toronto', 'Beijing', 'Dubai', 'Sao Paulo'
]

def build_city_keyboard():
    keyboard = []
    row = []
    for index, city in enumerate(CITIES):
        row.append(InlineKeyboardButton(city, callback_data=city))
        if (index + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

def build_city_keyboard_with_done(selected_cities):
    keyboard = []
    row = []
    for index, city in enumerate(CITIES):
        if city in selected_cities:
            button_text = f"✓ {city}"
        else:
            button_text = city
        row.append(InlineKeyboardButton(button_text, callback_data=city))
        if (index + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    done_button = InlineKeyboardButton('Done', callback_data='done')
    keyboard.append([done_button])
    return InlineKeyboardMarkup(keyboard)

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
    keyboard = build_city_keyboard()
    keyboard_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please select the city:", reply_markup=keyboard_markup)
    return MP_CITY

async def monthly_profile_city_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city = query.data
    context.user_data['city'] = city
    await query.edit_message_text(f"You have selected: {city}\nPlease enter the month (1-12):")
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
    keyboard = build_city_keyboard()
    keyboard_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please select the city:", reply_markup=keyboard_markup)
    return BTM_CITY

async def best_travel_month_city_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city = query.data
    context.user_data['city'] = city
    await query.edit_message_text(f"You have selected: {city}\nPlease enter the minimum temperature:")
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
    context.user_data['selected_cities'] = []
    keyboard = build_city_keyboard_with_done(selected_cities=[])
    await update.message.reply_text(
        "Please select the cities (tap to select, 'Done' when finished):",
        reply_markup=keyboard
    )
    return CC_CITIES

async def compare_cities_city_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    selected_cities = context.user_data.get('selected_cities', [])
    if data == 'done':
        if not selected_cities:
            await query.edit_message_text("You have not selected any cities. Operation cancelled.")
            return ConversationHandler.END
        else:
            cities_str = ', '.join(selected_cities)
            await query.edit_message_text(f"You have selected: {cities_str}\nPlease enter the month (1-12):")
            return CC_MONTH
    else:
        if data in selected_cities:
            selected_cities.remove(data)
        else:
            selected_cities.append(data)
        context.user_data['selected_cities'] = selected_cities
        keyboard = build_city_keyboard_with_done(selected_cities)
        selected_cities_str = ', '.join(selected_cities) if selected_cities else 'None'
        await query.edit_message_text(
            f"Selected cities: {selected_cities_str}\n\n"
            "Please select more cities or press 'Done' when finished.",
            reply_markup=keyboard
        )
        return CC_CITIES

async def compare_cities_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    month = update.message.text.strip()
    selected_cities = context.user_data.get('selected_cities', [])
    cities = ','.join(selected_cities)
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
