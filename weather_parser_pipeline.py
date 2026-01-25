# libraries

# class that parses weather data from the API
class parse_weather_data:
    def __init__(self, location, coordinates, field_names):
        self.location = location
        self.coordinates = coordinates
        self.field_names = field_names
        pass

    # collect the observed weather data
    def parse_observed_weather_data(self, observed_data):
        # initialize variables
        interval = observed_data['data']['timelines'][0]['intervals'][0]
        start_time = interval.get('startTime', '')
        date = start_time[0:10]
        time = start_time[11:19]
        weather_values = interval.get('values', {})
        parsed_data = [date, time, self.location, self.coordinates]

        # go through each field and collect the corresponding data
        for field in self.field_names:
            value = weather_values.get(field, '')
            parsed_data.append(value)

        #print(parsed_data)
        message = (
            f"Here is {parsed_data[2]} weather data for ({parsed_data[0]}) at ({parsed_data[1]}) hours:\n"
            f"Temperature: {parsed_data[4]} °F\n"
            f"Temperature Apparent: {parsed_data[5]} °F\n"
            f"Dew Point: {parsed_data[6]} °F\n"
            f"Humidity: {parsed_data[7]}%\n"
            f"Wind Speed: {parsed_data[8]} mph\n"
            f"Wind Direction: {parsed_data[9]}°\n"
            f"Wind Gust: {parsed_data[10]} mph\n"
            f"Pressure at Surface Level: {parsed_data[11]} inHg\n"
            f"Pressure at Sea Level: {parsed_data[12]} inHg\n"
            f"Precipitation Intensity: {parsed_data[13]} in/hr\n"
            f"Rain Intensity: {parsed_data[14]} in/hr\n"
            f"Freezing Rain Intensity: {parsed_data[15]} in/hr\n"
            f"Snow Intensity: {parsed_data[16]} in/hr\n"
            f"Sleet Intensity: {parsed_data[17]} in/hr\n"
            f"Precipitation Probability: {parsed_data[18]}%\n"
            f"Precipitation Type: {parsed_data[19]} (0 = No precipitation, 1 = Rain, 2 = Snow, 3 = Freezing rain, 4 = Ice pellets / sleet)\n"
            f"Rain Accumulation: {parsed_data[20]} in\n"
            f"Snow Accumulation: {parsed_data[21]} in\n"
            f"Snow Accumulation LWE: {parsed_data[22]} in of LWE\n"
            f"Snow Depth: {parsed_data[23]} in\n"
            f"Sleet Accumulation: {parsed_data[24]} in\n"
            f"Sleet Accumulation LWE: {parsed_data[25]} in of LWE\n"
            f"Ice Accumulation: {parsed_data[26]} in\n"
            f"Ice Accumulation LWE: {parsed_data[27]} in of LWE\n"
            f"Visibility: {parsed_data[28]} mi\n"
            f"Cloud Cover: {parsed_data[29]}%\n"
            f"Cloud Base: {parsed_data[30]} mi\n"
            f"Cloud Ceiling: {parsed_data[31]} mi\n"
            f"UV Index: {parsed_data[32]} (0-2: Low, 3-5: Moderate, 6-7: High, 8-10: Very High, 11+: Extreme)\n"
            f"UV Health Concern: {parsed_data[33]} (0-2: Low, 3-5: Moderate, 6-7: High, 8-10: Very High, 11+: Extreme)\n"
            f"Evapotranspiration: {parsed_data[34]} in\n"
            f"Thunderstorm Probability: {parsed_data[35]}%\n"
            f"EZ Heat Stress Index: {parsed_data[36]} (0-22: No Heat Stress 22-24: Mild Heat Stress 24-26: Moderate Heat Stress 26-28: Medium Heat Stress 28-30: Severe Heat Stress 30+: Extreme Heat Stress)\n"
        )
        return parsed_data, message
    
    # collect the historically observed weather data
    def parse_historically_observed_weather_data(self, historical_data):
        # initialize variables
        intervals = historical_data['data']['timelines'][0]['intervals']
        parsed_data = []
        historically_observed_data = []

        # go through each hour and collect the data
        for hour in intervals:
            start_time = hour.get('startTime', '')
            date = start_time[0:10]
            time = start_time[11:19]
            weather_values = hour.get('values', {})
            parsed_data = [date, time, self.location, self.coordinates]

            # go through each field and collect the corresponding data
            for field in self.field_names:
                value = weather_values.get(field, '')
                parsed_data.append(value)

            historically_observed_data.append(parsed_data)
        
        return historically_observed_data
    
    # collect the forecasted weather data
    def parse_forecasted_weather_data(self, forecasted_data):
        # initialize variables
        intervals = forecasted_data['data']['timelines'][0]['intervals']
        parsed_forecasted_data = []

        # go through each hour and collect the data
        for hour in intervals:
            start_time = hour.get('startTime', '')
            date = start_time[0:10]
            time = start_time[11:19]
            weather_values = hour.get('values', {})
            parsed_data = [date, time, self.location, self.coordinates]

            # go through each field and collect the corresponding data
            for field in self.field_names:
                value = weather_values.get(field, '')
                parsed_data.append(value)

            parsed_forecasted_data.append(parsed_data)

        return parsed_forecasted_data
                
    pass