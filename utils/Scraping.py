from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup

from dotenv import dotenv_values
from tqdm import tqdm
import time
from random import randint
import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd


def glints_login(browser, email_glints, password_glints) -> bool:
    """Function to login to glints.com using Selenium WebDriver.
    This function automates the login process by filling in the email and password fields from the .env file.
    Args:
        browser (webdriver): Selenium WebDriver instance.
        email_glints (str): email address for glints login
        password_glints (str): password for glints login
    Returns:
        bool: True if login is successful, False otherwise.
    """
    total_steps = 7
    max_waiting_time = 15 # seconds
    try:
        print("\nOpening browser...")
        
        with tqdm(total=total_steps, desc="Login Process",colour="green", ncols=200, unit="step") as pbar:

            browser.get("https://glints.com/id/login")
            pbar.update(1) # open link   1

            WebDriverWait(browser, max_waiting_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.LinkStyle__StyledLink-sc-usx229-0:nth-child(3)"))
            ).click() 
            pbar.update(1) # klik tombol "Masuk dengan Email"   2

            WebDriverWait(browser, max_waiting_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#login-form-email"))
            ).send_keys(email_glints) 
            pbar.update(1) # isi email  3        

            WebDriverWait(browser, max_waiting_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#login-form-password"))
            ).send_keys(password_glints) 
            pbar.update(1) # isi password   4

            WebDriverWait(browser, max_waiting_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ButtonStyle__SolidShadowBtn-sc-jyb3o2-3"))
            ).click()   
            pbar.update(1) # klik tombol "Masuk"    5

            WebDriverWait(browser, max_waiting_time).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".UserMenuComponentssc__NameHolder-sc-ovl5x6-4"))
                ))  
            pbar.update(1) # cek apakah profil sudah muncul  6

            if browser.find_elements(By.CSS_SELECTOR, ".UserMenuComponentssc__NameHolder-sc-ovl5x6-4"):
                pbar.update(1) # jika sudah muncul maka login berhasil  7
                # print("\nLogin successful!")
                return True
            else:
                print("\nAuthentication Error: Invalid credentials detected")
                return False
            
    except TimeoutException:
        print("\nNetwork Error: Timeout during login process")
        return False
    except Exception as e:
        print(f"\nSystem Error: Login failed - {str(e)}")
        return False
    

def request_page(job_title:str, page_num:int, browser:webdriver) -> BeautifulSoup:
    """Function to request a raw data html page from glints.com using Selenium WebDriver.
    This function automates the process of navigating to a specific job search page and retrieving its HTML content.
    Args:
        job_title (str): job_title to search for
        page_num (int): page number to request
        browser (webdriver): Selenium WebDriver instance.

    Returns:
        BeautifulSoup: raw page content of the requested page
    """
    try:
        # Random delay to avoid rate limiting
        time.sleep(randint(1, 5))
        
        url = f"https://glints.com/id/opportunities/jobs/explore?keyword={job_title}&country=ID&locationName=All+Cities%2FProvinces&lowestLocationLevel=1&page={page_num}"
        browser.get(url)

        WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.JobCardsc__JobcardContainer-sc-hmqj50-0"))
        )
        
        # browser.save_screenshot(f"page_{page_num}.png")  # Save screenshot for debugging
        html = browser.page_source
        soup = BeautifulSoup(html, "html.parser")
        return soup.find(id="__next")
        
    except TimeoutException:
        print(f"\nTimeout loading page {page_num} for '{job_title}'. Skipping...")
        return None
    except WebDriverException as e:
        print(f"\nBrowser error on page {page_num} for '{job_title}': {str(e)}. Skipping...")
        return None
    except Exception as e:
        print(f"\nUnexpected error loading page {page_num} for '{job_title}': {str(e)}. Skipping...")
        return None

def get_job_link_page(raw_page:BeautifulSoup) -> list:
    """Function to extract all job links from single page of glints.com.
    Args:
        raw_page (BeautifulSoup): raw page content of the requested page

    Returns:
        list: list of job links found on the page
    """
    if not raw_page:
        return []
        
    jobs = raw_page.find_all("div", class_="JobCardsc__JobcardContainer-sc-hmqj50-0 iirqVR CompactOpportunityCardsc__CompactJobCardWrapper-sc-dkg8my-5 hRilQl")
    links = []
    
    for job in jobs:
        job_link = job.find("a", class_="CompactOpportunityCardsc__JobCardTitleNoStyleAnchor-sc-dkg8my-12 jHptbP", href=True)
        if job_link and 'href' in job_link.attrs:
            links.append(job_link['href'])
            
    return links

