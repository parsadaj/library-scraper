import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import json

# Base URL of the library listings
base_url = "https://lib.ir/fa/libraries/p"
libraries = []

# Function to get the number of pages
def get_number_of_pages():
    response = requests.get(f"{base_url}1/")
    soup = BeautifulSoup(response.content, 'html.parser')
    pagination = soup.find('ul', class_='pagination')
    last_page_link = pagination.find_all('a')[0]['href']
    total_pages = int(last_page_link.split('/')[-1][1:])
    print(f"Total number of pages found: {total_pages}")
    return total_pages

# Function to scrape library details
def scrape_library_details(library_url):
    response = requests.get(library_url)
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
    address = soup.find_all('div', class_='libinfo')[1].find_all('div')[3].text.strip() if soup.find_all('div', class_='libinfo') and len(soup.find_all('div', class_='libinfo')[1].find_all('div')) > 3 else 'N/A'
    
    province, city = None, None
    if location != 'N/A':
        province, city = location.split('ـ')
        province = province.split(':')[1].strip() if ':' in province else province
        city = city.split(':')[1].strip() if ':' in city else city

    return {
        'province': province if province else 'N/A',
        'city': city if city else 'N/A',
        'address': address[7:].strip(),
        'phone_number': phone_number[11:].strip(),
        'website': website,
    }

# Function to scrape libraries from the list pages
def scrape_libraries(page_number):
    print(f"Scraping page {page_number}...")
    response = requests.get(f"{base_url}{page_number}/")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    table = soup.find('div', class_='table-responsive')
    if table:
        rows = table.find_all('tr')[1:]  # Skip the header row

        for row in rows:
            columns = row.find_all('td')
            if columns:
                library_name = columns[1].find('a').text.strip()
                library_link = columns[1].find('a')['href']
                print(f"Scraping details for library: {library_name}...")
                library_info = scrape_library_details(library_link)
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
