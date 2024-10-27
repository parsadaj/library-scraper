import pandas as pd
import os

# Define new column names
new_column_names = {
    'name': 'Name',
    'province': 'Prov.',
    'city': 'City',
    'address': 'Address',
    'phone_number': 'Phone No.',
    'website': 'Website'
}

# Read the original CSV file
df = pd.read_csv('libraries.csv')
results_path = 'results'
if not os.path.exists(results_path):
    os.makedirs(results_path)
    
# Function to create a README.md file with a table of library data
def create_readme(city_path, city_df):
    readme_path = os.path.join(city_path, 'README.md')

        # Rename columns to new names
    city_df.rename(columns=new_column_names, inplace=True)

    # Make the library name a hyperlink to the website
    def make_hyperlink(row):
        if row['Website'] != 'N/A':
            return f"[{row['Name']}]({row['Website']})"
        else:
            return row['Name']

    city_df['Name'] = city_df.apply(make_hyperlink, axis=1)

    # Drop the website column
    city_df = city_df.drop(columns=['Website', 'Phone No.', 'Prov.', 'City'])
            
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(city_df.to_markdown(index=False))
    print(f"Created {readme_path}")

# Iterate over each unique province
for province in df['province'].unique():
    province_df = df[df['province'] == province]
    
    # Create a directory for the province if it doesn't exist
    province_path = os.path.join(results_path, province)
    if not os.path.exists(province_path):
        os.makedirs(province_path)
    
    # Iterate over each unique city within the province
    for city in province_df['city'].unique():
        city_df = province_df[province_df['city'] == city]
        
        # Create a directory for the city within the province directory
        city_path = os.path.join(province_path, city)
        if not os.path.exists(city_path):
            os.makedirs(city_path)
        
        # Create a CSV file for the city within the city directory
        city_file_path = os.path.join(city_path, f"{city}.csv")
        city_df.to_csv(city_file_path, index=False)
        print(f"Created {city_file_path}")
        
        # Create the README.md file with a table of library data
        create_readme(city_path, city_df)

print("Clustering, file creation, and README generation completed successfully!")
