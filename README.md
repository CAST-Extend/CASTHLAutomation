
### **CASTHLAutomation**

####  **Purpose:**
The purpose of the script is to combining the below steps into single module to analysis of multiple applications using CAST Highlight. It streamlines the process of analyzing source code files for various applications, allowing users to specify configurations, define source paths, and customize analysis parameters through a configuration file. In user can run the specified step by entering the step number. 

0. Create Highlight Domain and Application
1. Download Metadata for GitHub organization
2. Download source code for all repositories in the organization in batches
3. Unzip the downloaded source code
4. Create application folders and move repositories
5. Trigger CAST Highlight onboarding for the source code


#### **Key objectives and functionalities of the script include:**
1.  **Creating Highlight Domain and Application**: The script automates the creating highlight domain and application.
2.  **Download Metadata**: Metadata for all the repositories in organization first will be downloaded in JSON format and then saved in csv file by using github rest api.
3.  **Download Source Code**: It will take the Repositories_Summary.csv as input checks the batch_number column. if the batch number column is not present it will asks us add that column with vaules. After that we need to run this step again then it will ask the batch number as input and it will download  all the repositories source code as ZIP file.
4.  **Unziping Source Code**: In this step all the repositories source code will be extracted and will be moved to unzip folder.
5.  **Application Folder Creation and Repositories Move**: First application folders will be creted and then repositories will be moved to application folder with its source code.
6.	**CAST Highlight Onboarding**: The script automates the process of analyzing multiple applications by interfacing with the CAST Highlight via command-line execution. It eliminates the need for manual intervention in initiating and monitoring the analysis process for each application.
7.	**Batch Processing**: Applications are grouped into batches, and each batch is processed concurrently, leveraging multi-threading to improve efficiency. This enables faster analysis of a large number of applications, enhancing overall productivity.
8.	**Configurability**: Users can customize various parameters such as source paths, ignored directories/files, server URLs, authentication tokens, and batch sizes through the config.properties file. This allows flexibility in adapting the script to different environments and analysis requirements.
9.	**Error Handling**: The script incorporates error handling mechanisms to detect and handle issues during the analysis process. It logs detailed error messages, including return codes from the HighLight Analyzer tool, facilitating troubleshooting and debugging.
10.	**Output Generation**: Upon completion of analysis for each application, the script generates a summary CSV file containing the status, reasons for success or failure, and paths to log files. Additionally, detailed log files are created for each thread, providing comprehensive insights into the analysis execution.
Overall, the script aims to streamline and automate the process of application analysis, improving efficiency, accuracy, and ease of management for software development and quality assurance teams. By abstracting the complexities of manual analysis tasks and providing a configurable and scalable solution, it empowers users to perform thorough and consistent analysis across multiple applications with minimal effort.
 
#### **Prerequisites:**
1.	**Java Development Kit (JDK**): Ensure that JDK is installed and configured properly on the system.
2.	**Python**: Install Python programming language (version 3.x) on the system.
3.	**Perl**: Make sure Perl is installed and its path is properly set as specified in the configuration.
4.	**HighLight Analyzer**: Obtain the HighLight Analyzer tool and ensure its executable file is accessible.
5.	**Internet Connectivity**: Ensure the system has internet connectivity for accessing URLs specified in the configuration.
6.	**Configuration File**: Prepare a configuration file named config.properties with necessary parameters (details in the Configuration section).

#### **Installation:**
1.	**Clone Repository**: Clone the repository containing the script to the local system.
2.	**Setup Environment**: Set up the Python virtual environment and install required libraries using pip install -r requirements.txt.
3.	**Configuration**: Configure the config.properties file with relevant paths and parameters (details in the Configuration section).
4.	**Prepare Input Data**: Prepare a file containing the list of applications to be analyzed, with each entry in the format ApplicationName;ApplicationID.

#### **Usage:**
1.	**Execute Script**: Run the script by executing python CASTHL_Automation.py.
2.  **Enter the choice**:  It asks the beolw choice. Entert the vaules from 0 to 5 one by one.
		0) Create Highlight Domain and Application
		1) Download Metadata for GitHub organization
		2) Download source code for all repositories in the organization in batches
		3) Unzip the downloaded source code
		4) Create application folders and move repositories
		5) Trigger CAST Highlight onboarding for the source code
3.	**Monitor Progress**: Monitor the console for progress updates on application analysis.
4.	**Review Logs**: Check the log files generated in the specified log folder for detailed information about the analysis process.

### **Configuration:**
Ensure the Config\config.properties and HLLogParser\config.properties file is correctly configured with the following parameters:

 **Config\config.properties**
    [GitHub]
- **github_org_name**: GitHub Organization Name.
- **github_token**: GitHub Access Token.

[Directories]
- **config_dir**: Configuration folder path.
- **src_dir**: Path to donload the source code.
- **unzip_dir**: Path to extract the downloaded source code.
- **logs_dir**: Path to the folder where log files will be stored.
- **output_dir**: Path to the folder where output files will be stored.
- **src_dir_analyze**: Path to the directory containing the source files of the applications to be analyzed.
- **highlight_perl_dir**:  Path to the Perl installation directory.
- **highlight_analyzer_dir**:  Path to the Perl analyzer directory.
- **RESULTS**: Path to the folder where analysis results will be stored.

[Input-File]
- **App_Repo_Mapping**: Path to the App-Repo-Mapping.xlsx file. 

[HIGHLIGHT-ONBOARDING]
- **highlight_application_mapping**: Path to the applications.txt file.
- **highlight_base_url**: URL for server communication.
- **highlight_executable**: Path to the HighLight Analyzer executable file.
- **highlight_company_id**: Identifier for the company.
- **highlight_token**: Authentication token for server communication.
- **BATCH_SIZE**: Number of applications to be processed concurrently (default is 1).
- **MAX_BATCHES**: Maximum number of batches to process.

 **DO NOT CHANGE THE BELOW SETTINGS**
 - **IGNORED_DIR**=test,jquery,third-party,lib,3rd-party,COTS,external,node_modules,Tests,Test,Testing,t.ds,.flow.js,.git,.svn,gradlew,.vscode,Samples,.git,.svn, gradle, .circleci, .azure, .vscode
- **IGNORED_PATHS**=.*dummy|.*\/[tT]est\_.*|.*\/UnitTest\/.*|.*\/IntegrationTest\/.*|.*node\_modules|.*\/[tT][eE][sS][tT].*
- **IGNORED_FILES**=.yaml, .gitignore,.gitmodules, Makefile, .npmignore, .checkstyle, build.xml, gradlew


**HLLogParser\config.properties**

[parameters]
- **root_directory**: Path to store the HL Automation Logs. 
- **output_directory**:  Path to store the HL Parser Logs.
- **bearer_token**: Identifier for the company.
- **api_url**: Highlight URL.
- **CompanyID**: Highlight CompanyID.


#### **Output:**
1.	**Repositories Summary CSV File**: A CSV file containing the Repositories metadata.
2.	**Log Files**: Detailed log files are generated for each thread and stored in the specified log folder.
3.	**Console Output**: Progress updates and error messages are displayed in the console during script execution.

#### **Sample Usage:**
Copy code
CASTHL_Automation.py
Enter the choice one by one from 0 to 5.

#### **Troubleshooting:**
•	Ensure all paths specified in the configuration file are correct and accessible.
•	Check internet connectivity if accessing external URLs.
•	Review log files for detailed error messages and troubleshooting steps.

#### **Notes:**
•	This script supports multi-threading for efficient processing of application batches.
•	Ensure proper permissions are set for accessing directories and executing files specified in the configuration.
