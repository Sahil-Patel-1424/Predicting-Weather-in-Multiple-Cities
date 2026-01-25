# libraries
import os
import json
import datetime
import ast
import time
import discord
from discord.ext import tasks, commands
import logging

# custom files
import api_pipeline
import weather_parser_pipeline
import csv_storage_pipeline
import gs_storage_pipeline
import discord_pipeline

# extract variables from variables.txt
def extract_txt_variables(file_name):
    variables = {}
    with open(file_name, mode='r', newline='', encoding='utf-8') as file:
        for line in file:
            if (('=' in line) and not (line.startswith('#'))):
                name, value = line.split('=', 1)
                name = name.strip()
                value = value.strip().strip("'").strip('"')

                # Use ast.literal_eval to safely parse lists or strings
                try:
                    variables[name] = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    variables[name] = value

    """"
    print(variables['API_KEY'])
    print("\n")
    print(variables['COORDINATES'])
    print("\n")
    print(variables['DISCORD_CHANNEL_IDS'])
    print("\n")
    print(variables['DISCORD_TOKEN'])
    print("\n")
    print(variables['FIELD_NAMES'])
    print("\n")
    print(variables['FORECAST_CSV_FILES'])
    print("\n")
    print(variables['FORECAST_GOOGLE_SHEETS'])
    print("\n")
    print(variables['HEADER_FIELDS'])
    print("\n")
    print(variables['LOCATIONS'])
    print("\n")
    print(variables['OBSERVED_CSV_FILES'])
    print("\n")
    print(variables['OBSERVED_GOOGLE_SHEETS'])
    print("\n")
    print(variables['SERVICE_ACCOUNT_FILE'])
    print("\n")
    print(variables['SPREADSHEET_ID'])
    print("\n")
    """
    return variables

