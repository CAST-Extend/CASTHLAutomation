# import os
# import datetime
# from argparse import ArgumentParser
# from git import Repo
# import openpyxl

# def read_excel_data(file_path):
#     data = []
#     try:
#         workbook = openpyxl.load_workbook(file_path)
#         sheet = workbook.active
#         for row in sheet.iter_rows(min_row=2, values_only=True):
#             server_location = row[3].replace('\\\\', '\\')
#             data.append((row[0], row[1], row[2], server_location))
#         workbook.close()
#     except Exception as e:
#         print(f"Error reading Excel file: {e}")
#     return data

# def create_directory_if_not_exists(directory_path):
#     if not os.path.exists(directory_path):
#         try:
#             os.makedirs(directory_path)
#             print(f"Directory '{directory_path}' created successfully.\n")
#         except OSError as e:
#             print(f"Error: {e}")
#     else:
#         print(f"Directory '{directory_path}' already exists.\n")

# def log_start_end_time(repository_name, start_time, end_time, total_time, log_file):
#     log_message = f"{repository_name} | {start_time} | {end_time} | {total_time} |"
#     with open(log_file, "a") as f:
#         f.write(log_message + "\n")

# def log_processing(repository_name, status, log_file):
#     log_message = f"{repository_name} | {status}"
#     with open(log_file, "a") as f:
#         f.write(log_message + "\n")

# def download_and_save_code(application_name, repository_url, server_location, token, start_end_log_file, processing_log_file):
#     application_name_directory = os.path.join(server_location, application_name)
#     create_directory_if_not_exists(application_name_directory)

#     # Extracting repository name without the ".git" extension
#     repository_name = repository_url.split('/')[-1].replace('.git', '')
#     repository_path = os.path.join(application_name_directory, repository_name)
    
#     if os.path.exists(repository_path) and os.listdir(repository_path):
#         log_processing(repository_name, "Skipped: Directory already exists and is not empty", processing_log_file)
#         print(f"Skipping repository '{repository_name}'. Directory already exists and is not empty.\n")
#     else:
#         start_time = datetime.datetime.now()
#         try:
#             cloned_url = repository_url.replace('https://', f'https://{token}@')
#             Repo.clone_from(cloned_url, repository_path, depth=1)
#             end_time = datetime.datetime.now()
#             total_time = end_time - start_time
#             log_start_end_time(repository_name, start_time, end_time, total_time, start_end_log_file)
#             log_processing(repository_name, "Successful", processing_log_file)
#             print(f"Repository '{repository_name}' downloaded successfully to '{repository_path}'.\n")
#         except Exception as e:
#             end_time = datetime.datetime.now()
#             total_time = end_time - start_time
#             log_start_end_time(repository_name, start_time, end_time, total_time, start_end_log_file)
#             log_processing(repository_name, f"Failed: {e}", processing_log_file)
#             print(f"Error cloning repository: {e}")


# if __name__ == "__main__":
#     parser = ArgumentParser()

#     parser.add_argument('-excel_file', '--excel_file', required=True, help='Excel File Name')
#     parser.add_argument('-batch', '--batch', required=True, help='Batch Number')
#     parser.add_argument('-token', '--token', required=True, help='GitHub Access Token')
#     parser.add_argument('-log_dir', '--log_dir', required=True, help='Log Directory')

#     args = parser.parse_args()

#     # Create log directory if it doesn't exist
#     create_directory_if_not_exists(args.log_dir)

#     start_end_log_file = os.path.join(args.log_dir, "TimetoClone.txt")
#     processing_log_file = os.path.join(args.log_dir, "ExecutionLog.txt")

#     # Clear log files if they already exist
#     open(start_end_log_file, 'w').close()
#     open(processing_log_file, 'w').close()

#     data = read_excel_data(args.excel_file)

#     for repository in data:
#         if repository[2] == int(args.batch):
#             download_and_save_code(repository[0], repository[1], repository[3], args.token, start_end_log_file, processing_log_file)
