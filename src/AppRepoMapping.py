import os
import pandas as pd
import shutil
import logging
import configparser
import sys
from datetime import datetime

def setup_logger(log_file):

    # Setup logger for migration process
    logger = logging.getLogger('migration_logger')
    logger.setLevel(logging.INFO)

    # Create file handler for migration log
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Create console handler for migration log
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Create formatter for migration log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def create_summary_logger(summary_log_file):
    # Setup logger for application summary
    summary_logger = logging.getLogger('summary_logger')
    summary_logger.setLevel(logging.INFO)

    # Create file handler for summary log
    summary_handler = logging.FileHandler(summary_log_file)
    summary_handler.setLevel(logging.INFO)

    # Create formatter for summary log
    summary_formatter = logging.Formatter('%(asctime)s - %(message)s')
    summary_handler.setFormatter(summary_formatter)

    # Add file handler to summary logger
    summary_logger.addHandler(summary_handler)

    return summary_logger

def clean_folder_name(name):
    # Replace characters that are not allowed in directory names
    forbidden_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|','(',')']
    for char in forbidden_chars:
        name = name.replace(char, '_')
    return name

def move_and_delete_folders(root_dir, logger):
    processed_dirs = set()  # To keep track of processed directories
    # Iterate over directories in root_dir
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames[:]:  # Iterate over a copy of dirnames to allow modification
            source_dir = os.path.join(dirpath, dirname)
            destination_dir = os.path.dirname(source_dir)
            try:
                # Check if the directory has already been processed
                if source_dir in processed_dirs:
                    continue
                # Check if the destination directory exists
                if os.path.exists(destination_dir):
                    # Check if the directory already exists at the destination
                    if not os.path.exists(os.path.join(destination_dir, dirname)):
                        # Move the entire directory to its parent directory
                        if source_dir != root_dir:  # Skip root_dir itself
                            shutil.move(source_dir, destination_dir)
                            logger.info(f"Directory '{source_dir}' moved to '{destination_dir}'.")
                            processed_dirs.add(source_dir)  # Add the directory to processed_dirs
                            # Delete the directory after successful move
                            os.rmdir(source_dir)
                    else:
                        pass
                    # Remove the directory from dirnames to prevent further iteration
                    dirnames.remove(dirname)
                else:
                    logger.error(f"Destination path '{destination_dir}' does not exist.")
            except Exception as e:
                logger.error(f"Failed to move directory '{source_dir}': {e}")


def create_application_folders(mapping_sheet, repo_folder, output_folder, logger, summary_logger):
    # Read the mapping sheet
    mapping_df = pd.read_excel(mapping_sheet)
    
    # Loop through each row in the mapping sheet
    for index, row in mapping_df.iterrows():
        repo_name = row['Repository']
        app_name = row['Application']

        # Check if app_name is NaN
        if pd.isna(app_name):
            logger.warning(f"Skipping row {index + 1}: Application Name is missing.")
            continue

        # Convert app_name to string to handle NaN
        app_name = str(app_name)

        # Clean up the application name for folder creation
        app_folder_name = clean_folder_name(app_name)
        
        # Create application folder if it doesn't exist
        app_folder_path = os.path.join(output_folder, app_folder_name)
        if not os.path.exists(app_folder_path):
            os.makedirs(app_folder_path)
            logger.info(f"Application folder '{app_name}' created.")
            
        if os.path.exists(app_folder_path+'\\'+repo_name): 
            dir_to_delete = app_folder_path+'\\'+repo_name
            command = f'rmdir /s /q "{dir_to_delete}"'
            os.system(command)
        
        # Move entire directory from repo to application folder
        repo_folder_path = os.path.join(repo_folder, repo_name)
        
        if os.path.exists(repo_folder_path) and os.path.isdir(repo_folder_path):
            shutil.move(repo_folder_path, app_folder_path)
            logger.info(f"Repository '{repo_name}' moved to application folder '{app_name}' with its contents.")
            summary_logger.info(f"{app_name};{repo_name};Passed")
            # Call the function to move and delete folders in the app folder
            move_and_delete_folders(app_folder_path, logger)
        else:
            logger.warning(f"Repository '{repo_name}' does not exist for application '{app_name}'.")
            summary_logger.info(f"{app_name};{repo_name};Failed")