def collect_job_links(browser:webdriver, job_title:str, limit:int=None) -> list:
    """Function to collect job links from multiple pages of glints.com.
    Args:
        browser (webdriver): Selenium WebDriver instance.
        job_title (str): job_title to search for
        limit (int, optional): limit pages . Defaults to None.

    Returns:
        list: list of job links found on the pages
    """
    print(f"\nAnalyzing job market for: {job_title} ...")

    #--------------------------- - 1. Get links from the first page
    all_jobs_link = []
    first_raw_page = request_page(job_title, 1, browser)
    if not first_raw_page:
        print(f"No matches found for '{job_title}', or there was an error loading the first page.")
        return []

    first_page_links = get_job_link_page(first_raw_page)
    all_jobs_link.extend(first_page_links)
    print(f"\nFound {len(first_page_links)} job listings on the first page.")

    #--------------------------- - 2. Check tombol next page
    next_page_button = first_raw_page.find_all("button", class_="UnstyledButton-sc-zp0cw8-0 AnchorPaginationsc__Number-sc-8wke03-3 dYSdtB bkvUQn")
    if not next_page_button:
        print(f"Retrieved {len(all_jobs_link)} job listings from this page.")
        return all_jobs_link
    
    #--------------------------- - 3. Iterasi ke halaman selanjutnya dan ambil link
    try:
        last_page_num = int(next_page_button[-1].get_text())
        max_page_num = limit if limit is not None and limit < last_page_num else last_page_num 

        print(f"Discovered {last_page_num} pages of job listings, capping the process at {max_page_num} pages.")

        for page_num in tqdm(range(2, max_page_num+1), desc=f"Collecting {max_page_num-1} remaining pages", colour='green', ncols=200, unit="page"):
            page = request_page(job_title, page_num, browser)
            if page:
                page_links = get_job_link_page(page)
                all_jobs_link.extend(page_links)
            # Continue to next page even if current page failed
            
        print(f"Successfully gathered {len(all_jobs_link)} job listings")
        return all_jobs_link
        
    except (ValueError, IndexError) as e:
        print(f"Error parsing pagination: {str(e)}")
        return all_jobs_link  # Return whatever links we've collected so far

def extract_text(soup, selector, default=None):
    """Helper function to safely extract text from a CSS selector"""
    element = soup.select_one(selector)
    return element.get_text() if element else default

def extract_job_details(url:str, browser:webdriver)-> dict:
    """Function to extract job details from a job url.
    This function automates the process of navigating to a specific job page and extracting its details.

    Args:
        url (str): job url to extract details from
        browser (webdriver): Selenium WebDriver instance.

    Returns:
        dict: dictionary containing job details
    """
    base_url = "https://glints.com" + url

    try:
        browser.get(base_url)
        time.sleep(randint(1, 5))  # Random delay to avoid rate limiting
        WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".TopFoldsc__JobOverViewTitle-sc-1fbktg5-3"))
        ) # Nama pekerjaan

        html = browser.page_source
        soup = BeautifulSoup(html, "html.parser")
        page = soup.find(id="__next")
        
        if not page:
            return None

        job_name = extract_text(page, "h1.TopFoldsc__JobOverViewTitle-sc-1fbktg5-3", "No Title")
        education = extract_text(page, "div.TopFoldsc__JobOverViewInfo-sc-1fbktg5-9:nth-child(4) > span", "No Requirement")
        job_type = extract_text(page, "div.TopFoldsc__JobOverViewInfo-sc-1fbktg5-9:nth-child(3)", "Unspecified")
        experience = extract_text(page, "div.TopFoldsc__JobOverViewInfo-sc-1fbktg5-9:nth-child(5)", "No Requirement")
        salary = extract_text(page, ".TopFoldsc__BasicSalary-sc-1fbktg5-13", "Unspecified")
        post_time = page.find("span", class_="TopFoldsc__PostedAt-sc-1fbktg5-12 fcmpfD").get_text(strip=True)
        post_time = post_time.replace("Tayang ","")

        list_skill = []
        container_skill = page.find("div", class_="Opportunitysc__SkillsContainer-sc-gb4ubh-10 jccjri")
        if container_skill:
            list_skill = [element.get_text(strip=True) for element in container_skill.find_all("span") if element.get_text(strip=True)]

        requirements = []
        extra_requirements = page.find_all("div", class_="TagStyle-sc-r1wv7a-4 bJWZOt JobRequirementssc__Tag-sc-15g5po6-3 cIkSrV")
        if extra_requirements and len(extra_requirements) > 3:
            requirements = [req.get_text() for req in extra_requirements[3:] if req]

        
        province = extract_text(page, "label.BreadcrumbStyle__BreadcrumbItemWrapper-sc-eq3cq-0:nth-child(3) > a", "Unspecified")
        city = extract_text(page, "label.BreadcrumbStyle__BreadcrumbItemWrapper-sc-eq3cq-0:nth-child(4) > a", "Unspecified")
        district = extract_text(page, "label.BreadcrumbStyle__BreadcrumbItemWrapper-sc-eq3cq-0:nth-child(5) > a", "Unspecified")

        company_name = extract_text(page, ".AboutCompanySectionsc__Title-sc-c7oevo-6 > a", "Unspecified")
        company_industry = extract_text(page, ".AboutCompanySectionsc__CompanyIndustryAndSize-sc-c7oevo-7 > span:nth-of-type(1)", "Unspecified")
        company_size = extract_text(page, ".AboutCompanySectionsc__CompanyIndustryAndSize-sc-c7oevo-7 > span:nth-of-type(2)", "Unspecified")
        
        return {
            "job name": job_name,
            "job type": job_type,
            "salary range": salary,
            "salary min": pd.Series(salary).str.extract(r'IDR([\d\.]+)\s*-\s*\d+')[0].str.replace('.', '').astype(float).values[0],
            "salary max": pd.Series(salary).str.extract(r'IDR[\d\.]+\s*-\s*([\d\.]+)')[0].str.replace('.', '').astype(float).values[0],
            "skills requirements": ", ".join(list_skill),
            "education requirements": education,
            "experience requirements": experience,
            "another requirements": ", ".join(requirements),
            "province": province,
            "city": city,
            "district": district,
            "company name": company_name,
            "company industry": company_industry,
            "company size": company_size,
            "last post": post_time,
            "post time": exctract_time(post_time),
            "obtained": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "url": base_url,
        }

    except TimeoutException:
        print(f"Timeout while loading job details for {base_url}")
        return None
    except Exception as e:
        print(f"\nError extracting job details for {base_url}: {str(e)}")
        return None

