# Scraping and Visualizing Data Science Job Market Trends from Glints
---
## 1. Project Overview 📌
This project automates job data extraction for Data Scientist roles from Glints using Selenium. It collects job details like titles, descriptions, salary ranges, and skills, helping researchers and job seekers analyze market trends and skill requirements. The data will be stored in Google Big Query and visualized using Looker Studio, providing insights into salaries, in-demand skills, and geographic distribution. This approach saves time for professionals and companies in research or recruitment.

## Project Description 
The data in this dataset was collected through web scraping from the Glints job portal. The scraper uses Selenium WebDriver to automate the browsing and data extraction process. Selenium is used to log in, search for job vacancies, and extract details such as job titles, salary ranges, required skills, and other metadata related to each job posting.

Process Overview:
1. Login: The scraper first logs into Glints using predefined credentials.
2. Search: After logging in, it searches for jobs with the title “Data Scientist.”
3. Scraping: Once the search results page loads, the scraper collects all job listing URLs.
4. Detail Extraction: For each job URL, detailed information such as job title, salary range, skills, etc., is extracted.
5. Data Storage: The extracted data is stored in a CSV file, including a timestamp to indicate when the data was scraped.

This dataset contains job postings for positions related to “Data Scientist” from [Glints](https://glints.com/id), a job portal based in Indonesia. The data was obtained through automated scraping of job listing pages on the Glints Indonesia website. By default the job search keyword is “Data Scientist” but you can change the search keyword.

## Dataset Column Descriptions
1. `Job Name`: The job title (e.g., Data Scientist, Lead Data Scientist).
2. `Job Type`: The nature of the job offered (e.g., Full Time, Contract, Hybrid).
3. `Salary Range`: The salary range offered for the position, often with units (e.g., "IDR7,000,000 - 10,000,000/Month").
4. `Salary Min`: Minimum salary offered for the job.
5. `Salary Max`: Maximum salary offered for the job.
6. `Skills Requirements`: Skills required for the role (e.g., Python, SQL, AWS).
7. `Education Requirements`: Minimum education level required (e.g., "Bachelor's Degree").
8. `Experience Requirements`: Required years of work experience (e.g., "1 - 3 years").
9. `Other Requirements`: Additional requirements such as age limits or specific certifications.
10. `Province`: The province where the job is located (e.g., DKI Jakarta, Yogyakarta, Banten).
11. `City`: The city of the job location (e.g., South Jakarta, South Tangerang).
12. `District`: The district within the city (e.g., Tebet, Ciputat).
13. `Company Name`: The name of the hiring company.
14. `Company Industry`: The industry in which the company operates (e.g., Information Technology, Telecommunications).
15. `Company Size`: The company’s size based on number of employees (e.g., 51 - 200 employees).
16. `Last Post`: The date the job listing was last posted or updated.
17. `Post Time`: The original date and time when the job was posted.
18. `Obtained`: The timestamp indicating when the data was scraped.
19. `URL`: The direct link to the job listing page.

## Requirements
The required Python libraries are listed in the requirements.txt file. To install the dependencies, simply run:
```
pip install -r requirements.txt
```
## Setup
1. Environment Variables<br>
Create a `.env` file in the `privacy/` folder to store sensitive information. Here's an example `.env` format:
    ```
    GLINTS_EMAIL=your_email@example.com
    GLINTS_PASSWORD=your_password
    PROJECT_ID=your_google_project_id
    DATASET_ID=your_bigquery_dataset_id
    KEY_JSON=your_service_account_key.json
    ```
2. Google Cloud service account JSON <br>
Make sure you put the Google Cloud service account JSON file into the `privacy/` folder.

## Project Structure
```.
├── privacy/
│   ├── your_service_account_key.json   # Google Cloud service account
│   └── .env                            # Environment variables
├── utils/
│   ├── Cleaning_and_storing.py         # Functions to clean and store data
│   └── Scraping.py                     # Functions to scrape job data
├── data/                               # Folder for storing raw and 
│                                         processed data (e.g., CSV files)
├── report/
│   ├── looker_link.txt                 # Looker Studio Dashboard
│   └── pptx file                       # Power Point Presentation file
├── main.py                             # Main execution script
├── requirements.txt                    # All requirements libraries
└── README.md                           # This readme
```

## Running the Script
To run the script, execute the following command in your terminal:
```
python main.py
```
What the script does:
1. Login to Glints using the credentials from the .env file.
2. Scrape job listings for the job title from keyword and collect relevant links.
3. Extract job details (e.g., job title, company, post time, etc.) from the collected links
4. Clean the data
5. Upload the cleaned data to Google BigQuery using the Google Cloud credentials.

Key Functions:
* `glints_login()`: Logs into Glints using provided email and password.
* `collect_job_links()`: Gathers job listing links based on the job title.
* `extract_all_job_details()`: Extracts details like job title, company, location, post time, etc.
* `cleaning_nan()`: Cleans rows with missing values in the dataset.
* `filter_relevan_job()`: Filters job listings that match relevant keywords like "data", "scientist", "machine learning", etc.
* `upload_gbq()`: Uploads the processed data to Google BigQuery.

## 7. Contact 
* **Nama**: Muhammad Khisanul Fakhrudin Akbar
* **Email** : shinaruikhisan@gmail.com
* **Linkedin** : https://www.linkedin.com/in/muhammad-khisanul-fakhrudin-akbar/