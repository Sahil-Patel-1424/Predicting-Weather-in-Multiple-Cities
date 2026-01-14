import discord
from discord.ext import tasks, commands
import logging
import os
import json
import datetime
from dotenv import load_dotenv

import weather_predictor
import data_collection

def discord_bot_notification(cities_data, csv_flags, sheet_flags, program_start_flag):
    #print(csv_flags)
    #print(sheet_flags)

    # configuring the Discord bot
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    intents = discord.Intents.default()
    intents.message_content = True
    bot = discord.Client(intents=intents)
    CHANNEL_ID = os.getenv('CHANNEL_ID')
    CHANNEL_ID = json.loads(CHANNEL_ID)
    target_times = [
        datetime.time(hour=13, minute=0, second=0),  # 6:00 AM
        datetime.time(hour=19, minute=0, second=0),  # 12:00 PM
        datetime.time(hour=1, minute=0, second=0),   # 6:00 PM
        datetime.time(hour=4, minute=0, second=0)    # 9:00 PM
    ]
    #print(f"CHANNEL_ID: {CHANNEL_ID}\n")
    #print(f"CHANNEL: {channel}\n")

    # retrieve the token from the .env file
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("\nDISCORD_TOKEN not set in .env. Aborting Discord bot startup.\n")
        return

    # Discord bot events and commands
    @tasks.loop(time=target_times)
    async def scheduled_task():
        nonlocal cities_data, csv_flags, sheet_flags, program_start_flag
        #print(f"1")
        if (program_start_flag == True):
            # collecting data from the API
            cities_data = data_collection.api_request()

            # write the data to a CSV file
            csv_flags = data_collection.write_to_csv_file(cities_data)         # keeping this for local backup
            sheet_flags = data_collection.write_to_google_sheets(cities_data)  # using this instead since it's easier to manage an online spreadsheet

            #print(f"2")

        #print(f"3")

        for discord_channel in CHANNEL_ID:
            channel = bot.get_channel(discord_channel)

            if (channel is None):
                channel = await bot.fetch_channel(discord_channel)

            #print(f"4")

            for city_data in cities_data:
                # prepare message to send to Discord
                i = 0
                discord_message = (
                    f"```\n"
                    f"Here is {city_data[3]} weather data for {city_data[0]} at {city_data[1]} hours:\n"
                    f"Temperature: {city_data[4]} °F\n"
                    f"Dew Point: {city_data[5]} °F\n"
                    f"Humidity: {city_data[6]}%\n"
                    f"Wind Speed: {city_data[7]} mph\n"
                    f"Wind Direction: {city_data[8]}°\n"
                    f"Pressure at Sea Level: {city_data[9]} inHg\n"
                    f"Precipitation Intensity: {city_data[10]} in/hr\n"
                    f"Rain Intensity: {city_data[11]} in/hr\n"
                    f"Precipitation Probability: {city_data[12]}%\n"
                    f"Precipitation Type: {city_data[13]} (0 = No precipitation, 1 = Rain, 2 = Snow, 3 = Freezing rain, 4 = Ice pellets / sleet)\n"
                    f"Rain Accumulation: {city_data[14]} in\n"
                    f"Visibility: {city_data[15]} mi\n"
                    f"Cloud Cover: {city_data[16]}%\n"
                    f"Cloud Base: {city_data[17]} mi\n"
                    f"Cloud Ceiling: {city_data[18]} mi\n"
                    f"UV Index: {city_data[19]} (0-2: Low, 3-5: Moderate, 6-7: High, 8-10: Very High, 11+: Extreme)\n"
                    f"Evapotranspiration: {city_data[20]} in\n"
                    f"Thunderstorm Probability: {city_data[21]}%\n"
                    f"```"
                )

                discord_flags_message = (
                    f"```\n"
                    f"Data Recording Status for {city_data[3]} on {city_data[0]}:\n"
                    f"CSV File Recorded: {'Yes' if (csv_flags[i]) else 'No'}\n"
                    f"Google Sheets Recorded: {'Yes' if (sheet_flags[i]) else 'No'}\n"
                    f"```"
                )

                # send the Discord message
                if (channel):
                    await channel.send(discord_message)
                    await channel.send(discord_flags_message)
                else:
                    print(f"Channel not found. Unable to send Discord message.\n")

                i = i + 1

                #print(f"5")

        program_start_flag = True

        #print(f"6")

        # close the Discord bot after sending the message
        #await bot.close()

    @bot.event
    async def on_ready():
        if not scheduled_task.is_running():
            scheduled_task.start()
            print(f"\nWe have logged in as {bot.user}\n")
    
    # run the Discord bot
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)
    
    return