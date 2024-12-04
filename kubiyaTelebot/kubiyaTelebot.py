

import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters
)
from kubiyaTelebotConstants import (
    MP_CITY, MP_MONTH,
    BTM_CITY, BTM_MIN_TEMP, BTM_MAX_TEMP,
    CC_CITIES, CC_MONTH
)
from kubiyaTelebotHandlers import (
    start,
    help_command,
    cancel,
    monthly_profile_start,
    monthly_profile_city,
    monthly_profile_month,
    best_travel_month_start,
    best_travel_month_city,
    best_travel_month_min_temp,
    best_travel_month_max_temp,
    compare_cities_start,
    compare_cities_cities,
    compare_cities_month,
    metrics
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    application = ApplicationBuilder().token('7722882576:AAGgqizyGzvgTI8XBgEDbh924GpP_wpaiaU').build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('metrics', metrics))
    application.add_handler(CommandHandler('cancel', cancel))

    conv_handler_mp = ConversationHandler(
        entry_points=[CommandHandler('monthly_profile', monthly_profile_start)],
        states={
            MP_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, monthly_profile_city)],
            MP_MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, monthly_profile_month)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler_btm = ConversationHandler(
        entry_points=[CommandHandler('best_travel_month', best_travel_month_start)],
        states={
            BTM_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, best_travel_month_city)],
            BTM_MIN_TEMP: [MessageHandler(filters.TEXT & ~filters.COMMAND, best_travel_month_min_temp)],
            BTM_MAX_TEMP: [MessageHandler(filters.TEXT & ~filters.COMMAND, best_travel_month_max_temp)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler_cc = ConversationHandler(
        entry_points=[CommandHandler('compare_cities', compare_cities_start)],
        states={
            CC_CITIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, compare_cities_cities)],
            CC_MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, compare_cities_month)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler_mp)
    application.add_handler(conv_handler_btm)
    application.add_handler(conv_handler_cc)

    application.run_polling()

if __name__ == '__main__':
    main()
