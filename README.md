# CASTHLAutomation

## Purpose

**CASTHLAutomation** is a Python-based automation tool designed to streamline the end-to-end process of analyzing multiple applications using CAST Highlight. It automates the workflow from fetching GitHub repository metadata, downloading and organizing source code, to triggering CAST Highlight onboarding and parsing results. The tool is highly configurable and supports batch processing, error handling, and detailed logging.

---

## Features & Workflow

The main entry point is `CASTHL_Automation.py`. The script is interactive and modular, allowing you to execute each step independently or as a sequence:

1. **Download Metadata:**  
   Fetches metadata for all repositories in a specified GitHub organization using the GitHub REST API. Metadata is saved as both JSON and CSV (`Repositories_Summary.csv`).

2. **Download Source Code:**  
   Downloads source code ZIPs for all repositories listed in `Repositories_Summary.csv`. Supports batch processing (batch numbers are managed in the CSV).

3. **Unzip Source Code:**  
   Extracts all downloaded ZIP files into a specified directory for further processing.

4. **Organize Application Folders:**  
   Creates application folders and moves the corresponding repositories into them, based on mappings defined in the configuration.

5. **CAST Highlight Onboarding:**  
   Triggers CAST Highlight analysis for each application using the Highlight Automation Command (Java JAR). Supports multi-threaded batch processing for efficiency.

6. **Log Parsing (Optional):**  
   The tool can parse CAST Highlight logs to extract and summarize results, using the HLLogParser module.

---

## Prerequisites

- **Python 3.x** (with `pip`)
- **Java Development Kit (JDK)**
- **Perl** (for Highlight Code Reader, if required)
- **CAST Highlight Automation Command** (Java JAR)
- **Internet Connectivity** (for GitHub and Highlight API access)
- **GitHub Personal Access Token** (with repo access)
- **CAST Highlight API Token**

---

## Installation

1. **Clone the Repository:**
   ```sh
   git clone <repo-url>
   cd CASTHLAutomation-main
   ```

2. **Set Up Python Environment:**
   ```sh
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Properties:**
   - Edit `Config/config.properties` with your environment-specific paths, tokens, and settings.
   - (Optional) Edit `HLLogParser/config.properties` for log parsing.

4. **Prepare Input Files:**
   - Ensure `App-Repo-Mapping.xlsx` and `applications.txt` are present in the `Config` directory.

---

## Usage

1. **Navigate to the `src` Directory:**
   ```sh
   cd src
   ```

2. **Run the Main Script:**
   ```sh
   python CASTHL_Automation.py
   ```

3. **Follow Interactive Prompts:**
   The script will prompt you to select a step:
   ```
	1. Download Metadata for GitHub organization.
	2. Download source code for all repositories in the organization in batches.
	3. Unzip the downloaded source code.
	4. Create application folders and move repositories.
	5. Copy or Append Mainframe folder to analyzed directory.
	6. Get applications long path.
	7. Trigger CAST Highlight onboarding for the source code.
	8. Run all the steps in one go from 1 to 7.
   ```
   Enter the step number to execute. You can run steps individually or in sequence.

4. **Monitor Progress:**
   - Console output provides real-time status.
   - Detailed logs are written to the directory specified in `logs_dir`.

---

## Configuration

Edit `Config/config.properties` with the following sections:

### [GitHub]
- `github_org_name`: GitHub Organization Name
- `github_token`: GitHub Personal Access Token
- `last_refresh_date`: Last refresh date (YYYY-MM-DD)

### [Directories]
- `config_dir`: Path to configuration files
- `src_dir`: Path to download source code ZIPs
- `unzip_dir`: Path to extract source code
- `logs_dir`: Path for log files
- `output_dir`: Path for output files
- `mainframe_src_folder`: (Optional) Path for mainframe sources
- `src_dir_analyze`: Path for source files to be analyzed
- `highlight_perl_dir`: Path to Perl installation
- `highlight_analyzer_dir`: Path to Highlight analyzer
- `RESULTS`: Path for analysis results

### [Input-File]
- `App_Repo_Mapping`: Path to `App-Repo-Mapping.xlsx`
- `Keyword_Scan`: Path to `KeywordScan.xml`

### [HIGHLIGHT-ONBOARDING]
- `highlight_application_mapping`: Path to `applications.txt`
- `highlight_base_url`: CAST Highlight base URL
- `highlight_executable`: Path to `HighlightAutomation.jar`
- `highlight_company_id`: Company ID
- `highlight_token`: Highlight API token
- `MAX_BATCHES`: Maximum number of batches (<=20)

### Ignored Settings (Do Not Change)
- `IGNORED_DIR`, `IGNORED_PATHS`, `IGNORED_FILES`: Directories, paths, and files to ignore during analysis.

### HLLogParser/config.properties (for log parsing)
- `root_directory`: Path to HL Automation logs
- `output_directory`: Path to HL Parser logs
- `bearer_token`: API token
- `api_url`: Highlight API URL
- `CompanyID`: Company ID

---

## Output

- **Repositories_Summary.csv:** Metadata for all repositories.
- **Log Files:** Detailed logs for each step and thread.
- **Console Output:** Real-time progress and error messages.
- **Analysis Results:** Output files in the specified `RESULTS` directory.

---

## Troubleshooting

- Ensure all paths in `config.properties` are correct and accessible.
- Check internet connectivity for GitHub and Highlight API access.
- Review log files for detailed error messages.
- Ensure all prerequisites (Python, Java, Perl, Highlight JAR) are installed and configured.

---

## Notes

- Supports multi-threaded batch processing for efficiency.
- Modular: You can run each step independently.
- Ensure proper permissions for all directories and files.
- For security, do not commit your tokens or sensitive configuration to version control.

---

## Sample Workflow

```sh
cd src
python CASTHL_Automation.py
# Enter step numbers as prompted (1-8)
```

---

For more details, refer to the comments and docstrings in the source
