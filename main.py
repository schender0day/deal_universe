import csv
import glob
import http.client
import json
import logging
import os
import time
import urllib
from urllib.parse import urlparse
import imgkit
import openai
import string
import pandas as pd
import pyperclip
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from test import extract_promotion_code_in_html, convert_html_to_jpeg


def remove_files():
    # Get a list of all the files in the current directory
    md_files = glob.glob('*.md')
    csv_files = glob.glob('*.csv')
    result_csv_files = glob.glob('result/*.csv')

    all_files = md_files + csv_files + result_csv_files

    if 'readme.md' in all_files:
        all_files.remove('readme.md')

    for filename in all_files:
        os.remove(filename)
        # print(f'Deleted file: {filename}')


def get_api_key():
    try:
        with open('key.txt', 'r') as file:
            api_key = file.read().strip()
        return api_key
    except Exception as e:
        logging.error(f'Failed to read API key: {e}')
        return None
def get_bitly_api_key():
    try:
        with open('bitly.txt', 'r') as file:
            api_key = file.read().strip()
        return api_key
    except Exception as e:
        logging.error(f'Failed to read API key: {e}')
        return None

def get_robots():
    try:
        conn = http.client.HTTPSConnection("api.browse.ai")
        headers = {'Authorization': f"Bearer {get_api_key()}"}
        conn.request("GET", "/v2/robots", headers=headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        return json.loads(data)
    except Exception as e:
        logging.error(f'Failed to get robots: {e}')
        return None


def get_robot_tasks(robot_id):
    try:
        conn = http.client.HTTPSConnection("api.browse.ai")
        headers = {'Authorization': f"Bearer {get_api_key()}"}
        conn.request("GET", f"/v2/robots/{robot_id}/tasks?page=1", headers=headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        return json.loads(data)
    except Exception as e:
        logging.error(f'Failed to get robot tasks: {e}')
        return None


def post_robot_task(robot_id, origin_url):
    try:
        url = f"https://api.browse.ai/v2/robots/{robot_id}/tasks"
        payload = {"inputParameters": {"originUrl": origin_url}}
        headers = {"Authorization": f"Bearer {get_api_key()}"}
        response = requests.request("POST", url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        logging.error(f'Failed to post robot task: {e}')
        return None


def generate_affiliate_link(product_link, affiliate_id):
    link = f"{product_link}/ref=nosim?tag={affiliate_id}"
    # print(link)
    return link


def generate_short_link(affiliate_link, bitly_key):
    url = "https://api-ssl.bitly.com/v4/shorten"
    headers = {
        "Authorization": f"Bearer {bitly_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "long_url": affiliate_link,
        "domain": "bit.ly",
    }
    response = requests.post(url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code != 200:
        logging.error("Bitly API request failed. Error: %s", response.text)
        return None

    return response.json()['link']


def clean_url(encoded_url):
    # Decode URL
    decoded_url = urllib.parse.unquote(encoded_url)

    # Extract amazon link from decoded URL
    amazon_url = urllib.parse.urlparse(decoded_url).query.split('url=')[1].split('&')[0]

    # Clean the Amazon URL to remove tracking information
    clean_url = amazon_url.split('?')[0]
    # print(clean_url)
    return clean_url
def temu_url_parser(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    product_link_tag = soup.find('a', {'class': '_3VEjS46S _2IVkRQY-'})
    relative_url = product_link_tag['href'] if product_link_tag else 'No product link found'
    base_url = "https://www.temu.com"
    full_url = base_url + relative_url if relative_url.startswith("/") else relative_url
    return full_url

def download_product_image(image_url, product_number):
    # Create the directory if it doesn't exist
    if not os.path.exists('./product_image'):
        os.makedirs('./product_image')

    # Download the image
    response = requests.get(image_url, stream=True)
    response.raise_for_status()

    # Save the image to the file
    filename = f'./product_image/product_{product_number}.jpeg'
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)


def parse_prices(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extracting the current price
    current_price_div = soup.find('div', {'class': '_2Ci4uR69', 'aria-hidden': 'true'})
    current_price = float(current_price_div.text) if current_price_div else None

    # Extracting the market price
    market_price_span = soup.find('span', {'data-type': 'marketPrice'})
    market_price = float(market_price_span.text[1:]) if market_price_span else None

    return current_price, market_price
def parse_prices_from_markdown(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    for line in lines[2:]:  # Skip the header and separator lines
        columns = line.split("|")
        if len(columns) > 6:  # There should be at least 7 columns (1-indexed Position to 7-indexed Short Link)
            price_html = columns[4]  # The Price column is the 5th column (4-indexed)
            current_price, market_price = parse_prices(price_html)
            print(f"Current price: {current_price}, Market price: {market_price}")

def print_product_info_in_md(robot_id, bitly_key):
    res = get_robot_tasks(robot_id)
    print(json.dumps(res, indent=4))
    if not os.path.exists('product_image'):
        os.makedirs('product_image')
    markdown_output = "| Position | Product Link | Image | Price | Product Name | Promotion | Short Link |\n| --- | --- | --- | --- | --- | --- | --- |\n"
    csv_output = []
    item_count = 0
    idx =  0
    for task in res.get('result', {}).get('robotTasks', {}).get('items', [])[-2:]:

        if 'capturedLists' in task and 'dealmoon ult2' in task['capturedLists']:
            for item in task['capturedLists']['dealmoon ult2']:
                # print(item)
                if item_count == 20:
                    break
                # Clean the product link to get the original Amazon URL
                amazon_url = clean_url(item['product link'])
                output_file = f'product_image/product_{idx + 1}.jpeg'
                convert_html_to_jpeg(item["product image"], output_file)
                promotion = f"Promotion Code:{item['promotion']}"
                affiliate_link = generate_affiliate_link(amazon_url, 'schentop5amaz-20')
                short_link = None
                price = item['price']
                generate_description(item_count + 1, price, item['product name'], affiliate_link, promotion)
                item_price = parse_prices_from_markdown(item['price'])
                markdown_output += f"| {item['Position']} | {amazon_url} | {item['image']} | {item_price} | {item['product name']} | {item.get('promotion', '')} | {short_link if short_link else affiliate_link} |\n"
                csv_output.append([item['Position'], amazon_url, item['image'], item['price'], item['product name'],
                                   item.get('promotion', ''), affiliate_link])
                item_count += 1
                idx += 1
            if item_count == 10:  # I changed this to 10 because you're checking for 10 items before
                break
        else:
            for item in task['capturedLists']['temu']:
                print("TEMUTEMUTEMUTEMUTEMU")
                if item_count == 15:
                    break
                # Clean the product link to get the original Amazon URL
                temu_url = temu_url_parser(item["product image"])
                output_file = f'product_image/product_{idx + 1}.jpeg'
                image = download_product_image(item["image"], idx + 1)
                promotion = f"Promotion Code: afq97285"
                affiliate_link = temu_url
                short_link = temu_url
                price = item['price']
                generate_description(item_count + 1, price, item['product name'], affiliate_link, promotion)
                markdown_output += f"| {item['Position']} | {item['price']} | {item['product name']} | {temu_url}  |\n"
                csv_output.append([item['Position'], temu_url, item['image'], item['price'], item['product name'],
                                   item.get('promotion', ''), affiliate_link])
                item_count += 1
                idx += 1
                print(markdown_output)
    timestamp = time.strftime("%Y%m%d-%H%M")
    markdown_filename = f"deal-{timestamp}"

    with open(f"{markdown_filename}.md", "w") as f:
        f.write(markdown_output)

    os.makedirs('./csv_output', exist_ok=True)

    with open(f'./csv_output/{markdown_filename}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_output)

    return markdown_filename


def sanitize_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in filename if c in valid_chars)
import re

def generate_description(position, discount_rate, product_name, short_link, promotion="no promotion code"):
    print("genearating description")
    # Extract the sale price and the original price from discount_rate using regular expressions
    sale_price_match = re.search(r'<span class="sale">(.+?)</span>', discount_rate)
    sale_price = sale_price_match.group(1) if sale_price_match else None
    original_price_match = re.search(r'<del class="origin">(.+?)</del>', discount_rate)
    original_price = original_price_match.group(1) if original_price_match else None

    # Generate description
    description = f"{position} {product_name}, Sale Price: {sale_price}, Original Price: {original_price}, {promotion},Link: {short_link}"

    # Generate timestamp
    timestamp = time.strftime("%Y%m%d-%H%M")

    # Sanitize product name for filename
    sanitized_product_name = sanitize_filename(product_name)

    # Create a directory for descriptions if it does not exist
    os.makedirs('./product_description', exist_ok=True)

    # Save the description in a text file named with product-timestamp
    with open(f'./product_description/{sanitized_product_name}-{timestamp}.txt', 'w') as file:
        file.write(description)

    # Print the description
    # print(description)

def add_space_around_pipe(filename):
    with open(filename, "r") as f:
        content = f.read()

    content = content.replace("|", " | ")

    with open(filename, "w") as f:
        f.write(content)

def generate_script_with_gpt(markdown_output):
    # Read API key and set it
    with open("chat.txt", "r") as file:
        openai.api_key = file.read().strip()

    # Read prompt from example_script.txt
    with open('example_script.txt', 'r') as f:
        additional_prompt = f.read()

    # Combine markdown_output and additional_prompt
    chat_prompt = additional_prompt + "\n" + markdown_output

    # Send a chat request
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": chat_prompt},
        ]
    )

    # Extract the generated script
    generated_script = response['choices'][0]['message']['content']

    # Save the generated_script in both markdown and CSV format in ./result directory
    os.makedirs('./result', exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M")
    script_filename = f"script-{timestamp}"
    with open(f'./result/{script_filename}.md', 'w') as f:
        f.write(generated_script)
    add_space_around_pipe(f'./result/{script_filename}.md')
    # The following is an example. Modify it based on the actual structure of your generated_script.
    csv_output = generated_script.replace("|", ",")  # Convert markdown table to CSV
    with open(f'./result/{script_filename}.csv', 'w') as f:
        f.write(csv_output)

    return script_filename  # Return the filename without extension



def iterate_last_column(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    output_text = ""
    # Remove undesired phrases from the lines
    lines = [line.replace("Description", "").replace("---", "") for line in lines]

    for line in lines:
        columns = line.split("|")
        if len(columns) > 1:  # Exclude lines that don't have the pipe character
            last_column = columns[-2]  # The last column is the second last element after split due to trailing "|"
            output_text += last_column.strip() + "\n"  # strip is used to remove leading and trailing whitespace
            print(last_column.strip())


    # Copy the output_text to clipboard
    pyperclip.copy(output_text)

# Usage
input_option = input("What would you like to do?\n1. Amazon\n2.Temu")
if input_option == "1":
    deal_list_robot_id = "44fbfcdb-d3d1-4c1a-9f7e-55a2116ec84c"
elif input_option == "2":
    deal_list_robot_id = "4fc8cf41-ab7e-4d59-8435-c5318485c26f"
screenshots_id = "da5987ee-0d04-4b70-96f9-6ae0fb5ec391"
task_id = "d774104e-e569-4f4a-8d51-4edc1bf50398"

def download_png_files(png_files):
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')
    count = 1
    for url in png_files:

        response = requests.get(url, stream=True)

        a = urlparse(url)
        filename = os.path.basename(a.path)

        if response.status_code == 200:
            with open('screenshots/'+f"{count} --- {filename}", 'wb') as f:
                f.write(response.content)
        count += 1

def get_single_task_result(robot_id, task_id, api_key):
    conn = http.client.HTTPSConnection("api.browse.ai")

    headers = {'Authorization': f"Bearer {api_key}"}

    conn.request("GET", f"/v2/robots/{robot_id}/tasks/{task_id}", headers=headers)

    res = conn.getresponse()
    data = res.read().decode("utf-8")

    return json.loads(data)
def get_png_files(task_result):
    captured_screenshots = task_result.get('result', {}).get('capturedScreenshots', {})
    png_files = []
    for screenshot in captured_screenshots.values():
        png_files.append(screenshot.get('src', ''))
    return png_files
# def print_last_column(filename):
#     df = pd.read_csv(f'./result/{filename}', sep="|", skiprows=1, quotechar='"', error_bad_lines=False)
#     df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x) # Remove unnecessary spaces
#     last_column = df.columns[-1] # Get the last column name
#     # print(df[last_column].dropna()) # Print the last column, dropping NaN values


def main():
    # Ask the user for their choice
    choice = input("Enter '1' to get screenshots of task, '2' to generate script, or '3' to do both: ")

    if choice == '1' or choice == '3':
        screenshots_list = get_png_files(get_single_task_result(screenshots_id, task_id, get_api_key()))
        download_png_files(screenshots_list)

    if choice == '2' or choice == '3':
        markdown_filename = print_product_info_in_md(deal_list_robot_id, get_api_key())

        # Open the markdown file and read its content
        with open(f"{markdown_filename}.md", "r") as f:
            markdown_output = f.read()

        # Use the markdown_output
        # script_filename = generate_script_with_gpt(markdown_output)

        # iterate_last_column(f"result/{script_filename}.md")
        # print_last_column(f"{script_filename}.md")
        # Call the function to remove files
        remove_files()


if __name__ == "__main__":
    main()