# store the weather data from various locations into CSV files and Google sheets
def weather_data_storage():
    print(f"Starting to store weather data into CSV files and Google sheets...\n")

    # load in the variables before doing anything else
    variables = extract_txt_variables("variables.txt")
    API_KEY = variables['API_KEY']
    COORDINATES = variables['COORDINATES']
    DISCORD_CHANNELS = variables['DISCORD_CHANNEL_IDS']
    DISCORD_TOKEN = variables['DISCORD_TOKEN']
    FIELD_NAMES = variables['FIELD_NAMES']
    FORECAST_CSV_FILES = variables['FORECAST_CSV_FILES']
    FORECAST_GOOGLE_SHEETS = variables['FORECAST_GOOGLE_SHEETS']
    HEADER_FIELDS = variables['HEADER_FIELDS']
    LOCATIONS = variables['LOCATIONS']
    OBSERVED_CSV_FILES = variables['OBSERVED_CSV_FILES']
    OBSERVED_GOOGLE_SHEETS = variables['OBSERVED_GOOGLE_SHEETS']
    SERVICE_ACCOUNT_FILE = variables['SERVICE_ACCOUNT_FILE']
    SPREADSHEET_ID = variables['SPREADSHEET_ID']

    observed_messages = []
    
    # collect data from the API and store it
    
    # loop through each location
    for i in range(len(LOCATIONS)):
        print(f"Collecting data from tomorrow.io weather API for {LOCATIONS[i]}...\n")
        weather_api = api_pipeline.process_api_data(COORDINATES[i], FIELD_NAMES, API_KEY)
        weather_data = weather_api.collect_weather_data()

        print(f"Collecting historically observed data from the past 24 hours from tomorrow.io weather API for {LOCATIONS[i]}...\n")
        historical_weather_data = weather_api.collect_historically_observed_data()


        # parsing the weather data before storing it
        print(f"Parsing observed, historically observed, and forecasted weather data for {LOCATIONS[i]}...\n")
        weather_parser = weather_parser_pipeline.parse_weather_data(LOCATIONS[i], COORDINATES[i], FIELD_NAMES)
        observed_data, observed_message = weather_parser.parse_observed_weather_data(weather_data)
        historical_data = weather_parser.parse_historically_observed_weather_data(historical_weather_data)
        forecasted_data = weather_parser.parse_forecasted_weather_data(weather_data)
        observed_messages.append(observed_message)


        # store the data into the CSV files
        print(f"Storing and sorting the observed, historically observed, and forecasted weather data into CSV files for {LOCATIONS[i]}...\n")

        # store the observed data and historically observed data into a CSV file
        csv_storage = csv_storage_pipeline.data_management(LOCATIONS[i], COORDINATES[i], FIELD_NAMES, HEADER_FIELDS)
        csv_storage.initialize_csv_file(OBSERVED_CSV_FILES[i])
        csv_storage.add_record_to_csv_file(OBSERVED_CSV_FILES[i], observed_data)

        for row in historical_data:
            csv_storage.add_record_to_csv_file(OBSERVED_CSV_FILES[i], row)

        csv_storage.sort_csv_file(OBSERVED_CSV_FILES[i])

        
        # store the forecasted data into a CSV file
        csv_storage.initialize_csv_file(FORECAST_CSV_FILES[i])

        for row in forecasted_data:
            csv_storage.add_record_to_csv_file(FORECAST_CSV_FILES[i], row)

        csv_storage.sort_csv_file(FORECAST_CSV_FILES[i])


        # store the data into the Google sheets
        print(f"Storing the observed, historically observed, and forecasted weather data into Google Sheets for {LOCATIONS[i]}...\n")

        # store the observed data and historically observed data into a Google sheet
        gs_storage = gs_storage_pipeline.storing_into_google_sheets(LOCATIONS[i], COORDINATES[i], FIELD_NAMES, HEADER_FIELDS, SPREADSHEET_ID, SERVICE_ACCOUNT_FILE)
        gs_storage.initialize_google_sheet(OBSERVED_GOOGLE_SHEETS[i])

        observed_data = [observed_data]
        stored_observed_data = gs_storage.all_data(OBSERVED_GOOGLE_SHEETS[i])
        
        stored_observed_data = gs_storage.compare_data(observed_data, stored_observed_data, OBSERVED_GOOGLE_SHEETS[i])
        stored_observed_data = gs_storage.compare_data(historical_data, stored_observed_data, OBSERVED_GOOGLE_SHEETS[i])
        gs_storage.sort_records(OBSERVED_GOOGLE_SHEETS[i], stored_observed_data)


        # store the forecasted data into a Google sheet
        gs_storage.initialize_google_sheet(FORECAST_GOOGLE_SHEETS[i])
        stored_forecasted_data = gs_storage.all_data(FORECAST_GOOGLE_SHEETS[i])
        stored_forecasted_data = gs_storage.compare_data(forecasted_data, stored_forecasted_data, FORECAST_GOOGLE_SHEETS[i])
        gs_storage.sort_records(FORECAST_GOOGLE_SHEETS[i], stored_forecasted_data)


        # pause the loop for 1 minute before moving on to the next location to prevent API request error
        print(f"Successfully finished storing weather data for {LOCATIONS[i]}...\n")
        print(f"Waiting 1 minute before storing data for the next location (if any)...\n")
        time.sleep(60)

    print(f"Successfully finished storing weather data into CSV files and Google sheets...\n")
    
    return observed_messages

# function that starts up the project
def main():
    print(f"Starting Weather Predictor Project...\n")

    print(datetime.datetime.now())
    print(datetime.datetime.now(datetime.timezone.utc))
    print("\n")
    
    # starting up the Discord bot
    print(f"Starting the Discord bot...\n")
    variables = extract_txt_variables("variables.txt")
    DISCORD_CHANNELS = variables['DISCORD_CHANNEL_IDS']
    DISCORD_TOKEN = variables['DISCORD_TOKEN']
    LOCATIONS = variables['LOCATIONS']

    if (not DISCORD_TOKEN):
        print("Error: DISCORD_TOKEN is not set. Please set the DISCORD_TOKEN variable and try again.")
        return
    
    if (not DISCORD_CHANNELS):
        print("Error: DISCORD_CHANNEL_IDS is not set. Please set the DISCORD_CHANNEL_IDS variable and try again.")
        return
    
    if (not LOCATIONS):
        print("Error: LOCATIONS is not set. Please set the LOCATIONS variable and try again.")
        return

    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    discord_bot = discord_pipeline.weather_predicting_bot(DISCORD_TOKEN, DISCORD_CHANNELS, LOCATIONS)
    discord_bot.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)

    return

if __name__ == "__main__":
    main()