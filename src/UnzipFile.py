import os
import zipfile
import datetime
import configparser
from multiprocessing import Pool, Lock
import shutil

# Define a lock for synchronizing access to the log file
log_lock = Lock()

def extract_and_move_contents(zip_ref, extract_path):
    try:
        # Extract all contents of the zip file to a temporary directory
        temp_extract_path = os.path.join(extract_path, "__temp__")
        zip_ref.extractall(temp_extract_path)

        # Move contents of the inner folder to the outer directory
        inner_folder = os.listdir(temp_extract_path)[0].rstrip()
        inner_folder_path = os.path.join(temp_extract_path, inner_folder)
        for item in os.listdir(inner_folder_path):
            item_path = os.path.join(inner_folder_path, item.rstrip())
            shutil.move(item_path, extract_path)

        # Delete the inner folder
        shutil.rmtree(inner_folder_path)

        # Remove the temporary directory
        os.rmdir(temp_extract_path)
    except Exception as e:
        print(f"Error while executing extract_and_move_contents() function: {e}")

def unzip_code(root_folder, extract_path, execution_log_path, time_to_unzip_log_path):
    success_count = 0
    failure_count = 0
    
    try:
        with open(execution_log_path, "a", encoding="utf-8") as execution_log, \
                open(time_to_unzip_log_path, "a", encoding="utf-8") as time_to_unzip_log:

            for root, dirs, files in os.walk(root_folder):
                # Check if the current depth is at level 2
                if root.count(os.sep) == root_folder.count(os.sep) + 1:
                    for file in files:
                        if file.endswith(".zip"):
                            repo_path = os.path.join(root, file)
                            repo_name = os.path.splitext(file)[0]
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")
                            execution_message = f"{timestamp} | {repo_name} | "

                            print(f"Extracting {repo_path} to {extract_path}")
                            if not zipfile.is_zipfile(repo_path):
                                failure_count += 1
                                raise ValueError(f"Not a valid zip file: {repo_path}")

                            # Create a directory with the name of the zip file
                            repo_extract_path = os.path.join(extract_path, repo_name)
                            if os.path.exists(repo_extract_path) and os.listdir(repo_extract_path):
                                dir_to_delete = repo_extract_path
                                command = f'rmdir /s /q "{dir_to_delete}"'
                                os.system(command)
                                # print(f"Warning: {repo_extract_path} already exists with contents. Skipping extraction for {repo_path}")
                                # continue  # Skip extraction if directory exists with contents
                            os.makedirs(repo_extract_path, exist_ok=True)

                            start_time = datetime.datetime.now()
                            try:
                                with zipfile.ZipFile(repo_path, 'r') as zip_ref:
                                    # Extract and move contents
                                    extract_and_move_contents(zip_ref, repo_extract_path)

                            except Exception as e:                               
                                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")
                                execution_log.write(f"{execution_message}Failed: {e}\n")
                                print(f"Extraction failed for {repo_path}: {e}\n")
                                failure_count += 1

                            else:
                                end_time = datetime.datetime.now()
                                total_time = end_time - start_time

                                execution_log.write(f"{execution_message}Successful\n")
                                time_to_unzip_log.write(f"{repo_name} | {start_time} | {end_time} | {total_time}\n")
                                print(f"Extraction completed for {repo_path}\n")
                                success_count += 1

    except Exception as e:
        print(f"Error while executing unzip_code() function: {e}")
        #timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")
        #execution_message = f"{timestamp} | Failed: {str(e)}\n"
        #with open(execution_log_path, "a") as execution_log:
        #    execution_log.write(execution_message)
        #failure_count += 1

    finally:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")
        with open(execution_log_path, "a", encoding="utf-8") as execution_log:
            execution_log.write(f"{timestamp} | Summary: Processed {success_count} zip files successfully, {failure_count} zip files failed.\n")


def create_and_run_batches(config):
    try:
        repos_folder = config['Paths']['repos_folder']
        extract_folder = config['Paths']['extract_folder']
        logs_folder = config['Paths']['logs_folder']
        os.makedirs(logs_folder, exist_ok=True)

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        execution_log_path = os.path.join(logs_folder, f"execution_log_{timestamp}.txt")
        time_to_unzip_log_path = os.path.join(logs_folder, f"time_to_unzip_log_{timestamp}.txt")

        pool_args = []
        for root, dirs, files in os.walk(repos_folder):
            for file in files:
                if file.endswith(".zip"):
                    repo_name = os.path.splitext(file)[0]
                    repo_path = os.path.join(root, file)
                    extract_path = os.path.join(extract_folder, repo_name)
                    os.makedirs(extract_path, exist_ok=True)
                    pool_args.append((repo_path, extract_path, repo_name, execution_log_path, time_to_unzip_log_path, 0))

        with Pool() as pool:
            pool.map(unzip_code, pool_args)
    except Exception as e:
        print(f"Error while executing create_and_run_batches() function: {e}")


def main():
    global config
    config = configparser.ConfigParser()
    config.read('config.properties')
    create_and_run_batches(config)


if __name__ == "__main__":
    main()
