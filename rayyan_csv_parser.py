# Import packages
import os
import re  # for regular expressions
import pandas as pd
import numpy as np  # for np.nan

# Function to map decisions to codes
def map_decision(decision):
    if decision.lower() == "excluded":
        return 0
    elif decision.lower() == "included":
        return 1
    elif decision.lower() == "maybe":
        return 999
    else:
        return None

# Function to extract names and coded decisions from inclusion_status
def extract_decisions(inclusion_status):
    if pd.isnull(inclusion_status):
        return None
    decisions = re.findall(r'"(.*?)"\s*=>\s*"(.*?)"', inclusion_status)
    return {name: map_decision(decision) for name, decision in decisions}

# Function to search all columns in a row for inclusion status
def find_inclusion_status_in_row(row):
    for col in row.index:
        value = str(row[col])
        if pd.notnull(value):
            match = re.search(r'RAYYAN-INCLUSION:\s*({.*?})', value)
            if match:
                return match.group(1)
    return None

# Function to extract DOI link from a string
def extract_doi(url_string):
    if pd.isnull(url_string):
        return None
    # Regular expression pattern to match DOI URLs
    doi_pattern = r'(https?://(?:dx\.)?doi\.org/[^\s]+)'
    matches = re.findall(doi_pattern, url_string)
    if matches:
        # Return the first DOI link found
        return matches[0]
    else:
        return None

# Function to anonymize the reviewer names in coded_decisions
def anonymize_decisions(decisions, reviewer_mapping):
    if decisions is None:
        return None
    return {reviewer_mapping[reviewer]: decision for reviewer, decision in decisions.items()}

# List all .csv files in the current directory, excluding any that contain '_CLEAN.csv' to avoid reprocessing output files
csv_files = [file for file in os.listdir('.') if file.endswith('.csv') and '_CLEAN.csv' not in file]

# Loop through each CSV file in the list
for file_name in csv_files:
    print(f"Processing file: {file_name}")

    try:
        # Read the CSV file with semicolon separator
        df = pd.read_csv(file_name, sep=';', engine='python')
    except Exception as e:
        print(f"Error reading {file_name}: {e}")
        continue  # Skip to the next file if there's an error

    # Apply the function to each row to find inclusion_status
    df['inclusion_status'] = df.apply(find_inclusion_status_in_row, axis=1)

    # Check if all required columns are present
    required_columns = ['title', 'abstract', 'pubmed_id', 'url', 'notes', 'inclusion_status']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Skipping {file_name} due to missing columns: {missing_columns}")
        continue  # Skip this file if required columns are missing

    # Apply the function to the 'inclusion_status' column
    df['coded_decisions'] = df['inclusion_status'].apply(extract_decisions)

    # --- Anonymize Reviewer Names ---
    # Create mapping from reviewer names to 'Reviewer N' based on order of appearance
    reviewer_mapping = {}
    reviewer_counter = 1
    for decisions in df['coded_decisions']:
        if decisions is not None:
            for reviewer in decisions.keys():
                if reviewer not in reviewer_mapping:
                    reviewer_mapping[reviewer] = f'Reviewer {reviewer_counter}'
                    reviewer_counter += 1

    # Apply the anonymization to coded_decisions
    df['coded_decisions'] = df['coded_decisions'].apply(
        lambda decisions: anonymize_decisions(decisions, reviewer_mapping)
    )
    # --- End of Anonymization ---

    # Create the TI-AB column based on the coded_decisions
    df['TI-AB'] = df['coded_decisions'].apply(
        lambda decisions: np.nan if decisions is None or decisions == 'None' else (
            0 if decisions and all(decision == 0 for decision in decisions.values()) else 1
        )
    )

    # Extract DOI links from the 'url' column
    df['doi'] = df['url'].apply(extract_doi)

    # Select the relevant columns for final output
    df = df[['title', 'abstract', 'doi', 'TI-AB', "coded_decisions"]]

    # Export the df DataFrame to a CSV file with the modified name
    output_file_name = file_name.replace('.csv', '_CLEAN.csv')
    # Prepend output_file_name with 'TRAM_'
    output_file_name = 'TRAM_' + output_file_name
    df.to_csv(output_file_name, index=False, sep=";")

    # Display the name of the output file
    print(f"DataFrame exported to {output_file_name}\n")
