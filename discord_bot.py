# libraries
import discord
from discord.ext import tasks, commands
import logging
import os
import json
import datetime
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

# custom files
import data_pipeline

# class that collects and stores weather data every hour
class weather_data_collector:
    def __init__(self):
        self.header_fields = json.loads(os.getenv('HEADER_FIELDS'))
        self.field_names = json.loads(os.getenv('FIELD_NAMES'))

        self.observed_csv_file_names = json.loads(os.getenv('OBSERVED_CSV_FILES'))
        self.forecast_csv_file_names = json.loads(os.getenv('FORECAST_CSV_FILES'))
        self.observed_google_sheet_names = json.loads(os.getenv('OBSERVED_GOOGLE_SHEETS'))
        self.forecast_google_sheet_names = json.loads(os.getenv('FORECAST_GOOGLE_SHEETS'))

        self.locations = json.loads(os.getenv('LOCATIONS'))
        self.coordinates = json.loads(os.getenv('COORDINATES'))
        self.latest_observed_data = []
        pass

    def run_hourly_collection(self):
        self.latest_observed_data.clear()

        for (i, location) in enumerate(self.locations):
            # load data from the weather API
            api_instance = data_pipeline.api_data(self.coordinates[i], self.field_names)
            api_instance.load_api()

            # parse the forecast and observed weather data
            weather_parser_instance = data_pipeline.weather_parser(location, self.coordinates[i], self.field_names)
            weather_parser_instance.parse_forecast_weather_data(api_instance.api_data)
            weather_parser_instance.parse_observed_weather_data(api_instance.api_data)

            # store the forecast weather data in the CSV file
            forecast_csv_instance = data_pipeline.csv_storage(self.forecast_csv_file_names[i], location, self.coordinates[i], self.header_fields, self.field_names)
            forecast_csv_instance.initialize_csv_file()

            for row in weather_parser_instance.forecast_weather_data:
                forecast_csv_instance.add_record_to_csv_file(row)

            # store the forecast weather data in the Google sheet
            forecast_gs_instance = data_pipeline.google_sheet_storage(self.forecast_google_sheet_names[i], location, self.coordinates[i], self.header_fields, self.field_names)
            forecast_gs_instance.initialize_google_sheet()
            forecast_gs_instance.preload_existing_keys()

            for row in weather_parser_instance.forecast_weather_data:
                forecast_gs_instance.preload_records(row)

            forecast_gs_instance.add_records_to_google_sheet()

            # store the observed weather data in the CSV file
            observed_csv_instance = data_pipeline.csv_storage(self.observed_csv_file_names[i], location, self.coordinates[i], self.header_fields, self.field_names)
            observed_csv_instance.initialize_csv_file()

            for row in weather_parser_instance.observed_weather_data:
                observed_csv_instance.add_record_to_csv_file(row)

            # store the observed weather data in the Google sheet
            observed_gs_instance = data_pipeline.google_sheet_storage(self.observed_google_sheet_names[i], location, self.coordinates[i], self.header_fields, self.field_names)
            observed_gs_instance.initialize_google_sheet()
            observed_gs_instance.preload_existing_keys()

            for row in weather_parser_instance.observed_weather_data:
                observed_gs_instance.preload_records(row)

            observed_gs_instance.add_records_to_google_sheet()

            # save observed data for Discord bot
            self.latest_observed_data.append(weather_parser_instance.observed_weather_data[0])

        return self.latest_observed_data
    pass

