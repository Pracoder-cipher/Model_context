import os
import pandas as pd
import requests
import argparse
from datetime import datetime
import sys

sys.path.append(os.path.dirname(__file__))

selected_buildID = None
if "SWCONF_API_KEY" in os.environ:
    apiKey = os.environ["SWCONF_API_KEY"]

# Stability processing functions
def calculate_stability_status(test_case_results):
    """Calculates the stability status as a single formatted string."""
    valid_results = [r for r in test_case_results if r in {"OK", "NOK", "Not run"}]
    if not valid_results:
        return "No Data"

    total = len(valid_results)
    ok_percentage = round((valid_results.count("OK") / total) * 100, 2)
    nok_percentage = round((valid_results.count("NOK") / total) * 100, 2)
    not_run_percentage = round((valid_results.count("Not run") / total) * 100, 2)

    if set(valid_results) == {"OK"}:
        stability = "Stable (OK)"
    elif set(valid_results) == {"NOK"}:
        stability = "Stable (NOK)"
    elif set(valid_results) == {"Not run"}:
        stability = "Stable (Not run)"
    elif set(valid_results) == {"NOK", "Not run"}:
        stability = "Stable (NOK)"
    else:
        stability = "Unstable"

    status_parts = []
    if ok_percentage > 0:
        status_parts.append(f"{ok_percentage}% OK")
    if nok_percentage > 0:
        status_parts.append(f"{nok_percentage}% NOK")
    if not_run_percentage > 0:
        status_parts.append(f"{not_run_percentage}% Not Run")

    status_text = ", ".join(status_parts)

    return f"{stability} - {status_text}"
def generate_master_sheet(extracted_data_dir, stability_data_dir, output_file):
    """
    Generates a master sheet, and calculates stability.
    """
    print(f"Extracted Data Directory: {extracted_data_dir}")
    print(f"Stability Data Directory: {stability_data_dir}")

    if not os.path.exists(extracted_data_dir):
        raise FileNotFoundError(f"Extracted data directory not found: {extracted_data_dir}")
    if not os.path.exists(stability_data_dir):
        raise FileNotFoundError(f"Stability data directory not found: {stability_data_dir}")

    extracted_files = [f for f in os.listdir(extracted_data_dir) if f.endswith('.xlsx')]
    print(f"Excel files found: {extracted_files}")
    print("All files in extracted_data_dir:", os.listdir(extracted_data_dir))

    dataframes = []
    for file in extracted_files:
        file_path = os.path.join(extracted_data_dir, file)
        try:
            xlsx = pd.ExcelFile(file_path)
            for sheet_name in xlsx.sheet_names:
                df = pd.read_excel(xlsx, sheet_name=sheet_name)
                df['Source_File'] = file
                df['Sheet_Name'] = sheet_name
                dataframes.append(df)
        except Exception as e:
            print(f"Failed to read {file_path}: {e}")

    if not dataframes:
        raise ValueError("No Excel data found to process in the extracted data directory.")

    master_df = pd.concat(dataframes, ignore_index=True)

    # *** Stability Calculation Start ***
    # Pivot the DataFrame to get test results per file
    pivot_df = master_df.pivot_table(
        index='TestCase_Name',
        columns='Source_File',
        values='TestCase_Result',  # Make sure this is the correct column name
        aggfunc='first',
        fill_value="" #important
    )

    # Calculate stability status for each test case
    pivot_df['Stability_Status'] = pivot_df.apply(
        lambda row: calculate_stability_status(row.dropna().values), axis=1
    )
    # Merge the stability data back into the master dataframe.  Important to keep other columns
    master_df = master_df.merge(pivot_df['Stability_Status'], left_on='TestCase_Name', right_index=True, how='left')

    # *** Stability Calculation End ***
    stability_master_sheet_path = os.path.join(stability_data_dir, output_file)
    master_df.to_excel(stability_master_sheet_path, index=False) # index=False prevents extra index column
    print(f"Stability master sheet generated at: {stability_master_sheet_path}")

    return stability_master_sheet_path


def push_stability_data_to_artifactory(
    stability_data_repo_path,
    filename,
    stability_file_path,
    stability_data_url,
    username,
    password
):
    target_path = f"{stability_data_repo_path}/{filename}"
    if not os.path.exists(stability_file_path):
        raise FileNotFoundError(f"Error: File not found at {stability_file_path}")
    url_to_push = f"{stability_data_url}/{target_path}"  # Corrected URL construction.
    print(f"URL_To_Artifactory: {url_to_push}")
    try:
        with open(stability_file_path, "rb") as file:
            response = requests.put(
                url_to_push,
                data=file,
                auth=(username, password),
                headers={"Authorization": f"ApiKey {apiKey}"},
            )
        # Handle response
        if response.status_code == 201:
            print("File pushed successfully!")
        else:
            print(f"Failed to push file. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", dest="OptStabilityDataRepoPath", default=None, required=True, metavar=None, help="")
    parser.add_argument("-o", dest="OptOutputFile", required=True, help="Output Filename")
    parser.add_argument("-g", dest="OptStabilityDataDir", required=True, help="Stability Dir Path")
    parser.add_argument("-S", dest="OptStabilityDataUrl", default=None, required=True, metavar=None, help="Artifactory URL")
    parser.add_argument("-U", dest="OptUsername", default=None, required=True, metavar=None, help="Username")
    parser.add_argument("-P", dest="OptPassword", default=None, required=True, metavar=None, help="Password")
    parser.add_argument("-x", dest="OptExtractDataDir", required=True, help="Extract Dir Path")
    args = parser.parse_args()

    stability_data_repo_path = args.OptStabilityDataRepoPath
    output_file = args.OptOutputFile
    stability_data_dir = args.OptStabilityDataDir
    stability_data_url = args.OptStabilityDataUrl
    username = args.OptUsername
    password = args.OptPassword
    extracted_data_dir = args.OptExtractDataDir
    stability_file_path = os.path.join(stability_data_dir, output_file)

    # 1. Generate the master sheet (which now includes stability)
    generated_file_path = generate_master_sheet(extracted_data_dir, stability_data_dir, output_file)

    # 2. Push the generated file to Artifactory
    push_stability_data_to_artifactory(stability_data_repo_path, output_file, generated_file_path, stability_data_url, username, password)



if __name__ == "__main__":
    main()
