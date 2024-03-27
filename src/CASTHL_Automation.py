import threading
import requests
import json
import datetime
import csv
import pandas as pd
import os
from argparse import ArgumentParser
import configparser
import zipfile
import UnzipFile
import AppRepoMapping
import HLScanAndOnboard
import logging


def get_all_repo_metadata(org_name, access_token, output_file_path, log_file_path):
    start_time = datetime.datetime.now()
    log_messages = []

    try:
        # Initialize an empty list to store all repositories
        all_repos = []

        # Fetch repositories from GitHub API with pagination
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        page_number = 1
        while True:
            repo_url = f"https://api.github.com/orgs/{org_name}/repos?per_page=200&page={page_number}"
            response = requests.get(repo_url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            print (response.raise_for_status)
            repos = response.json()
            if not repos:  # No more repositories on this page
                break
            all_repos.extend(repos)
            page_number += 1

        # Save repository metadata to JSON file
        with open(output_file_path, "w") as json_file:
            json.dump(all_repos, json_file, indent=4)

        log_messages.append(f"Metadata for all repositories in organization {org_name} downloaded successfully.")
        print(f"Metadata for all repositories in organization {org_name} downloaded successfully.")
    except requests.exceptions.RequestException as e:
        log_messages.append(f"Error: {str(e)}")

    end_time = datetime.datetime.now()
    total_time = end_time - start_time


    # Log the start and end time, along with total time taken
    with open(log_file_path, "a") as log_file:
        log_file.write(f"Start Time: {start_time}\n")
        log_file.write(f"End Time: {end_time}\n")
        log_file.write(f"Total Time Taken: {total_time}\n")
        for message in log_messages:
            log_file.write(message + "\n")

def json_to_csv(json_filename, csv_filename):
    try:
        # Read JSON data from file
        with open(json_filename, 'r') as json_file:
            json_data = json.load(json_file)
              
        # Add additional headers
        headers = ['id', 'name', 'default_branch', 'size', 'updated_at', 'clone_url','archive_url']
        #headers.extend(additional_headers)
        
        # Write to CSV
        with open(csv_filename, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            for entry in json_data:
                # Extract data from each entry
                row_data = {key: entry.get(key, '') for key in headers}
                # Write row to CSV
                writer.writerow(row_data)
        print("Repo Summary CSV file generated successfully.")
        
    except FileNotFoundError:
        print("File not found.")
    except json.JSONDecodeError:
        print("Invalid JSON format.")
    except Exception as e:
        print(f"An error occurred: {e}")

def modify_archive_urls(csv_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Define a function to replace placeholders in archive_url and create a new column
    def replace_url(row):
        archive_format = 'zipball/'
        ref = row['default_branch']
        final_url = row['archive_url'].replace('{archive_format}', archive_format).replace('{/ref}', ref)
        return final_url

    # Apply the function to create the new column 'archive_url_download'
    df['repo_archive_download_api'] = df.apply(replace_url, axis=1)

    # Write the modified DataFrame back to the original CSV file
    df.to_csv(csv_file_path, index=False)

def check_column_exists(file_path, column_name):
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Check if the column exists
        if column_name not in df.columns:
            print(f"Column '{column_name}' does not exist in the CSV file.")
            return False
        
        # Check if the column has data
        if df[column_name].empty:
            print(f"Column '{column_name}' exists but has no data.")
            return False
        
        return True
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
def read_csv_data(file_path):
    """
    Reads data from a CSV file.
    Parameters:
        file_path (str): The path to the CSV file.
    Returns:
        list: A list containing tuples of data extracted from the CSV file.
    """
    data = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                data.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))  # Assuming 4 columns in the CSV
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return data

def log_start_end_time(repository_name, start_time, end_time, total_time, log_file):
    """
    Logs start and end time of a process.
    Parameters:
        repository_name (str): The name of the repository or process.
        start_time (datetime): The start time of the process.
        end_time (datetime): The end time of the process.
        total_time (timedelta): The total time taken for the process.
        log_file (str): The path to the log file.
    """
    log_message = f"{repository_name} | {start_time} | {end_time} | {total_time} |"
    with open(log_file, "a") as f:
        f.write(log_message + "\n")

def log_processing(repository_name, status, log_file):
    """
    Logs the processing status of a repository.
    Parameters:
        repository_name (str): The name of the repository.
        status (str): The processing status.
        log_file (str): The path to the log file.
    """    
    log_message = f"{repository_name} | {status}"
    with open(log_file, "a") as f:
        f.write(log_message + "\n")

def download_zip_archive(repository_url, repository_path, token):
    """
    Downloads a ZIP archive from a given URL.
    Parameters:
        repository_url (str): The URL of the repository.
        repository_path (str): The path to save the ZIP archive.
        token (str): The GitHub access token.
        
    Returns:
        bool: True if download is successful, False otherwise.
    """
    #print(f"Inside **download_zip_archive**'.")
    headers = {'Authorization': f'token {token}'}
    response = requests.get(repository_url, headers=headers)
    
    if response.status_code == 200:
        with open(repository_path, 'wb') as f:
            f.write(response.content)
        return True
    else:
        return False

def download_and_save_code(application_name, repository_url, server_location, token, start_end_log_file, processing_log_file):
    """
    Downloads and saves code from a repository.
    Parameters:
        application_name (str): The name of the application or repository.
        repository_url (str): The URL of the repository.
        server_location (str): The location to save the repository.
        token (str): The GitHub access token.
        start_end_log_file (str): The path to the log file for start and end times.
        processing_log_file (str): The path to the log file for processing status.
    """
    #print(f"Inside **Download-And-Save**'.")
    application_name_directory = os.path.join(server_location, application_name)
        # Check if the 'Output' folder exists, if not, create it
    if not os.path.exists(application_name_directory):
        os.makedirs(application_name_directory)
    
    repository_zip_path = os.path.join(application_name_directory, application_name + '.zip')
    #print(f"repository_zip_path '{repository_zip_path}'.")
    if os.path.exists(repository_zip_path):
        log_processing(application_name, "Skipped: ZIP file already exists", processing_log_file)
        print(f"Skipping repository '{application_name}'. ZIP file already exists.\n")
    else:
        start_time = datetime.datetime.now()
        try:
            if download_zip_archive(repository_url, repository_zip_path, token):
                with zipfile.ZipFile(repository_zip_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    if not file_list:
                        log_processing(application_name, "Repo is empty", processing_log_file)
                        print(f"Repository '{application_name}' is empty.\n")
                    else:
                        end_time = datetime.datetime.now()
                        total_time = end_time - start_time
                        log_start_end_time(application_name, start_time, end_time, total_time, start_end_log_file)
                        log_processing(application_name, "Successful", processing_log_file)
                        print(f"Repository '{application_name}' downloaded successfully as ZIP file to '{repository_zip_path}'.\n")
            else:
                print(f"Failed to download repository '{application_name}'.")
        except Exception as e:
            end_time = datetime.datetime.now()
            total_time = end_time - start_time
            log_start_end_time(application_name, start_time, end_time, total_time, start_end_log_file)
            log_processing(application_name, f"Failed: {e}", processing_log_file)
            print(f"Error downloading repository: {e}")

def main():
    
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Read configuration from config.properties file
    config = configparser.ConfigParser()
    config_file_path = os.path.join(os.path.dirname(__file__), '..', 'Config', 'config.properties')
    config.read(config_file_path)

    # Get values from the config file
    org_name = config.get('GitHub', 'github_org_name')
    token = config.get('GitHub', 'github_token')
    src_dir = config.get('Directories', 'src_dir')
    unzip_dir = config.get('Directories', 'unzip_dir')
    logs_dir = config.get('Directories', 'logs_dir')
    output_dir = config.get('Directories', 'output_dir')
    App_Repo_Mapping = config.get('Input-File', 'App_Repo_Mapping')
    src_dir_analyze = config.get('Directories', 'src_dir_analyze')

    # Check if the 'Output' folder exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Check if the 'Log Dir' folder exists, if not, create it
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
        # Check if the 'Source Dir' folder exists, if not, create it
    if not os.path.exists(src_dir):
        os.makedirs(src_dir)
    
    # Check if the 'Output' folder exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    while True:
        print("Select options:")
        print("0. Create Highlight Domain and Application")
        print("1. Download Metadata for GitHub organization")
        print("2. Download source code for all repositories in the organization in batches")
        print("3. Unzip the downloaded source code")
        print("4. Create application folders and move repositories")
        print("5. Trigger CAST Highlight onboarding for the source code")
        choice = input("Enter your choice (0/1/2/3/4/5): ")
        if choice not in ['0', '1', '2', '3', '4', '5']:
            print("Invalid choice. Please enter 0, 1, 2, 3, 4 or 5.")
            continue
        else:
            break

    output_type = int(choice)
    if output_type == 1:
          
        # Save repository metadata to JSON file
        output_file_path = os.path.join(output_dir, f"{org_name}_Repositories_Metadata.json")

        # Save repository metadata to JSON file
        log_file_path = os.path.join(logs_dir, f"{org_name}_Metadatadownload.log")
        
        # Save repository metadata to CSV file
        output_csv_file_path = os.path.join(output_dir, f"{org_name}_Repositories_Summary.csv")
        
        get_all_repo_metadata(org_name, token, output_file_path, log_file_path)
        json_to_csv(output_file_path, output_csv_file_path)
        modify_archive_urls(output_csv_file_path)
        print(f"Refer Log file {log_file_path} for downloag log and time to downloaded Metadata.")
        print(f"CSV file generated {output_csv_file_path} with summary of repositories which can be used for downloading source code(Task-2).")
    elif output_type == 2:
        output_csv_file_path = os.path.join(output_dir, f"{org_name}_Repositories_Summary.csv")
        if not os.path.exists(output_csv_file_path):
            print("Please run option 1 to download metadata first.")
            return
        if not check_column_exists(output_csv_file_path, 'batch_number'):
            print(f"Column 'batch_number' does not exist in file {output_csv_file_path}. Create new column with name 'batch_number' and enter number of batch you want to run for download.")
            return
        if not check_column_exists(output_csv_file_path, 'repo_archive_download_api'):
            print(f"Column 'repo_archive_download_api' does not exist in file {output_csv_file_path}. Review CSV file and rerun option 1.")
            return
        if not check_column_exists(output_csv_file_path, 'name'):
            print(f"Column 'name' does not exist in file {output_csv_file_path}. Review CSV file and rerun option 1.")
            return
        
        #src_dir = input("Directory location to download the source code: ")
        batch = input("Enter batch number to download the source code: ")
       
        #log_folder = os.path.join(os.path.dirname(__file__), '..', 'Logs')
        start_end_log_file = os.path.join(logs_dir, f"Timetodownload_{batch}.txt")
        processing_log_file = os.path.join(logs_dir, f"StatusLog_{batch}.txt")

        # Check if the start_end_log_file exists, if not, create it
        if not os.path.exists(start_end_log_file):
            with open(start_end_log_file, "w") as start_end_log:
                start_end_log.write("Start Time\tEnd Time\tTotal Time Taken\n")
        
        # Check if the processing_log_file exists, if not, create it
        if not os.path.exists(processing_log_file):
            with open(processing_log_file, "w") as processing_log:
                processing_log.write("Timestamp\tMessage\n")

        # Clear log files if they already exist
        open(start_end_log_file, 'w').close()
        open(processing_log_file, 'w').close()
        # Save repository metadata to CSV file
        output_csv_file_path = os.path.join(output_dir, f"{org_name}_Repositories_Summary.csv")
        data = read_csv_data(output_csv_file_path)  
        for repository in data:
            
            # Check for equality
            if repository[8] == str(batch):
                download_and_save_code(repository[1], repository[7], src_dir, token, start_end_log_file, processing_log_file)

    elif output_type == 3:

        #Unzip_File.unzip_code(src_dir, unzip_dir, os.path.join(logs_dir, f"Unzip_Execution{current_datetime}.log"), os.path.join(logs_dir, f"Unzip_Time{current_datetime}.log"))
        try:
            UnzipFile.unzip_code(src_dir, unzip_dir, os.path.join(logs_dir, f"Unzip_Execution{current_datetime}.log"), os.path.join(logs_dir, f"Unzip_Time{current_datetime}.log"))
        except Exception as e:
            print(f"Error occurred during extraction: {e}")

    elif output_type == 4:
        log_file=os.path.join(logs_dir, f"migration_log_{current_datetime}.log")
        logger = AppRepoMapping.setup_logger(log_file)
        summary_log_file = os.path.join(logs_dir, f"summary_log_{current_datetime}.txt")
        summary_logger = AppRepoMapping.create_summary_logger(summary_log_file)
        if not os.path.exists(App_Repo_Mapping):
            print("Application to repository mapping information is missing, please refer README.md to create mapping spreadhseet.")
            return
        AppRepoMapping.create_application_folders(App_Repo_Mapping, unzip_dir, src_dir_analyze, logger, summary_logger)
    
    elif output_type == 5:

        try:
                HLScanAndOnboard.main()
                
        except Exception as e:
                logging.error(f'{e}')

    else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
