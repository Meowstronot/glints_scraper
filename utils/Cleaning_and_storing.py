import numpy as np
import pandas as pd

import pandas_gbq
from google.oauth2 import service_account
from dotenv import dotenv_values
import os


# _________________________________________________________________________________________ Cleaning

def cek_nan(df:pd.DataFrame) -> list:
    """This function checks each column in the DataFrame for NaN values and prints the count 
    of NaN values found in each column. If any column contains NaN values, the results 
    will be displayed; otherwise, a message will be shown indicating no NaN values are detected.

    Args:
    df (pd.DataFrame): The DataFrame to be checked.

    Returns:
        list: A list of column names that contain NaN values.
    """
    all_col = df.isna().sum()
    col_na = all_col[all_col>0]

    if not col_na.empty:
        print("\nColumn NAN count")
        print(col_na)
    else:
        print("\nNo Column NAN Detected")

    return list(col_na.index)

def cleaning_nan(df:pd.DataFrame, list_na:list) -> pd.DataFrame:
    """This function cleans NaN values in the specified columns of the DataFrame based on the given conditions.

    For each column specified in `list_na`, the function performs the following operations:
    - Drops rows where `skills_requirements` is NaN.
    - Fills NaN in `salary_min` and `salary_max` based on conditions in `salary_range` (i.e., 'Unspecified' or range values).
    - Fills NaN in `another_requirements` with a default value of "No other requirements".
    - Fills NaN in `company_industry` with "Unspecified".

    Args:
    df (pd.DataFrame): The DataFrame to be cleaned.
    list_na (list): A list of column names to clean.

    Returns:
        pd.DataFrame: The cleaned DataFrame with NaN values handled.
    """
    df= df.copy()
    for val in list_na:
        
        if val == "skills_requirements":
            df = df.dropna(subset=['skills_requirements'])

        elif val == "salary_min":
            # jika kosong dan kolom salary_range = Unspecified
            df.loc[df['salary_min'].isna() & (df['salary_range'] == 'Unspecified'), 'salary_min'] = 0
            # jika masih kosong dan kolom salary range tidak berbentuk range tapi 1 nilai saja
            df["salary_min"] = df["salary_min"].fillna(df["salary_range"].str.extract(r'IDR([\d\.]+)\/Bulan')[0].str.replace('.', '').astype(float))
        elif val == "salary_max":
            df.loc[df['salary_max'].isna() & (df['salary_range'] == 'Unspecified'), 'salary_max'] = 0
            df["salary_max"] = df["salary_max"].fillna(df["salary_range"].str.extract(r'IDR([\d\.]+)\/Bulan')[0].str.replace('.', '').astype(float))

        elif val == "another_requirements":
            df["another_requirements"] = df["another_requirements"].fillna("No other requirements")
            
        elif val == "company_industry":
            df["company_industry"] = df["company_industry"].fillna("Unspecified")

    cek_nan(df)
    return df

# _________________________________________________________________________________________ Storing

def upload_gbq(df:pd.DataFrame , project_id:str, dataset_id:str, key_path:str) -> None:
    """Uploads data from a pandas DataFrame to Google BigQuery tables. The function uploads two tables:
    - The main DataFrame `df` to the "Glints" table.
    - A table with skills counts (from the "skills_requirements" column) to the "Skills" table.

    Args:
    df (pd.DataFrame): The main DataFrame to be uploaded.
    project_id (str): The Google Cloud Project ID.
    dataset_id (str): The BigQuery Dataset ID.
    key_path (str): Path to the service account key file for authentication.

    Returns:
        None
    """

    # ---- Credential configuration
    scopes = ["https://www.googleapis.com/auth/bigquery"]
    credentials = service_account.Credentials.from_service_account_file(filename=key_path, scopes=scopes) 

    # print("Google BigQuery Configuration")
    # print(f"Project ID: {project_id}")
    # print(f"Dataset ID: {dataset_id}")
    # print(f"Key Path: {key_path}")

    table_skill = df["skills_requirements"].str.split(",",expand=True).stack().str.strip().value_counts().reset_index()
    list_table = {"Glints": df, 
            "Skills": table_skill}

    for table_name, table in list_table.items():
        # Upload DataFrame to BigQuery
        pandas_gbq.to_gbq(
            dataframe=table,
            destination_table=f"{dataset_id}.{table_name}",
            project_id=project_id,
            if_exists="replace",
            credentials=credentials
        )
        print(f"Table {table_name} uploaded successfully!")

if __name__ == "__main__":

    # Mendapatkan main directory langsung
    main_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Membaca file CSV dengan path yang benar
    df = pd.read_csv(os.path.join(main_directory, "data", "Glints_RAW.csv"), parse_dates=['post_time', 'obtained'])
    print(type(df))

    list_nan = cek_nan(df)
    df = cleaning_nan(df, list_nan)
    print(df.shape)
