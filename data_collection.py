import os
import requests
import json
import csv
import gspread
from google.oauth2.service_account import Credentials

import weather_predictor

def load_api(fields, coordinates):
    # grab the weather data from Tomorrow.io API
    url = "https://api.tomorrow.io/v4/timelines"
    API_KEY = os.getenv('API_KEY')
    query = {
        "location": coordinates,
        "fields": fields,
        "units": "imperial",
        "timesteps": "1d",
        "apikey": API_KEY
    }
    response = requests.request("GET", url, params = query)
    return response

def api_request():
    # documentation of various features
    # https://docs.tomorrow.io/reference/welcome
    # https://docs.tomorrow.io/reference/data-layers-core   (this is the free tier)

    # list of fields to request from the API
    fields = ['temperature', 'dewPoint', 'humidity', 'windSpeed', 'windDirection', 'pressureSeaLevel', 'precipitationIntensity', 'rainIntensity', 'precipitationProbability', 'precipitationType', 'rainAccumulation', 'visibility', 'cloudCover', 'cloudBase', 'cloudCeiling', 'uvIndex', 'evapotranspiration', 'thunderstormProbability']

    # grab the weather data from Tomorrow.io API
    COORDINATES = os.getenv('COORDINATES')
    COORDINATES = json.loads(COORDINATES)
    LOCATIONS = os.getenv('LOCATIONS')
    LOCATIONS = json.loads(LOCATIONS)
    #print(COORDINATES)
    #print(COORDINATES[0])

    #responses = []
    cities_data = []
    i = 0

    for coordinates in COORDINATES:
        response = load_api(fields, coordinates)
        print(response.text)
        #responses.append(response)
    
        #response = load_api(fields, COORDINATES[0])
        #print(response.text)
        #print("\n")

        # gather the data from the API
        data = json.loads(response.text)

        # parse through the API data to extract today's information
        interval = data['data']['timelines'][0]['intervals'][0]
        start_time = interval.get('startTime', '')
        date = start_time[0:10]
        time = start_time[11:19]
        values = interval.get('values', {})
        weather_data = [date, time, coordinates, LOCATIONS[i]]

        for key in fields:
            #print(values.get(key))
            weather_data.append(values.get(key))

        cities_data.append(weather_data)

        # print out the results
        #print(weather_data)
        message = (
            f"\nThe temperature in {weather_data[3]} today ({weather_data[0]}) at ({time}) hours is ({weather_data[4]}) degrees Fahrenheit with ({weather_data[15]})% cloud cover\n\n"
            f"Here is the rest of today's ({weather_data[0]}) information at ({weather_data[1]}) hours:\n"
            f"Temperature: {weather_data[4]} degrees Fahrenheit\n"
            f"Dew Point: {weather_data[5]} degrees Fahrenheit\n"
            f"Humidity: {weather_data[6]}%\n"
            f"Wind Speed: {weather_data[7]} mph\n"
            f"Wind Direction: {weather_data[8]} degrees\n"
            f"Pressure at Sea Level: {weather_data[9]} inHg\n"
            f"Precipitation Intensity: {weather_data[10]} in/hr\n"
            f"Rain Intensity: {weather_data[10]} in/hr\n"
            f"Precipitation Probability: {weather_data[11]}%\n"
            f"Precipitation Type: {weather_data[12]} (0 = No precipitation, 1 = Rain, 2 = Snow, 3 = Freezing rain, 4 = Ice pellets / sleet)\n"
            f"Rain Accumulation: {weather_data[13]} in\n"
            f"Visibility: {weather_data[14]} mi\n"
            f"Cloud Cover: {weather_data[15]}%\n"
            f"Cloud Base: {weather_data[16]} mi\n"
            f"Cloud Ceiling: {weather_data[17]} mi\n"
            f"UV Index: {weather_data[18]} (0-2: Low, 3-5: Moderate, 6-7: High, 8-10: Very High, 11+: Extreme)\n"
            f"Evapotranspiration: {weather_data[19]} in\n"
            f"Thunderstorm Probability: {weather_data[20]}%\n"
        )
        print(message)

        # go to the next city
        i = i + 1

    return cities_data

