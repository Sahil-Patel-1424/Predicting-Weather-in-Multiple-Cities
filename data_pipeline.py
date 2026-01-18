# libraries
import os
import requests
import json
import csv
import gspread
from google.oauth2.service_account import Credentials

# class that manages API data requests
class api_data:
    def __init__(self, coordinates, field_names):
        self.coordinates = coordinates
        self.field_names = field_names
        self.api_data = None
        pass

    # grab the weather data from Tomorrow.io API
    def load_api(self):
        # tomorrow.io API setup
        url = "https://api.tomorrow.io/v4/timelines"
        API_KEY = os.getenv('API_KEY')

        query = requests.get(url, params={
            "location": self.coordinates,
            "fields": self.field_names,
            "units": "imperial",
            "timesteps": "1h",
            "apikey": API_KEY
        })

        ### FOR DEBUGGING PURPOSES ONLY. COMMENT OUT WHEN NOT IN PRODUCTION. ###
        print(f"API Status: {query.status_code}\n")
        print(f"API Response: {query.text}\n")

        self.api_data = query.json()

        """
        query = {
            "location": self.coordinates,
            "fields": self.field_names,
            "units": "imperial",
            "timesteps": "1h",
            "apikey": API_KEY
        }

        self.api_data = requests.request("GET", url, params = query)
        self.api_data = json.loads(self.api_data.text)
        ###"""
        pass
    pass

# class that parses weather data from API response
class weather_parser:
    def __init__(self, location, coordinates, field_names):
        self.location = location
        self.coordinates = coordinates
        self.field_names = field_names
        self.forecast_weather_data = []
        self.observed_weather_data = []
        pass

    # grab the forcasted hourly weather data from the API response
    def parse_forecast_weather_data(self, api_data):
        # parse through the API data to extract hourly information
        interval = api_data['data']['timelines'][0]['intervals']
        weather_data = []

        # go through each hourly forecast and store the data
        for hour in interval:
            start_time = hour.get('startTime', '')
            date = start_time[0:10]
            time = start_time[11:19]
            values = hour.get('values', {})
            weather_data = [date, time, self.coordinates, self.location]

            for key in self.field_names:
                weather_data.append(values.get(key))

            self.forecast_weather_data.append(weather_data)

        pass
        
    # grab the observed hourly weather data from the API response
    def parse_observed_weather_data(self, api_data):
        # parse through the API data to extract hourly information
        interval = api_data['data']['timelines'][0]['intervals'][0]
        start_time = interval.get('startTime', '')
        date = start_time[0:10]
        time = start_time[11:19]
        values = interval.get('values', {})
        weather_data = [date, time, self.coordinates, self.location]

        # go through each field and store the data
        for key in self.field_names:
            weather_data.append(values.get(key))

        self.observed_weather_data.append(weather_data)

        # print out the observed weather data
        message = (
            f"\nHere is ({weather_data[3]}) weather data for ({weather_data[0]}) at ({weather_data[1]}) hours:\n"
            f"Temperature: {weather_data[4]} °F\n"
            f"Temperature Apparent: {weather_data[5]} °F\n"
            f"Dew Point: {weather_data[6]} °F\n"
            f"Humidity: {weather_data[7]}%\n"
            f"Wind Speed: {weather_data[8]} mph\n"
            f"Wind Direction: {weather_data[9]}°\n"
            f"Wind Gust: {weather_data[10]} mph\n"
            f"Pressure at Surface Level: {weather_data[11]} inHg\n"
            f"Pressure at Sea Level: {weather_data[12]} inHg\n"
            f"Precipitation Intensity: {weather_data[13]} in/hr\n"
            f"Rain Intensity: {weather_data[14]} in/hr\n"
            f"Freezing Rain Intensity: {weather_data[15]} in/hr\n"
            f"Snow Intensity: {weather_data[16]} in/hr\n"
            f"Sleet Intensity: {weather_data[17]} in/hr\n"
            f"Precipitation Probability: {weather_data[18]}%\n"
            f"Precipitation Type: {weather_data[19]} (0 = No precipitation, 1 = Rain, 2 = Snow, 3 = Freezing rain, 4 = Ice pellets / sleet)\n"
            f"Rain Accumulation: {weather_data[20]} in\n"
            f"Snow Accumulation: {weather_data[21]} in\n"
            f"Snow Accumulation LWE: {weather_data[22]} in of LWE\n"
            f"Snow Depth: {weather_data[23]} in\n"
            f"Sleet Accumulation: {weather_data[24]} in\n"
            f"Sleet Accumulation LWE: {weather_data[25]} in of LWE\n"
            f"Ice Accumulation: {weather_data[26]} in\n"
            f"Ice Accumulation LWE: {weather_data[27]} in of LWE\n"
            f"Visibility: {weather_data[28]} mi\n"
            f"Cloud Cover: {weather_data[29]}%\n"
            f"Cloud Base: {weather_data[30]} mi\n"
            f"Cloud Ceiling: {weather_data[31]} mi\n"
            f"UV Index: {weather_data[32]} (0-2: Low, 3-5: Moderate, 6-7: High, 8-10: Very High, 11+: Extreme)\n"
            f"UV Health Concern: {weather_data[33]} (0-2: Low, 3-5: Moderate, 6-7: High, 8-10: Very High, 11+: Extreme)\n"
            f"Evapotranspiration: {weather_data[34]} in\n"
            f"Thunderstorm Probability: {weather_data[35]}%\n"
            f"EZ Heat Stress Index: {weather_data[36]} (0-22: No Heat Stress 22-24: Mild Heat Stress 24-26: Moderate Heat Stress 26-28: Medium Heat Stress 28-30: Severe Heat Stress 30+: Extreme Heat Stress)\n"
        )
        print(message)
        pass
    pass

