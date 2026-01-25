# libraries
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd

# class that manages storing data into Google sheets
class storing_into_google_sheets:
    def __init__(self, location, coordinates, field_names, header_fields, SPREADSHEET_ID, SERVICE_ACCOUNT_FILE):
        self.location = location
        self.coordinates = coordinates
        self.field_names = field_names
        self.header_fields = header_fields
        self.SPREADSHEET_ID = SPREADSHEET_ID
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        # establish connection to Google sheets API
        credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        client = gspread.authorize(credentials)
        self.workbook = client.open_by_key(self.SPREADSHEET_ID)
        pass

    # creates the Google sheet if it does not already exist
    def initialize_google_sheet(self, sheet_name):
        # check if the Google sheet for the location already exists
        for sheet in self.workbook.worksheets():
            if (sheet_name == sheet.title):
                print(f"{sheet_name} Google spreadsheet for {self.location} already exists. Ignoring entry...\n")
                return
            
        # create the Google sheet for the location
        worksheet = self.workbook.add_worksheet(title=sheet_name, rows="25000", cols=len(self.header_fields))
        worksheet.append_row(self.header_fields)
        print(f"Successfully created new {sheet_name} Google spreadsheet for {self.location}...\n")
        return

    # grabs data from a Google sheet
    def all_data(self, sheet_name):
        # check if the Google sheet for the location already exists
        sheet_data = None
        for sheet in self.workbook.worksheets():
            if (sheet_name == sheet.title):
                sheet_data = self.workbook.worksheet(sheet_name).get_all_values()
        #print(sheet_data)
        #print(type(sheet_data))    # list of lists
        return sheet_data
    
    # compare new data with existing data in the Google sheet
    def compare_data(self, weather_data, stored_data, sheet_name):
        i = 0
        stored_data_temp = stored_data[1:]      # exclude header row

        for weather_row in weather_data:
            weather_flag = False
            for stored_row in stored_data_temp:
                if (weather_row[0] == stored_row[0] and weather_row[1] == stored_row[1]):
                    print(f"({weather_row[0]} {weather_row[1]}) data has already been recorded in the {sheet_name} Google Sheet for {self.location}. Ignoring entry...\n")
                    weather_flag = True
            if (weather_flag == False):
                stored_data.append(weather_row)
            i = i + 1
        return stored_data
    
    # bubble sort algorithm for sorting data in the Google sheet
    def bubble_sort(self, data_frame, column, sheet_row_count):
        n = sheet_row_count - 1  # exclude header row

        for i in range(n):
            for j in range(0, n - i - 1):
                if (data_frame.iloc[j][column] > data_frame.iloc[j + 1][column]):
                    temp = data_frame.iloc[j]
                    data_frame.iloc[j] = data_frame.iloc[j + 1]
                    data_frame.iloc[j + 1] = temp
        return data_frame

    # prepares to store multiple weather data records into a Google sheet at once
    def sort_records(self, sheet_name, sheet_data):
        worksheet = self.workbook.worksheet(sheet_name)
        sheet_row_count = len(sheet_data)
        worksheet.clear()
        sheet_data[0] = self.header_fields

        df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
        df['DateTime'] = pd.to_datetime(df['Date (YYYY-MM-DD)'] + ' ' + df['Time (HH:MM:SS)'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        df = self.bubble_sort(df, 'DateTime', sheet_row_count)
        df = df.drop(columns=['DateTime'])   # remove temporary column
        
        # replace NaN with empty string and convert all values to strings to avoid JSON serialization errors
        sheet_data = [df.columns.values.tolist()] + df.fillna('').astype(str).values.tolist()
        worksheet.append_rows(sheet_data)
        pass

    pass