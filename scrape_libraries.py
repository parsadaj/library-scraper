import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import json
import time

# Base URL of the library listings
base_url = "https://lib.ir/fa/libraries/p"
libraries = []

def send_request(url, msg):
    while True:
        tried = 0
        try:
            response = requests.get(url)
        except Exception as e:
            tried += 1
            if tried < 15:
                print(e)
                print(msg)
                time.sleep(2)
                continue
            else:
                raise e
        if response.status_code == 200:
            return response
        elif response.status_code == 500:
            print(msg)
            time.sleep(2)
        else:
            raise
    

# Function to get the number of pages
def get_number_of_pages():
    response = send_request(f"{base_url}1/", msg="Retrying retrieveing number of pages...")
    soup = BeautifulSoup(response.content, 'html.parser')
    pagination = soup.find('ul', class_='pagination')
    last_page_link = pagination.find_all('a')[0]['href']
    total_pages = int(last_page_link.split('/')[-1][1:])
    print(f"Total number of pages found: {total_pages}")
    return total_pages

# Function to scrape library details
def scrape_library_details(library_url, page_number, lib_number):
    response = send_request(library_url, msg=f"Retrying request for library: {lib_number+1} in page {page_number}...")


    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the necessary information
    library_title = soup.find('h1').find('a').text.strip() if soup.find('h1') else 'N/A'
    location = soup.find('h2', id='liblocation').text.strip() if soup.find('h2', id='liblocation') else 'N/A'
    
    # Extract the website URL from the span
    spans =soup.find_all('span')
    website = 'N/A'
    for span in spans:
        if span.find('a') and "http" in span.find('a')['href']:
            website = span.find('a')['href']
            break
    
    phone_number = soup.find_all('div', class_='libinfo')[0].find_all('div')[2].text.strip() if soup.find_all('div', class_='libinfo') and len(soup.find_all('div', class_='libinfo')[0].find_all('div')) > 2 else 'N/A'
    address = soup.find_all('div', class_='libinfo')[2].find_all('div')[3].text.strip() if soup.find_all('div', class_='libinfo') and len(soup.find_all('div', class_='libinfo')[1].find_all('div')) > 3 else 'N/A'
    
    province, city = None, None
    if location != 'N/A':
        province = location.split('شهر:')[0].strip().split('استان:')[1].strip()[:-1].strip()
        city = location.split('شهر:')[1].strip()

    return {
        'province': province if province else 'N/A',
        'city': city if city else 'N/A',
        'address': address[7:].strip(),
        'phone_number': phone_number[11:].strip(),
        'website': website,
        'url':library_url
    }

# Function to scrape libraries from the list pages
def scrape_libraries(page_number):
    print(f"Scraping page {page_number}...")
    response = send_request(f"{base_url}{page_number}/", msg=f"Retrying request for page {page_number}...")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    table = soup.find('div', class_='table-responsive')
    if table:
        rows = table.find_all('tr')[1:]  # Skip the header row

        for lib_number, row in enumerate(rows):
            columns = row.find_all('td')
            if columns:
                library_name = columns[1].find('a').text.strip()
                library_link = "https://lib.ir" + columns[1].find('a')['href']
                print(f"Scraping details for library: {lib_number+1} in page {page_number}...")
                library_info = scrape_library_details(library_link, page_number, lib_number)
                libraries.append({
                    'name': library_name,
                    **library_info
                })



# Get the total number of pages
total_pages = get_number_of_pages()

# Scrape multiple pages
for page in range(1, total_pages + 1):
    scrape_libraries(page)

# Save the libraries data to a CSV file
df = pd.DataFrame(libraries)
df.to_csv('libraries.csv', index=False)
print("CSV file created successfully!")

# Save the libraries data to a JSON file for the GitHub repository
with open('libraries.json', 'w', encoding='utf-8') as f:
    json.dump(libraries, f, ensure_ascii=False, indent=4)
print("JSON file created successfully!")
