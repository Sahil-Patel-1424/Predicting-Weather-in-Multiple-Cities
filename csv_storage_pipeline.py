# libraries
import os
import csv
import pandas as pd

# class that stores weather data into CSV files
class data_management:
    def __init__(self, location, coordinates, field_names, header_fields):
        self.location = location
        self.coordinates = coordinates
        self.field_names = field_names
        self.header_fields = header_fields
        pass

    # creates the CSV file if it does not already exist
    def initialize_csv_file(self, file_name):
        # check if the CSV file does not exist and create it
        if (os.path.exists(file_name) == False):
            with open(file_name, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(self.header_fields)
                print(f"Successfully created new {file_name} CSV file for {self.location}...\n")
        else:
            print(f"{file_name} CSV file for {self.location} already exists. Ignoring entry...\n")

        pass

    # add the data record into the CSV file
    def add_record_to_csv_file(self, file_name, data_record):
        # check if the record already exists in the CSV file
        with open(file_name, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=',', quotechar='"')
            for row in reader:
                if (len(row) < 2):
                    continue
                if ((row[0] == data_record[0]) and (row[1] == data_record[1])):
                    print(f"({data_record[0]} {data_record[1]}) data has already been recorded in the {file_name} CSV file for {self.location}. Ignoring entry...\n")
                    return
                
        # add the record into the CSV file
        with open(file_name, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(data_record)
            print(f"Successfully added ({data_record[0]} {data_record[1]}) data into the {file_name} CSV file for {self.location}...\n")

        pass

    # counts the number of rows from the CSV file
    def count_rows_csv_file(self, file_name):
        with open(file_name, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=',', quotechar='"')
            row_count = sum(1 for row in reader)
        return row_count
    
    # bubble sort algorithm for sorting data in the CSV file
    def bubble_sort(self, data_frame, column, file_row_count):
        n = file_row_count - 1  # exclude header row

        for i in range(n):
            for j in range(0, n - i - 1):
                if (data_frame.iloc[j][column] > data_frame.iloc[j + 1][column]):
                    temp = data_frame.iloc[j]
                    data_frame.iloc[j] = data_frame.iloc[j + 1]
                    data_frame.iloc[j + 1] = temp
        return data_frame

    # sort the data in the CSV file by date and time
    def sort_csv_file(self, file_name):
        # read the CSV file into a pandas dataframe
        df = pd.read_csv(file_name)

        # check if there is enough data to sort
        file_row_count = self.count_rows_csv_file(file_name)
        if (file_row_count <= 2):
            print(f"Not enough data in the {file_name} CSV file for {self.location} to sort. Ignoring sorting...\n")
            return

        # convert the Date and Time columns into a single column and sort the data by that column
        df['DateTime'] = pd.to_datetime(df['Date (YYYY-MM-DD)'] + ' ' + df['Time (HH:MM:SS)'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        
        #df = df.sort_values(by=['DateTime'])
        df = self.bubble_sort(df, 'DateTime', file_row_count)
        df = df.drop(columns=['DateTime'])      # remove the temporary column
        df.to_csv(file_name, index=False)

        print(f"Successfully sorted the {file_name} CSV file for {self.location} by date and time...\n")

        pass

    pass