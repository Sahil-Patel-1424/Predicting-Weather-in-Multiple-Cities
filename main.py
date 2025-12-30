# libraries
import requests
import json
import csv
import os

"""
url = "https://api.tomorrow.io/v4/weather/forecast?location=42.3478,-71.0466&apikey=wQD3N6cAJVBq3JiA7wx3woNJB845eueY"
headers = {
    "accept": "application/json"
}
response = requests.get(url, headers=headers)
print(response.json())
print("\n")
"""

"""
print("Weather Forecast")
print("==============================")
results = response.json()['data']['timelines'][0]['intervals']
for daily_result in results:
    date = daily_result['startTime'][0:10]
    temp = round(daily_result['values']['temperature'])
    print("On", date, "it will be:", temp, "F")
print("==============================\n")
"""


# To-Do list:
# 1. Create a script that automatically runs this program once per day
# 2. Have the script save the CSV file to GitHub repository
# 3. Use object-oriented programming to refactor the code
# 4. Use global variables to store API data to make it easier to access and use object-oriented programming
# 5. Use functions to modernize the code

def main():
    url = "https://api.tomorrow.io/v4/timelines"
    query = {
        "location": "33.464473, -112.166824",
        "fields": ["temperature", "dewPoint", "humidity", "windSpeed", "windDirection", "pressureSeaLevel", "precipitationIntensity", "rainIntensity", "precipitationProbability", "precipitationType", "rainAccumulation", "visibility", "cloudCover", "cloudBase", "cloudCeiling", "uvIndex", "evapotranspiration", "thunderstormProbability"],
        "units": "imperial",
        "timesteps": "1d",
        "apikey": ""
    }
    response = requests.request("GET", url, params = query)
    print(response.text)
    print("\n")

    # documentation of various features
    # https://docs.tomorrow.io/reference/welcome
    # https://docs.tomorrow.io/reference/data-layers-core   (this is the free tier)

    # gather the data from the API
    data = json.loads(response.text)

    # parse through the API data to extract today's information (they are already global variables)
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
    print(f"\nThe temperature in Phoenix today ({date}) at ({time}) hours is ({temperature}) degrees Fahrenheit with ({cloud_cover})% cloud cover\n")
    print(f"Here is the rest of today's ({date}) information at ({time}) hours:")
    print(f"Temperature: {temperature} degrees Fahrenheit")
    print(f"Dew Point: {dew_point} degrees Fahrenheit")
    print(f"Humidity: {humidity}%")
    print(f"Wind Speed: {wind_speed} mph")
    print(f"Wind Direction: {wind_direction} degrees")
    print(f"Pressure at Sea Level: {pressure_sea_level} inHg")
    print(f"Precipitation Intensity: {precipitation_intensity} in/hr")
    print(f"Rain Intensity: {rain_intensity} in/hr")
    print(f"Precipitation Probability: {precipitation_probability}%")
    print(f"Precipitation Type: {precipitation_type} (0 = No precipitation, 1 = Rain, 2, = Snow, 3 = Freezing rain, 4 = Ice pellets / sleet)")
    print(f"Rain Accumulation: {rain_accumulation} in")
    print(f"Visibility: {visibility} mi")
    print(f"Cloud Cover: {cloud_cover}%")
    print(f"Cloud Base: {cloud_base} mi")
    print(f"Cloud Ceiling: {cloud_ceiling} mi")
    print(f"UV Index: {uv_index} (0-2: Low, 3-5: Moderate, 6-7: High, 8-10: Very High, 11+: Extreme)")
    print(f"Evapotranspiration: {evapotranspiration} in")
    print(f"Thunderstorm Probability: {thunderstorm_probability}%")

    # check if the CSV file exists. else, create the CSV file.
    csv_file_path = 'phoenix_weather_data.csv'

    if (os.path.exists(csv_file_path) == False):
        # store the results in a CSV file
        with open(csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Date (YYYY-MM-DD)', 'Time (HH:MM:SS)', 'Temperature (F)', 'Dew Point (F)', 'Humidity (%)', 'Wind Speed (mph)', 'Wind Direction (degrees)', 'Pressure at Sea Level (inHg)', 'Precipitation Intensity (in/hr)', 'Rain Intensity (in/hr)', 'Precipitation Probability (%)', 'Precipitation Type', 'Rain Accumulation (in)', 'Visibility (mi)', 'Cloud Cover (%)', 'Cloud Base (mi)', 'Cloud Ceiling (mi)', 'UV Index', 'Evapotranspiration (in)', 'Thunderstorm Probability (%)'])
            writer.writerow([date, time, temperature, dew_point, humidity, wind_speed, wind_direction, pressure_sea_level, precipitation_intensity, rain_intensity, precipitation_probability, precipitation_type, rain_accumulation, visibility, cloud_cover, cloud_base, cloud_ceiling, uv_index, evapotranspiration, thunderstorm_probability])
            print(f"\nSuccessfully created new CSV file. Today's ({date}) data has been recorded in the CSV file.\n")
    else:
        # check if today's data has already been recorded. else, store today's data in the CSV file.
        recorded = False
        with open(csv_file_path, mode='r', newline='') as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in reader:
                if (row[0] == date):
                    recorded = True
                    print(f"\nToday's ({date}) data has already been recorded in the CSV file. Ignoring entry...\n")
                    break
        
        # check if today's data has not been recorded
        if (recorded == False):
            # store today's data in the CSV file
            with open(csv_file_path, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow([date, time, temperature, dew_point, humidity, wind_speed, wind_direction, pressure_sea_level, precipitation_intensity, rain_intensity, precipitation_probability, precipitation_type, rain_accumulation, visibility, cloud_cover, cloud_base, cloud_ceiling, uv_index, evapotranspiration, thunderstorm_probability])
                print(f"\nToday's ({date}) data has been recorded in the CSV file.\n")
        return
    
main()