def split_extract_running(links:list,split:int) -> list:
    total_links = len(links)
    return [links[i:i+split] for i in range(0, total_links, split)]

def extract_all_job_details(links:list, browser:webdriver, split:int=60) -> list:
    """Function to extract job details from multiple job links.
    This function automates the process of navigating to each job page and extracting its details.

    Args:
        links (list): list of job links to extract details from
        browser (webdriver): Selenium WebDriver instance.
        split (int, optional): number of links to process in each batch. Defaults to 60.

    Returns:
        list: list of dictionaries containing job details
    """
    #--------------------------- - 1. Atur pembagian running
    if split > len(links):
        print(f"Split value {split} is greater than the number of links {len(links)}")
        # return []
        

    splited_links = split_extract_running(links, split)
    print(f"\nSplitting {len(links)} job links into {len(splited_links)} batches for the job detail extraction process.")

    #--------------------------- - 2. Menjalankan running tiap batch
    jobs = []
    for i, list_link in enumerate(splited_links,start=1):

        time.sleep(randint(3, 8))  # Random delay to avoid rate limiting
        for link in tqdm(list_link, desc=f"(Batch {i}) Fetching full job details" ,ncols=200, unit="step"):
            job_details = extract_job_details(link, browser)
            if job_details:
                jobs.append(job_details)
    return jobs

def exctract_time(post_time):

    if "menit" in post_time.lower():
        minute = int(post_time.split(" ")[0])
        post_time = dt.datetime.now() - pd.Timedelta(minutes=minute)
        return post_time.strftime("%Y-%m-%d %H:%M:%S")
    
    elif "jam" in post_time.lower():
        hour = int(post_time.split(" ")[0])
        post_time = dt.datetime.now() - pd.Timedelta(hours=hour)
        return post_time.strftime("%Y-%m-%d %H:%M:%S")
    
    elif "kemarin"in post_time.lower():
        post_time = dt.datetime.now() - pd.Timedelta(days=1)
        return post_time.strftime("%Y-%m-%d %H:%M:%S")
        
    elif "hari" in post_time.lower():
        day = int(post_time.split(" ")[0])
        post_time = dt.datetime.now() - pd.Timedelta(days=day)
        return post_time.strftime("%Y-%m-%d %H:%M:%S")
    
    elif "bulan" in post_time.lower():
        month = int(post_time.split(" ")[0])
        post_time = dt.datetime.now() - relativedelta(months=month)
        return post_time.strftime("%Y-%m-%d %H:%M:%S")
    
    elif "tahun" in post_time.lower():
        year = int(post_time.split(" ")[0])
        post_time = dt.datetime.now() - relativedelta(years=year)
        return post_time.strftime("%Y-%m-%d %H:%M:%S")
    
    else:
        return None
        

if __name__ == "__main__":
    
    email_glints = dotenv_values("../privacy/.env").get("GLINTS_EMAIL")
    password_glints = dotenv_values("../privacy/.env").get("GLINTS_PASSWORD")

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

        result = extract_all_job_details(all_links, browser, split=500)
        if not result:
            print("No job details found")
            browser.quit()
            exit()
        df = pd.DataFrame(result)

        # save to csv_______________________________________________
        df.to_csv(f"Glints_{job_title}.csv", index=False)
        print(f"\nSuccessfully saved to CSV file, name: Glints_{job_title}.csv")

    except KeyboardInterrupt:
        print("\n\nUser interruption detected. Stopping...")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        print("The program is now shutting down properly.")
    finally:
        browser.quit()
        print("Browser session terminated\n")
