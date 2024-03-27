import csv
import requests
import os
import shutil
import datetime
import json

def list_organization_repos(org_name, access_token, output_type):
    url = f"https://api.github.com/orgs/{org_name}/repos"
    headers = {
        'Authorization': f'token {access_token}'
    }
    params = {
        'per_page': 100,  # Number of repositories per page
        'page': 1         # Page number
    }
    repos = []

    # Fetch repositories with pagination
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            repos_page = response.json()
            repos.extend(repos_page)
            if len(repos_page) < 100:
                break  # Break if the number of repositories fetched is less than 100
            params['page'] += 1  # Move to the next page
        else:
            print(f"Failed to fetch organization repositories. Status code: {response.status_code}")
            return

    # Prepare output data
    output = []
    for repo in repos:
        repo_name = repo.get('name')
        repo_size = get_repo_size(org_name, repo_name, access_token) if output_type == 2 else None
        repo_size = f"{repo_size} KB" if repo_size else None
        if output_type == 1:
            output.append({'Repo_name': repo_name})
        elif output_type == 2:
            output.append({'Repo_name': repo_name, 'Repo_Size': repo_size})

    return output

def get_repo_size(org_name, repo_name, access_token):
    url = f"https://api.github.com/repos/{org_name}/{repo_name}"
    headers = {
        'Authorization': f'token {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repo_data = response.json()
        size = repo_data.get('size', 'N/A')
        return size
    else:
        print(f"Failed to fetch repository data. Status code: {response.status_code}")
        return None

def write_to_csv(data, filename):
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    except IOError:
        print("Error: Could not write to file. Please check the filename and try again.")

import datetime

def checkout_master_branch(org_name, repo_name, access_token, destination_path):
    url = f"https://api.github.com/repos/{org_name}/{repo_name}/tarball/master"
    headers = {
        'Authorization': f'token {access_token}'
    }
    try:
        start_time = datetime.datetime.now()
        response = requests.get(url, headers=headers, stream=True)
        end_time = datetime.datetime.now()
        
        if response.status_code == 200:
            with open(os.path.join(destination_path, f"{repo_name}_master.tar.gz"), 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            print(f"Master branch of {repo_name} has been checked out to {destination_path}.")
        else:
            print(f"Failed to checkout master branch of {repo_name}. Status code: {response.status_code}")
        
        # Write to log file
        with open('download_log.txt', 'a') as log_file:
            log_file.write(f"{repo_name} | {start_time} | {end_time}\n")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {repo_name}. Error: {e}")
        print(f"Moving to the next repository.")
      
def get_all_repo_metadata(org_name, access_token):
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
            repo_url = f"https://api.github.com/orgs/{org_name}/repos?per_page=100&page={page_number}"
            response = requests.get(repo_url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

            repos = response.json()
            if not repos:  # No more repositories on this page
                break
            all_repos.extend(repos)
            page_number += 1

        # Save repository metadata to JSON file
        with open(f"{org_name}_Repositories_Metadata.json", "w") as json_file:
            json.dump(all_repos, json_file, indent=4)

        log_messages.append(f"Metadata for all repositories in organization {org_name} downloaded successfully.")

    except requests.exceptions.RequestException as e:
        log_messages.append(f"Error: {str(e)}")

    end_time = datetime.datetime.now()
    total_time = end_time - start_time

    # Log the start and end time, along with total time taken
    with open("download_log.txt", "a") as log_file:
        log_file.write(f"Start Time: {start_time}\n")
        log_file.write(f"End Time: {end_time}\n")
        log_file.write(f"Total Time Taken: {total_time}\n")
        for message in log_messages:
            log_file.write(message + "\n")

def get_single_repo_metadata(org_name, repo_name):
    start_time = datetime.datetime.now()
    log_messages = []

    try:
        # Fetch repository metadata from GitHub API
        repo_response = requests.get(f"https://api.github.com/repos/{org_name}/{repo_name}")
        repo_response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

        repo_metadata = repo_response.json()

        # Save repository metadata to JSON file
        with open(f"{repo_name}_Metadata.json", "w") as json_file:
            json.dump(repo_metadata, json_file, indent=4)

        log_messages.append(f"Metadata for repository {repo_name} downloaded successfully.")

    except requests.exceptions.RequestException as e:
        log_messages.append(f"Error: {str(e)}")

    end_time = datetime.datetime.now()
    total_time = end_time - start_time

    # Log the start and end time, along with total time taken
    with open("download_log.txt", "a") as log_file:
        log_file.write(f"Start Time: {start_time}\n")
        log_file.write(f"End Time: {end_time}\n")
        log_file.write(f"Total Time Taken: {total_time}\n")
        for message in log_messages:
            log_file.write(message + "\n")

def main():
    
    ORG_NAME = input("Enter the name of the GitHub organization: ")
    ACCESS_TOKEN = input("Enter GitHub access token: ")
    GITAPI_URL = "https://api.github.com/orgs/CAST-Extend/repos"
    
    while True:
        print("Select options:")
        print("1. Get name of all GitHub repositories in an organization")
        print("2. Get name & size of all GitHub repositories in an organization")
        print("3. Checkout master branch of each repository to a physical drive location")
        print("4. Download GitHub organization metadata")
        print("5. Download GitHub organization metadata for single repository")

        choice = input("Enter your choice (1/2/3/4/5): ")
        if choice not in ['1', '2', '3', '4', '5']:
            print("Invalid choice. Please enter 1, 2, 3, 4 or 5.")
            continue
        else:
            break

    output_type = int(choice)
    if output_type in [1, 2]:
        output = list_organization_repos(ORG_NAME, ACCESS_TOKEN, output_type)
        if output:
            if output_type == 2:
                output_filename = "Repo-output.csv"
            else:
                while True:
                    output_filename = input("Enter output file name (e.g., output.csv): ")
                    if output_filename.strip() == "":
                        print("Please provide a valid output file name.")
                        continue
                    else:
                        break

            try:
                write_to_csv(output, output_filename)
                print(f"Data has been written to {output_filename}")
            except Exception as e:
                print(f"An error occurred while writing to the file: {e}")
    elif output_type == 3:
        destination_path = input("Enter the destination path to checkout the repositories: ")
        for repo in list_organization_repos(ORG_NAME, ACCESS_TOKEN, 1):
            checkout_master_branch(ORG_NAME, repo['Repo_name'], ACCESS_TOKEN, destination_path)
    elif output_type == 4:
         get_all_repo_metadata(ORG_NAME, ACCESS_TOKEN)
    elif output_type == 5:
        repo_name = input("Enter the name of the repository: ")
        get_single_repo_metadata(ORG_NAME, repo_name)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
