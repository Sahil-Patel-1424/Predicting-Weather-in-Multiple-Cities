# libraries
import requests
import json
import csv
import os
import discord
from dotenv import load_dotenv
import logging
from discord.ext import tasks, commands

def discord_bot_notification():
    # prepare the Discord message
    discord_message = (
        f"\nThe temperature in Phoenix (at the State Farm Stadium) today (**{date}**) at **{time}** hours is **{temperature}** °F with **{cloud_cover}%** cloud cover\n\n"
        f"__Here is the rest of today's (**{date}**) information at **{time}** hours:__\n"
        f"**Temperature:** {temperature} °F\n"
        f"**Dew Point:** {dew_point} °F\n"
        f"**Humidity:** {humidity}%\n"
        f"**Wind Speed:** {wind_speed} mph\n"
        f"**Wind Direction:** {wind_direction}°\n"
        f"**Pressure at Sea Level:** {pressure_sea_level} inHg\n"
        f"**Precipitation Intensity:** {precipitation_intensity} in/hr\n"
        f"**Rain Intensity:** {rain_intensity} in/hr\n"
        f"**Precipitation Probability:** {precipitation_probability}%\n"
        f"**Precipitation Type:** {precipitation_type} (0 = No precipitation, 1 = Rain, 2 = Snow, 3 = Freezing rain, 4 = Ice pellets / sleet)\n"
        f"**Rain Accumulation:** {rain_accumulation} in\n"
        f"**Visibility:** {visibility} mi\n"
        f"**Cloud Cover:** {cloud_cover}%\n"
        f"**Cloud Base:** {cloud_base} mi\n"
        f"**Cloud Ceiling:** {cloud_ceiling} mi\n"
        f"**UV Index:** {uv_index} (0-2: Low, 3-5: Moderate, 6-7: High, 8-10: Very High, 11+: Extreme)\n"
        f"**Evapotranspiration:** {evapotranspiration} in\n"
        f"**Thunderstorm Probability:** {thunderstorm_probability}%"
    )

    discord_csv_message = recorded_message.format(date_text=date)

    # configuring the Discord bot
    load_dotenv()
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    intents = discord.Intents.default()
    intents.message_content = True
    bot = discord.Client(intents=intents)
    CHANNEL_ID = os.getenv('CHANNEL_ID')
    #print(f"CHANNEL_ID: {CHANNEL_ID}\n")
    #print(f"CHANNEL: {channel}\n")

    # Discord bot events and commands
    @bot.event
    @tasks.loop(hours=6)
    async def on_ready():
        print(f"\nWe have logged in as {bot.user}\n")

        channel = bot.get_channel(CHANNEL_ID)

        if (channel is None):
            channel = await bot.fetch_channel(CHANNEL_ID)

        # send the Discord message
        #message.channel.send(discord_message)
        #message.channel.send(discord_csv_message)
        if (channel):
            await channel.send(discord_message)
            await channel.send(discord_csv_message)
        else:
            print("Channel not found. Unable to send Discord message.\n")

        # close the Discord bot after sending the message
        await bot.close()

    # retrieve the token from the .env file
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("\nDISCORD_TOKEN not set in .env. Aborting Discord bot startup.\n")
        return
    
    # run the Discord bot
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)

    return

