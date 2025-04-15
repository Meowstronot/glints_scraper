import os
from utils.Scraping import *
from utils.Cleaning_and_storing import *



if __name__ == "__main__":
    
    env_data = dotenv_values("privacy/.env")
    # ---- Glints Configuration
    email_glints = env_data.get("GLINTS_EMAIL")
    password_glints = env_data.get("GLINTS_PASSWORD")

    # ---- BigQuery Configuration
    project_id = env_data.get("PROJECT_ID")
    dataset_id = env_data.get("DATASET_ID")
    key_json = env_data.get("KEY_JSON")
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "privacy", key_json)
    # print(key_path)

    try:
        # Konfigurasi Browser________________________________________ 1
        options = Options()
        options.add_argument("--headless")
        # options.headless = True
        options.set_preference('network.proxy.type', 0)  # Nonaktifkan proxy
        options.set_preference("general.useragent.override", 
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
        browser = webdriver.Firefox(options=options)

        # Proses Login_______________________________________________ 2
        if glints_login(browser, email_glints, password_glints):
            print("Login success!!")
        else:
            print("Login failed!!")
            browser.quit()
            exit()

        # Scraping Data_____________________________________________ 3
        job_title = "Data Scientist"
        all_links = collect_job_links(browser, job_title, limit=1)
        print(f"\nTotal job found: {len(all_links)}")

        result = extract_all_job_details(all_links, browser, split=50)
        if not result:
            print("No job details found")
            browser.quit()
            exit()
        df = pd.DataFrame(result)

        # save to csv_______________________________________________ 4
        # df.to_csv(f"data/Glints_RAW.csv", index=False)
        # print(f"\nSuccessfully saved to CSV file, name: Glints_RAW.csv")

        # cleaning__________________________________________________ 5
        df = pd.read_csv("data/Glints_RAW.csv", parse_dates=['post_time', 'obtained'])
        print("\n Cleaning RAW data....")
        # clening NAN
        list_nan = cek_nan(df)
        df = cleaning_nan(df, list_na=list_nan)
        print(f"Cleaning NAN Succesfully: {df.shape[0]} baris, {df.shape[1]} kolom")
        # cleaning relevan job
        keywords = ['data', 'scientist', 'machine learning', 'big data', 'modeling', 'analytst', "analis"]
        df = filter_relevan_job(df,list_keyword=keywords)
        print(f"\nSuccessfully filter ({df.shape[0]}) data to relevan job")

        # Storing to Google Big Query______________________________ 6
        if not df.empty:
            print("\nUploading to Google Big Query...")
            upload_gbq(df,project_id,dataset_id,key_path=key_path)


    except KeyboardInterrupt:
        print("\n\nUser interruption detected. Stopping...")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        print("The program is now shutting down properly.")
    finally:
        browser.quit()
        print("Browser session terminated\n")
