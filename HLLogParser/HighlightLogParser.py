import os
import requests
import csv
import json
import openpyxl
import pandas as pd
from datetime import datetime
import re
import configparser

# Function to parse datetime from log line
def parse_datetime(log_line):
    return datetime.strptime(log_line[:23], "%Y-%m-%d %H:%M:%S,%f")

# Function to calculate time difference in minutes
def calculate_time_difference(start_time, end_time):
    time_difference_seconds = (end_time - start_time).total_seconds()
    return time_difference_seconds / 60

# Function to read log file and extract application name and ID
def read_log_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        start_time = None
        end_time = None
        application_name = None
        application_id = None

        for line in lines:
            if "INFO  console: Command Line version" in line:
                start_time = parse_datetime(line)
            elif "INFO  console: Highlight automation completed successfully!" in line:
                end_time = parse_datetime(line)
                break

            # Extracting application name and ID from the log line
            match = re.search(r"application \[name='(.*?)',id=(\d+)\]", line)
            if match:
                application_name = match.group(1)
                application_id = match.group(2)

        if start_time and end_time:
            total_time_minutes = calculate_time_difference(start_time, end_time)
            return start_time, end_time, total_time_minutes, application_name, application_id
        else:
            return start_time, "Error", "Error", None, None

# Function to recursively search for log files in a directory
def find_log_files(root_dir):
    log_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".log"):
                log_files.append(os.path.join(root, file))
    return log_files

def retrieve_HLAppName_and_LOC(api_url, bearer_token, CompanyID):
    # Define headers
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    RESTURL = "{}/WS2/domains/{}/applications".format(api_url, CompanyID)
    
    # Make a GET request to the API
    try:
        response = requests.get(RESTURL, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()

            # # Save API response to output.json
            # with open('output.json', 'w') as json_file:
            #     json.dump(data, json_file, indent=4)
            #     print("API response saved to output.json.")
            # if not data:
            #     print("No data found in the API response.")
            #     return
            
            # Create and open a CSV file in write mode
            with open('HLAppsandLOC.csv', 'w', newline='') as csvfile:
                # Create a CSV writer object
                csv_writer = csv.writer(csvfile)

                # Write headers
                csv_writer.writerow(['ID', 'Name', 'Total Lines of Code'])
                
                # Write data to CSV file
                for app in data:
                    try:
                        # Assuming we use the first set of metrics
                        csv_writer.writerow([app['id'], app['name'], app['metrics'][0]['totalLinesOfCode']])
                        #print(f"Results Found for application {app['name']}, {app['metrics'][0]['totalLinesOfCode']}.")
                    except (KeyError, IndexError):
                        print(f"No results found for application {app['name']}.")

            print("API call output is written to HLAppsandLOC.csv.")

        else:
            print("Failed to retrieve data from the API.")
    except requests.RequestException as e:
        print(f"Error occurred while making API request: {e}")

# Main function
def main():
    config = configparser.ConfigParser()
    config.read('config.properties')

    root_directory = config.get('parameters', 'root_directory')
    output_directory = config.get('parameters', 'output_directory')
    bearer_token = config.get('parameters', 'bearer_token')
    api_url = config.get('parameters', 'api_url')
    CompanyID = config.get('parameters', 'CompanyID')

    if not all([root_directory, output_directory, bearer_token, api_url, CompanyID]):
        print("Please provide all inputs in config.properties.")
        return

    log_files = find_log_files(root_directory)
    if not log_files:
        print("No log files found in the specified directory.")
        return

    data = []
    for log_file in log_files:
        start_time, end_time, total_time, application_name, application_id = read_log_file(log_file)
        if start_time:
            # Extracting application name from the log file path
            data.append([application_name, application_id, log_file, start_time, end_time, total_time])

    output_file_path = os.path.join(output_directory, "HLLogReport.xlsx")
    df = pd.DataFrame(data, columns=['Application Name', 'Application ID', 'Log File', 'Start Time', 'End Time', 'Total Time (minutes)'])
    df.to_excel(output_file_path, index=False)
    print("Output written to Excel file:", output_file_path)

    # Call retrieve_HLAppName_and_LOC function
    retrieve_HLAppName_and_LOC(api_url, bearer_token, CompanyID)

    # Read HLAppsandLOC.csv and HighlightLogSummary.csv
    hl_apps_loc_df = pd.read_csv('HLAppsandLOC.csv')

    # Merge data from both dataframes
    merged_df = pd.merge(df, hl_apps_loc_df, left_on='Application Name', right_on='Name', how='left')

    # Create a new Excel workbook for consolidated data
    consolidated_workbook = openpyxl.Workbook()
    consolidated_sheet = consolidated_workbook.active

    # Write headers to the consolidated sheet
    consolidated_sheet['A1'] = 'Application Name'
    consolidated_sheet['B1'] = 'Application ID'
    consolidated_sheet['C1'] = 'Log File'
    consolidated_sheet['D1'] = 'Start Time'
    consolidated_sheet['E1'] = 'End Time'
    consolidated_sheet['F1'] = 'Total Time (minutes)'
    consolidated_sheet['G1'] = 'LOC'
    #consolidated_sheet['H1'] = 'App ID'

    # Write data to the consolidated sheet
    for index, row in merged_df.iterrows():
        consolidated_sheet[f'A{index + 2}'] = row['Application Name']
        consolidated_sheet[f'B{index + 2}'] = row['Application ID']
        consolidated_sheet[f'C{index + 2}'] = row['Log File']
        consolidated_sheet[f'D{index + 2}'] = row['Start Time']
        consolidated_sheet[f'E{index + 2}'] = row['End Time']
        consolidated_sheet[f'F{index + 2}'] = row['Total Time (minutes)']
        consolidated_sheet[f'G{index + 2}'] = row['Total Lines of Code']
        #consolidated_sheet[f'H{index + 2}'] = row['ID']

    # Save the consolidated workbook
    consolidated_workbook.save(os.path.join(output_directory, 'HLLogSummaryReport.xlsx'))
    print("Consolidated data has been written to HLLogSummaryReport.xlsx.")
    # Delete HLAppsandLOC.csv and HLLogReport.xlsx
    os.remove('HLAppsandLOC.csv')
    os.remove(output_file_path)
# Run the main function
if __name__ == "__main__":
    main()
