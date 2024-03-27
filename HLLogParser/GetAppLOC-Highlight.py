import csv
import requests

# Define the API URL
api_url = "https://rpa.casthighlight.com/WS2/domains/22072/applications"

# Define your bearer token
bearer_token = "xxxxxxxxxx"

# Define headers
headers = {
    "Authorization": f"Bearer {bearer_token}",
    "Content-Type": "application/json"
}

# Make a GET request to the API
response = requests.get(api_url, headers=headers)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse JSON response
    data = response.json()

    # Create and open a CSV file in write mode
    with open('applications.csv', 'w', newline='') as csvfile:
        # Create a CSV writer object
        csv_writer = csv.writer(csvfile)

        # Write headers
        csv_writer.writerow(['ID', 'Name', 'Total Lines of Code'])

        # Write data to CSV file
        for app in data:
            try:
                # Assuming we use the first set of metrics
                csv_writer.writerow([app['id'], app['name'], app['metrics'][0]['totalLinesOfCode']])
            except (KeyError, IndexError):
                print(f"No 'metrics' or 'totalLinesOfCode' data found for application {app['name']}.")

    print("Data has been written to applications.csv file.")

else:
    print("Failed to retrieve data from the API.")