# class that manages and save weather data records to various CSV files
class csv_storage:
    def __init__(self, file_name, location, coordinates, header_fields, field_names):
        self.file_name = file_name
        self.location = location
        self.coordinates = coordinates
        self.header_fields = header_fields
        self.field_names = field_names
        pass

    # creates the CSV file with headers if it doesn't exist
    def initialize_csv_file(self):
        # check if file does not exist and create it
        if (os.path.exists(self.file_name) == False):
            with open(self.file_name, mode='w', newline='') as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(self.header_fields)
                print(f"Successfully created new {self.file_name} CSV file for {self.location}.\n")
        # if file already exists then do nothing
        else:
            print(f"{self.file_name} CSV file for {self.location} already exists. Ignoring entry...\n")
        pass

    # add record to CSV file
    def add_record_to_csv_file(self, record):
        # first check if record already exists
        with open(self.file_name, mode='r', newline='') as file:
            reader = csv.reader(file, delimiter=',', quotechar='"')
            for row in reader:
                if ((row[0] == record[0]) and (row[1] == record[1])):
                    print(f"({record[0]} {record[1]}) data has already been recorded in the {self.file_name} file. Ignoring entry...\n")
                    return
                
        # add record
        with open(self.file_name, mode='a', newline='') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(record)
            print(f"({record[0]} {record[1]}) data has been recorded in the {self.file_name} file.\n")
        pass
    
    pass

# class that manages and save weather data records to various Google sheets
class google_sheet_storage:
    def __init__(self, sheet_name, location, coordinates, header_fields, field_names):
        self.sheet_name = sheet_name
        self.location = location
        self.coordinates = coordinates
        self.header_fields = header_fields
        self.field_names = field_names
        self.workbook = None
        self.worksheet = None
        self.existing_keys = None
        self.pending_records = []
        pass

    # creates the Google sheet with headers if it doesn't exist
    def initialize_google_sheet(self):
        # google sheets API setup
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
        self.workbook = client.open_by_key(SPREADSHEET_ID)
        
        # stop creating the sheet if it already exists
        for sheet in self.workbook.worksheets():
            if (self.sheet_name == sheet.title):
                print(f"{self.sheet_name} Google Sheet for {self.location} already exists. Ignoring entry...\n")
                return
        
        # create the Google sheet
        self.worksheet = self.workbook.add_worksheet(title=self.sheet_name, rows=25000, cols=len(self.header_fields))
        self.worksheet.insert_row(self.header_fields, 1)
        print(f"Successfully created new {self.sheet_name} Google Sheet for {self.location}.\n")
        pass

    # preload existing keys from Google sheet
    def preload_existing_keys(self):
        self.worksheet = self.workbook.worksheet(self.sheet_name)
        rows = self.worksheet.get_all_values()
        self.existing_keys = set(f"{row[0]}_{row[1]}" for row in rows[1:])  # skip header row
        pass

    # preload records for mass appending in Google sheet
    def preload_records(self, record):
        # first check if record already exists
        key = f"{record[0]}_{record[1]}"
        if (key in self.existing_keys):
            print(f"({record[0]} {record[1]}) data has already been recorded in the {self.sheet_name} Google Sheet. Ignoring entry...\n")
            return
        
        # preload the record
        self.existing_keys.add(key)
        self.pending_records.append(record)
        pass

    # add records to Google sheet
    def add_records_to_google_sheet(self):
        # first check if there are any pending records to add
        if (len(self.pending_records) == 0):
            print(f"No new records to add to the {self.sheet_name} Google Sheet. Ignoring entry...\n")
            return
        
        # add records
        self.worksheet.append_rows(self.pending_records, value_input_option='RAW')

        # clear pending records
        print(f"{len(self.pending_records)} new records from ({self.pending_records[0][0]} {self.pending_records[0][1]}) to ({self.pending_records[-1][0]} {self.pending_records[-1][1]}) have been recorded in the {self.sheet_name} Google Sheet.\n")
        self.pending_records.clear()
        pass
    pass