# libraries
import json
import requests
import datetime
import time

# class that manages collecting and storing data from the Tomorrow.io weather API
class process_api_data:
    def __init__(self, coordinates, field_names, API_KEY):
        self.coordinates = coordinates
        self.field_names = field_names
        self.url = "https://api.tomorrow.io/v4/timelines"
        self.API_KEY = API_KEY

        pass

    # collect weather data from the API
    def collect_weather_data(self):
        # make the API request while handling potential errors

        # initialize variables for retries
        max_retries = 3
        sleep_time = 10

        # make the API request with retries
        for attempt in range(1, max_retries + 1):
            # if everything goes right then perform this API request
            try:
                # make the API request
                params = {
                    "location": self.coordinates,
                    "fields": self.field_names,
                    "units": "imperial",
                    "timesteps": "1h",
                    "apikey": self.API_KEY
                }

                query = requests.get(url=self.url, params=params, timeout=10)
                query.raise_for_status()  # raise an error for bad status codes

                ### FOR DEBUGGING PURPOSES ONLY. COMMENT OUT WHEN NOT IN PRODUCTION. ###
                #print(f"API Status: {query.status_code}\n")
                #print(f"API Response: {query.text}\n")

                # store the weather data
                weather_data = query.json()
                #print(weather_data)

                return weather_data
            # handle HTTP errors
            except requests.exceptions.HTTPError as HTTPError:
                # retrieve the status code
                status = HTTPError.response.status_code

                print(f"Attempt {attempt} out of {max_retries} failed: HTTP {status}\n")

                # handle specific HTTP errors
                self.handle_http_errors(status, HTTPError)

                # if the error is not a specific fatal error then attempt to retry the request
                if (attempt < max_retries):
                    print(f"Error is not caught as fatal. Retrying in {sleep_time} seconds...\n")

                    # delay before retrying
                    time.sleep(sleep_time)
                    sleep_time = sleep_time * 2     # increase the delay for the next retry
                # if the maximum number of retries is reached then raise the error and exit
                else:
                    raise RuntimeError("Maximum retry attempts reached for API request. Please try again later.") from HTTPError
                
            # handle other request exceptions
            except requests.exceptions.RequestException as RequestException:
                print(f"Attempt {attempt} out of {max_retries} failed: {RequestException}\n")

                # if the error is not a specific fatal error then attempt to retry the request
                if (attempt < max_retries):
                    print(f"Error is not caught as fatal. Retrying in {sleep_time} seconds...\n")

                    # delay before retrying
                    time.sleep(sleep_time)
                    sleep_time = sleep_time * 2     # increase the delay for the next retry
                # if the maximum number of retries is reached then raise the error and exit
                else:
                    raise RuntimeError("Maximum retry attempts reached for API request. Please try again later.") from RequestException
                
        pass

    # collect historical observed weather data from the past 24 hours
    def collect_historically_observed_data(self):
        # make the API request while handling potential errors

        # initialize variables for retries
        max_retries = 3
        sleep_time = 10

        # make the API request with retries
        for attempt in range(1, max_retries + 1):
            # make the API request while handling potential errors
            try:
                # set the time range for the past 24 hours
                start_time = (datetime.datetime.now(datetime.timezone.utc).replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=24)).replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
                end_time = (datetime.datetime.now(datetime.timezone.utc).replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

                historical_params = {
                    "location": self.coordinates,
                    "fields": self.field_names,
                    "units": "imperial",
                    "timesteps": "1h",
                    "startTime": start_time,
                    "endTime": end_time,
                    "apikey": self.API_KEY
                }

                # make the API request
                query = requests.get(url=self.url, params=historical_params, timeout=10)
                query.raise_for_status()  # raise an error for bad status codes

                ### FOR DEBUGGING PURPOSES ONLY. COMMENT OUT WHEN NOT IN PRODUCTION. ###
                #print(f"API Status: {query.status_code}\n")
                #print(f"API Response: {query.text}\n")

                # store the historical weather data
                historical_weather_data = query.json()
                #print(historical_weather_data)

                return historical_weather_data
            # handle HTTP errors
            except requests.exceptions.HTTPError as HTTPError:
                # retrieve the status code
                status = HTTPError.response.status_code

                print(f"Attempt {attempt} out of {max_retries} failed: HTTP {status}\n")

                # handle specific HTTP errors
                self.handle_http_errors(status, HTTPError)

                # if the error is not a specific fatal error then attempt to retry the request
                if (attempt < max_retries):
                    print(f"Error is not caught as fatal. Retrying in {sleep_time} seconds...\n")

                    # delay before retrying
                    time.sleep(sleep_time)
                    sleep_time = sleep_time * 2     # increase the delay for the next retry
                # if the maximum number of retries is reached then raise the error and exit
                else:
                    raise RuntimeError("Maximum retry attempts reached for API request. Please try again later.") from HTTPError
                
            # handle other request exceptions
            except requests.exceptions.RequestException as RequestException:
                print(f"Attempt {attempt} out of {max_retries} failed: {RequestException}\n")

                # if the error is not a specific fatal error then attempt to retry the request
                if (attempt < max_retries):
                    print(f"Error is not caught as fatal. Retrying in {sleep_time} seconds...\n")

                    # delay before retrying
                    time.sleep(sleep_time)
                    sleep_time = sleep_time * 2     # increase the delay for the next retry
                # if the maximum number of retries is reached then raise the error and exit
                else:
                    raise RuntimeError("Maximum retry attempts reached for API request. Please try again later.") from RequestException
                
        pass

    # handles HTTP errors when calling the API
    def handle_http_errors(self, status, HTTPError):
        # HTTP status code categories:
        # 100-199: Informational responses (can be ignored)
        # 200-299: Successful responses (can be ignored)
        # 300-399: Redirection messages (implement redirection handling if necessary)
        # 400-499: Client error responses (handle specific client errors)
        # 500-599: Server error responses (handle specific server errors)

        # define the HTTP errors (c)urrently catching only the 400 series errors)
        http_errors = {
            400: "Fatal HTTP Error 400: Bad request. Please check your API request parameters (e.g., URL).",
            401: "Fatal HTTP Error 401: Authentication failed. Please check your API key.",
            403: "Fatal HTTP Error 403: Access forbidden. Please check your API key permissions or your API request paramaters (e.g., URL).",
            404: "Fatal HTTP Error 404: Resource not found. Please check your API request parameters (e.g., URL).",
            405: "Fatal HTTP Error 405: Method not allowed. Please check your API request method (e.g., DELETE or POST).",
            409: "Fatal HTTP Error 409: Conflict detected. Please avoid making conflicting requests simultaneously.",
            413: "Fatal HTTP Error 413: Payload too large. Please reduce the size of your API request parameters.",
            414: "Fatal HTTP Error 414: URL too long. Please shorten your API request URL.",
            429: "Fatal HTTP Error 429: Too many requests. Please reduce the frequency of your API requests."
        }

        # What a bad request error (HTTP Error 400) might look like:
        # params = {
        #     "location": self.field_names,   # incorrect parameter
        #     "fields": self.coordinates,     # incorrect parameter
        #     "units": "imperial",
        #     "timesteps": "1h",
        #     "apikey": self.API_KEY
        # }

        # What an authentication error (HTTP Error 401) might look like:
        # API_KEY = "ABC123"    # invalid API key

        # What a forbidden error (HTTP Error 403) might look like:
        # params = {
        #     "location": self.coordinates,
        #     "fields": ["particulateMatter25"],  # field not included in the free plan
        #     "units": "imperial",
        #     "timesteps": "1h",
        #     "apikey": self.API_KEY
        # }

        # What a not found error (HTTP Error 404) might look like:
        # url = "https://api.tomorrow.io/v4/ABC123"   # invalid URL

        # What a method not allowed error (HTTP Error 405) might look like:
        # using POST/DELETE instead of GET or vice versa
        # query = requests.delete(url=self.url, params=params, timeout=10)

        # What a conflict error (HTTP Error 409) might look like:
        # making conflicting requests simultaneously

        # What a payload too large error (HTTP Error 413) might look like:
        # params = {
        #     "location": self.coordinates,
        #     "fields": ["temperature"] * 1000,     # excessively large number of fields
        #     "units": "imperial",
        #     "timesteps": "1h",
        #     "apikey": self.API_KEY
        # }

        # What a URL too long error (HTTP Error 414) might look like:
        # url = "https://api.tomorrow.io/v4/timelines?" + "a" * 5000   # excessively long URL

        # What a too many requests error (HTTP Error 429) might look like:
        # making too many API requests in a short period of time

        # check if the status code is in the defined HTTP errors
        if (status in http_errors):
            raise RuntimeError(f"{http_errors[status]}") from HTTPError
        
        pass

    pass