# class that manages the Discord bot for weather predictions
class weather_predicting_discord_bot(commands.Bot):
    def __init__(self, weather_data_collector):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

        self.weather_data_collector = weather_data_collector
        self.discord_channel_ids = json.loads(os.getenv('DISCORD_CHANNEL_IDS'))
        self.latest_observed_data = []
        self.last_sent_date = None
        pass

    # start up the Discord bot
    async def on_ready(self):
        print(f"Logged in as {self.user}\n")

        # start the hourly weather data collection task
        if (not self.hourly_weather_collection.is_running()):
            self.hourly_weather_collection.start()

        # start the daily Discord update task
        if (not self.daily_discord_update.is_running()):
            self.daily_discord_update.start()
        pass

    # collect weather data every hour
    @tasks.loop(hours=1)
    #@tasks.loop(minutes=10)
    async def hourly_weather_collection(self):
        print(f"Running hourly weather data collection...\n")

        # collect latest weather data
        self.latest_observed_data = self.weather_data_collector.run_hourly_collection()
        pass

    # print weather data to Discord at 12:00 PM every day
    #@tasks.loop(minutes=10)
    @tasks.loop(time=datetime.time(hour=12, minute=0, second=0, tzinfo=ZoneInfo("America/Phoenix")))
    async def daily_discord_update(self):
        # check if the Discord message was already sent today
        today = datetime.date.today()
        if (self.last_sent_date == today):
            print(f"Discord daily update already sent today ({today}). Skipping...\n")
            return
        else:
            self.last_sent_date = today

        # check if there is latest data to send
        if (not self.latest_observed_data):
            self.latest_observed_data = self.weather_data_collector.run_hourly_collection()
        
        # prepare Discord message
        discord_message = (
            f"```\n"
            f"Daily Weather Update for {self.latest_observed_data[0][0]} at 12:00 PM (Phoenix, AZ time):\n"
            f"```\n"
        )

        # send Discord message to each channel
        for discord_channel_id in self.discord_channel_ids:
            discord_channel = self.get_channel(int(discord_channel_id)) or await self.fetch_channel(int(discord_channel_id))
            await discord_channel.send(discord_message)
        
        # prepare weather data for each city
        for city_data in self.latest_observed_data:
            discord_message = (
                f"```\n"
                f"\nHere is {city_data[3]} weather data for {city_data[0]} at {city_data[1]} hours:\n"
                f"Temperature: {city_data[4]} °F\n"
                f"Temperature Apparent: {city_data[5]} °F\n"
                f"Dew Point: {city_data[6]} °F\n"
                f"Humidity: {city_data[7]}%\n"
                f"Wind Speed: {city_data[8]} mph\n"
                f"Wind Direction: {city_data[9]}°\n"
                f"Wind Gust: {city_data[10]} mph\n"
                f"Pressure at Surface Level: {city_data[11]} inHg\n"
                f"Pressure at Sea Level: {city_data[12]} inHg\n"
                f"Precipitation Intensity: {city_data[13]} in/hr\n"
                f"Rain Intensity: {city_data[14]} in/hr\n"
                f"Freezing Rain Intensity: {city_data[15]} in/hr\n"
                f"Snow Intensity: {city_data[16]} in/hr\n"
                f"Sleet Intensity: {city_data[17]} in/hr\n"
                f"Precipitation Probability: {city_data[18]}%\n"
                f"Precipitation Type: {city_data[19]} (0 = No precipitation, 1 = Rain, 2 = Snow, 3 = Freezing rain, 4 = Ice pellets / sleet)\n"
                f"Rain Accumulation: {city_data[20]} in\n"
                f"Snow Accumulation: {city_data[21]} in\n"
                f"Snow Accumulation LWE: {city_data[22]} in of LWE\n"
                f"Snow Depth: {city_data[23]} in\n"
                f"Sleet Accumulation: {city_data[24]} in\n"
                f"Sleet Accumulation LWE: {city_data[25]} in of LWE\n"
                f"Ice Accumulation: {city_data[26]} in\n"
                f"Ice Accumulation LWE: {city_data[27]} in of LWE\n"
                f"Visibility: {city_data[28]} mi\n"
                f"Cloud Cover: {city_data[29]}%\n"
                f"Cloud Base: {city_data[30]} mi\n"
                f"Cloud Ceiling: {city_data[31]} mi\n"
                f"UV Index: {city_data[32]} (0-2: Low, 3-5: Moderate, 6-7: High, 8-10: Very High, 11+: Extreme)\n"
                f"UV Health Concern: {city_data[33]} (0-2: Low, 3-5: Moderate, 6-7: High, 8-10: Very High, 11+: Extreme)\n"
                f"Evapotranspiration: {city_data[34]} in\n"
                f"Thunderstorm Probability: {city_data[35]}%\n"
                f"EZ Heat Stress Index: {city_data[36]} (0-22: No Heat Stress 22-24: Mild Heat Stress 24-26: Moderate Heat Stress 26-28: Medium Heat Stress 28-30: Severe Heat Stress 30+: Extreme Heat Stress)\n"
                f"```"
            )

            # send Discord message to each channel
            for discord_channel_id in self.discord_channel_ids:
                discord_channel = self.get_channel(int(discord_channel_id)) or await self.fetch_channel(int(discord_channel_id))
                await discord_channel.send(discord_message)
        pass
    pass

# function that starts up the Discord bot
def main():
    # load environment variables from .env
    load_dotenv()

    print(datetime.datetime.now())
    print(datetime.datetime.now(datetime.timezone.utc))

    # retrieve the token from the .env file
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("DISCORD_TOKEN not set in .env. Aborting Discord bot startup.\n")
        return
    
    # configuring the Discord bot
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    wdc_instance = weather_data_collector()
    bot = weather_predicting_discord_bot(wdc_instance)
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)
    return