from bs4 import BeautifulSoup
import pandas as pd

from bs4 import BeautifulSoup

def url_parser(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    product_link_tag = soup.find('a', href=True)
    if product_link_tag:
        relative_url = product_link_tag['href']
        base_url = "https://www.temu.com"
        full_url = base_url + relative_url if relative_url.startswith("/") else relative_url
        return full_url
    else:
        return None  # Return None or some placeholder when no URL found

def read_csv_file():
    file_directory = '/Users/xinchen/Documents/temu_csv/teme3.csv'
    df = pd.read_csv(file_directory, skiprows=0)  # Skip the first row
    return df

# Read CSV file
data = read_csv_file()

# Apply the function to each cell in the 'image' column
data['image'] = data['image'].apply(url_parser)

# reorder dataframe
data = data[['Position', 'product name', 'image', 'current price']]

# Print the DataFrame
print(data.head())

# Write DataFrame to CSV
data.to_csv('/Users/xinchen/Documents/temu_csv/temu3_modified.csv', index=False)
