import pandas as pd
import re

def read_csv_file(file_name):
    try:
        data = pd.read_csv(file_name)
        return data
    except FileNotFoundError:
        print("File not found. Please check the file name and try again.")
    except Exception as e:
        print("An error occurred: ", e)
def hyperlink_to_url(hyperlink):
    # Check if hyperlink is a string
    if isinstance(hyperlink, str):
        url = re.search(r'href=[\'"]?([^\'" >]+)', hyperlink)
        if url:
            return url.group(1)
    # Return hyperlink as is if it's not a string or if no match was found
    return hyperlink

# Read the csv file
df = read_csv_file('/Users/xinchen/Documents/temu_csv/amazon-best-seller_1.csv')

# Apply the function to the "Product Link" column
df['Product Link'] = df['Product Link'].apply(hyperlink_to_url)

print(df)