def write_to_csv_file(cities_data):
    CSV_FILES = os.getenv('CSV_FILES')
    CSV_FILES = json.loads(CSV_FILES)
    csv_flags = [False] * len(CSV_FILES)
    i = 0

    for csv_file in CSV_FILES:
        # check if the CSV file does not exist
        #print(csv_file)
        if (os.path.exists(csv_file) == False):
            # store today's data in the CSV file
            with open(csv_file, mode='w', newline='') as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(['Date (YYYY-MM-DD)', 'Time (HH:MM:SS)', 'Coordinates', 'Location', 'Temperature (F)', 'Dew Point (F)', 'Humidity (%)', 'Wind Speed (mph)', 'Wind Direction (degrees)', 'Pressure at Sea Level (inHg)', 'Precipitation Intensity (in/hr)', 'Rain Intensity (in/hr)', 'Precipitation Probability (%)', 'Precipitation Type', 'Rain Accumulation (in)', 'Visibility (mi)', 'Cloud Cover (%)', 'Cloud Base (mi)', 'Cloud Ceiling (mi)', 'UV Index', 'Evapotranspiration (in)', 'Thunderstorm Probability (%)'])
                writer.writerow(cities_data[i])
                print(f"Successfully created new CSV file: {csv_file}. {cities_data[i][0]} data has been recorded in the {csv_file} file.\n")
                csv_flags[i] = True
        # else, write to the existing CSV file
        else:
            # check if today's data has already been recorded. else, store today's data in the CSV files.
            recorded = False
            with open(csv_file, mode='r', newline='') as file:
                reader = csv.reader(file, delimiter=',', quotechar='"')
                for row in reader:
                    if (row[0] == cities_data[i][0]):
                        recorded = True
                        print(f"{cities_data[i][0]} data has already been recorded in the {csv_file} file. Ignoring entry...\n")
                        csv_flags[i] = True
                        break

            # check if today's data has not been recorded
            if (recorded == False):
                # store today's data in the CSV file
                with open(csv_file, mode='a', newline='') as file:
                    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(cities_data[i])
                    print(f"{cities_data[i][0]} data has been recorded in the {csv_file} file.\n")
                    csv_flags[i] = True
        
        i = i + 1

    return csv_flags

def write_to_google_sheets(cities_data):
    # google sheets API setup
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    # open google sheet by sheet ID
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    #sheet = client.open_by_key(SHEET_ID)
    #values_list = sheet.sheet1.row_values(1)
    #print(values_list)
    workbook = client.open_by_key(SPREADSHEET_ID)
    SHEET_ID = os.getenv('WORKSHEETS')
    SHEET_ID = json.loads(SHEET_ID)
    sheet_flags = [False] * len(SHEET_ID)
    i = 0
    #print(workbook)

    for sheet in SHEET_ID:
        worksheet = workbook.worksheet(sheet)

        # check if header row exists and add it into spreadsheet if it doesn't exist
        header_row = ['Date (YYYY-MM-DD)', 'Time (HH:MM:SS)', 'Coordinates', 'Location', 'Temperature (F)', 'Dew Point (F)', 'Humidity (%)', 'Wind Speed (mph)', 'Wind Direction (degrees)', 'Pressure at Sea Level (inHg)', 'Precipitation Intensity (in/hr)', 'Rain Intensity (in/hr)', 'Precipitation Probability (%)', 'Precipitation Type', 'Rain Accumulation (in)', 'Visibility (mi)', 'Cloud Cover (%)', 'Cloud Base (mi)', 'Cloud Ceiling (mi)', 'UV Index', 'Evapotranspiration (in)', 'Thunderstorm Probability (%)']
        existing_header = worksheet.row_values(1)
        if (existing_header != header_row):
            worksheet.insert_row(header_row, 1)
            print(f"Header row added to {sheet} Sheet.\n")
        else:
            print(f"Header row already exists in {sheet} Sheet. Ignoring entry...\n")

        # # check if today's data was appended to the spreadsheet, if not then append it
        existing_dates = worksheet.col_values(1)
        if (cities_data[i][0] in existing_dates):
            print(f"{cities_data[i][0]} data in {cities_data[i][3]} already exists in {sheet} Sheet. Ignoring entry...\n")
            sheet_flags[i] = True
        else:
            worksheet.append_row(cities_data[i])
            print(f"{cities_data[i][0]} data in {cities_data[i][3]} has been written to {sheet} Sheet.\n")
            sheet_flags[i] = True

        i = i + 1

    return sheet_flags