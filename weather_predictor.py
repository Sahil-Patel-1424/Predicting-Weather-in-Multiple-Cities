# libraries
from dotenv import load_dotenv

import data_collection
import discord_bot

global weather_data, csv_files, recorded_message, google_flag

def main():
    # load environment variables from .env
    load_dotenv()
    
    # collecting data from the API
    cities_data = data_collection.api_request()
    print(cities_data)

    # write the data to a CSV file
    csv_flags = data_collection.write_to_csv_file(cities_data)   # keeping this for local backup
    sheet_flags = data_collection.write_to_google_sheets(cities_data)         # using this instead since it's easier to manage an online spreadsheet

    # have Discord bot notify me when the weather data has been recorded
    program_start_flag = False
    discord_bot.discord_bot_notification(cities_data, csv_flags, sheet_flags, program_start_flag)
    
    return

if __name__ == "__main__":
    main()