def write_to_csv_file():
    global csv_file_path, recorded_message
    csv_file_path = 'phoenix_weather_data.csv'

    # check if the CSV file exists. else, create the CSV file.
    if (os.path.exists(csv_file_path) == False):
        # store the results in a CSV file
        with open(csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Date (YYYY-MM-DD)', 'Time (HH:MM:SS)', 'Temperature (F)', 'Dew Point (F)', 'Humidity (%)', 'Wind Speed (mph)', 'Wind Direction (degrees)', 'Pressure at Sea Level (inHg)', 'Precipitation Intensity (in/hr)', 'Rain Intensity (in/hr)', 'Precipitation Probability (%)', 'Precipitation Type', 'Rain Accumulation (in)', 'Visibility (mi)', 'Cloud Cover (%)', 'Cloud Base (mi)', 'Cloud Ceiling (mi)', 'UV Index', 'Evapotranspiration (in)', 'Thunderstorm Probability (%)'])
            writer.writerow([date, time, temperature, dew_point, humidity, wind_speed, wind_direction, pressure_sea_level, precipitation_intensity, rain_intensity, precipitation_probability, precipitation_type, rain_accumulation, visibility, cloud_cover, cloud_base, cloud_ceiling, uv_index, evapotranspiration, thunderstorm_probability])
            recorded_message = "Successfully created new CSV file. Today's ({date_text}) data in Phoenix (at the State Farm Stadium) has been recorded in the CSV file."
            #print("\n")
            print(recorded_message.format(date_text=date))
            #print("\n")
    else:
        # check if today's data has already been recorded. else, store today's data in the CSV file.
        recorded = False
        with open(csv_file_path, mode='r', newline='') as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in reader:
                if (row[0] == date):
                    recorded = True
                    recorded_message = "Today's ({date_text}) data in Phoenix (at the State Farm Stadium) has already been recorded in the CSV file. Ignoring entry..."
                    #print("\n")
                    print(recorded_message.format(date_text=date))
                    #print("\n")
                    break
        
        # check if today's data has not been recorded
        if (recorded == False):
            # store today's data in the CSV file
            with open(csv_file_path, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow([date, time, temperature, dew_point, humidity, wind_speed, wind_direction, pressure_sea_level, precipitation_intensity, rain_intensity, precipitation_probability, precipitation_type, rain_accumulation, visibility, cloud_cover, cloud_base, cloud_ceiling, uv_index, evapotranspiration, thunderstorm_probability])
                recorded_message = "Today's ({date_text}) data in Phoenix (at the State Farm Stadium) has been recorded in the CSV file."
                #print("\n")
                print(recorded_message.format(date_text=date))
                #print("\n")
    return

def api_request():
    # documentation of various features
    # https://docs.tomorrow.io/reference/welcome
    # https://docs.tomorrow.io/reference/data-layers-core   (this is the free tier)

    # grab the weather data from Tomorrow.io API
    url = "https://api.tomorrow.io/v4/timelines"
    API_KEY = os.getenv('API_KEY')
    query = {
        "location": "33.527283, -112.263275",   # State Farm Stadium coordinates
        "fields": ["temperature", "dewPoint", "humidity", "windSpeed", "windDirection", "pressureSeaLevel", "precipitationIntensity", "rainIntensity", "precipitationProbability", "precipitationType", "rainAccumulation", "visibility", "cloudCover", "cloudBase", "cloudCeiling", "uvIndex", "evapotranspiration", "thunderstormProbability"],
        "units": "imperial",
        "timesteps": "1d",
        "apikey": API_KEY
    }
    response = requests.request("GET", url, params = query)
    print(response.text)
    #print("\n")

    # gather the data from the API
    data = json.loads(response.text)

    # parse through the API data to extract today's information (they are already global variables)
    global date, time, temperature, dew_point, humidity, wind_speed, wind_direction, pressure_sea_level, precipitation_intensity, rain_intensity, precipitation_probability, precipitation_type, rain_accumulation, visibility, cloud_cover, cloud_base, cloud_ceiling, uv_index, evapotranspiration, thunderstorm_probability
    date = data['data']['timelines'][0]['intervals'][0]['startTime'][0:10]                                          # YYYY-MM-DD
    time = data['data']['timelines'][0]['intervals'][0]['startTime'][11:19]                                         # HH:MM:SS (24-hour clock)
    temperature = data['data']['timelines'][0]['intervals'][0]['values']['temperature']                             # degrees Fahrenheit
    dew_point = data['data']['timelines'][0]['intervals'][0]['values']['dewPoint']                                  # degrees Fahrenheit
    humidity = data['data']['timelines'][0]['intervals'][0]['values']['humidity']                                   # percentage (%)
    wind_speed = data['data']['timelines'][0]['intervals'][0]['values']['windSpeed']                                # miles per hour (mph)
    wind_direction = data['data']['timelines'][0]['intervals'][0]['values']['windDirection']                        # degrees (0-360)
    pressure_sea_level = data['data']['timelines'][0]['intervals'][0]['values']['pressureSeaLevel']                 # inches of mercury (inHg)
    precipitation_intensity = data['data']['timelines'][0]['intervals'][0]['values']['precipitationIntensity']      # inches per hour (in/hr)
    rain_intensity = data['data']['timelines'][0]['intervals'][0]['values']['rainIntensity']                        # inches per hour (in/hr)
    precipitation_probability = data['data']['timelines'][0]['intervals'][0]['values']['precipitationProbability']  # percentage (%)
    precipitation_type = data['data']['timelines'][0]['intervals'][0]['values']['precipitationType']                # 0 = No precipitation, 1 = Rain, 2, = Snow, 3 = Freezing rain, 4 = Ice pellets / sleet
    rain_accumulation = data['data']['timelines'][0]['intervals'][0]['values']['rainAccumulation']                  # inches (in)
    visibility = data['data']['timelines'][0]['intervals'][0]['values']['visibility']                               # miles (mi)
    cloud_cover = data['data']['timelines'][0]['intervals'][0]['values']['cloudCover']                              # percentage (%)
    cloud_base = data['data']['timelines'][0]['intervals'][0]['values']['cloudBase']                                # miles (mi)
    cloud_ceiling = data['data']['timelines'][0]['intervals'][0]['values']['cloudCeiling']                          # miles (mi)
    uv_index = data['data']['timelines'][0]['intervals'][0]['values']['uvIndex']                                    # 0-2: Low, 3-5: Moderate, 6-7: High, 8-10: Very High, 11+: Extreme
    evapotranspiration = data['data']['timelines'][0]['intervals'][0]['values']['evapotranspiration']               # inches (in)
    thunderstorm_probability = data['data']['timelines'][0]['intervals'][0]['values']['thunderstormProbability']    # percentage(%)

    # print out the results
    message = (
        f"\nThe temperature in Phoenix (at the State Farm Stadium) today ({date}) at ({time}) hours is ({temperature}) degrees Fahrenheit with ({cloud_cover})% cloud cover\n\n"
        f"Here is the rest of today's ({date}) information at ({time}) hours:\n"
        f"Temperature: {temperature} degrees Fahrenheit\n"
        f"Dew Point: {dew_point} degrees Fahrenheit\n"
        f"Humidity: {humidity}%\n"
        f"Wind Speed: {wind_speed} mph\n"
        f"Wind Direction: {wind_direction} degrees\n"
        f"Pressure at Sea Level: {pressure_sea_level} inHg\n"
        f"Precipitation Intensity: {precipitation_intensity} in/hr\n"
        f"Rain Intensity: {rain_intensity} in/hr\n"
        f"Precipitation Probability: {precipitation_probability}%\n"
        f"Precipitation Type: {precipitation_type} (0 = No precipitation, 1 = Rain, 2 = Snow, 3 = Freezing rain, 4 = Ice pellets / sleet)\n"
        f"Rain Accumulation: {rain_accumulation} in\n"
        f"Visibility: {visibility} mi\n"
        f"Cloud Cover: {cloud_cover}%\n"
        f"Cloud Base: {cloud_base} mi\n"
        f"Cloud Ceiling: {cloud_ceiling} mi\n"
        f"UV Index: {uv_index} (0-2: Low, 3-5: Moderate, 6-7: High, 8-10: Very High, 11+: Extreme)\n"
        f"Evapotranspiration: {evapotranspiration} in\n"
        f"Thunderstorm Probability: {thunderstorm_probability}%\n"
    )
    print(message)

    return

def main():
    # collecting data from the API and storing it in a CSV file
    api_request()
    write_to_csv_file()

    # have Discord bot notify me when the weather data has been recorded
    discord_bot_notification()

    return
    
main()