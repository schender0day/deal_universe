import http.client
import requests
import json
import logging
import csv
import os
import requests
from datetime import datetime
logging.basicConfig(level=logging.INFO)
import openai
import pandas as pd

# Define the path of your API key file
file_path = "chat.txt"

# Ensure the file exists
if not os.path.exists(file_path):
    raise ValueError("API Key file does not exist")

# Read the API key from the file
with open(file_path, "r") as file:
    openai.api_key = file.read().strip()
with open("bitly.txt", "r") as file:
    bitly_key = file.read().strip()
# Load the API key from a local file
def get_api_key():
    try:
        with open('key.txt', 'r') as file:
            api_key = file.read().replace('\n', '')
        return api_key
    except Exception as e:
        logging.error(f'Failed to read API key: {e}')
# Get a list of robots
def get_robots():
    try:
        conn = http.client.HTTPSConnection("api.browse.ai")
        headers = {'Authorization': f"Bearer {get_api_key()}"}
        conn.request("GET", "/v2/robots", headers=headers)
        res = conn.getresponse()
        data = res.read()
        pretty_data = json.loads(data.decode("utf-8"))
        return pretty_data
        # print(json.dumps(pretty_data, indent=4))
    except Exception as e:
        logging.error(f'Failed to get robots: {e}')

# Get tasks for a specific robot
def get_robot_tasks(robotId):
    try:
        conn = http.client.HTTPSConnection("api.browse.ai")
        headers = {'Authorization': f"Bearer {get_api_key()}"}
        conn.request("GET", f"/v2/robots/{robotId}/tasks?page=1", headers=headers)
        res = conn.getresponse()
        data = res.read()
        pretty_data = json.loads(data.decode("utf-8"))
        # print(json.dumps(pretty_data, indent=4))
        return pretty_data
    except Exception as e:
        logging.error(f'Failed to get robot tasks: {e}')

# Get tasks for a specific robot at a specific page
def get_robot_tasks_page(robotId, pageNumber):
    try:
        conn = http.client.HTTPSConnection("api.browse.ai")
        headers = {'Authorization': f"Bearer {get_api_key()}"}
        conn.request("GET", f"/v2/robots/{robotId}/tasks?page={pageNumber}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        pretty_data = json.loads(data.decode("utf-8"))
        return pretty_data
    except Exception as e:
        print(json.dumps(pretty_data, indent=4))
    except Exception as e:
        logging.error(f'Failed to get robot tasks page: {e}')

# Post a task for a specific robot
def post_robot_task(robotId, originUrl):
    try:
        url = f"https://api.browse.ai/v2/robots/{robotId}/tasks"
        payload = {"inputParameters": {"originUrl": originUrl}}
        headers = {"Authorization": f"Bearer {get_api_key()}"}
        response = requests.request("POST", url, json=payload, headers=headers)
        pretty_data = json.loads(response.text)
        return pretty_data
        # print(json.dumps(pretty_data, indent=4))
    except Exception as e:
        logging.error(f'Failed to post robot task: {e}')

# Get a specific tagisk of a robot
def get_specific_task(robotId, taskId):
    try:
        conn = http.client.HTTPSConnection("api.browse.ai")
        headers = {'Authorization': f"Bearer {get_api_key()}"}
        conn.request("GET", f"/v2/robots/{robotId}/tasks/{taskId}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        pretty_data = json.loads(data.decode("utf-8"))
        print(json.dumps(pretty_data, indent=4))
    except Exception as e:
        logging.error(f'Failed to get specific task: {e}')

def get_png_filenames(response):
    png_files = []

    try:
        tasks = response['data']['browseai']['getRobot']['tasks']
        for task in tasks:
            screenshots = task['data']['capturedScreenshots']
            for screenshot in screenshots.values():
                src = screenshot['src']
                if src.endswith('.png'):
                    png_files.append(src)
    except KeyError:
        print('Unable to find key in the response.')

    return png_files
def download_screenshots(screen_shot_robot_id):
    # Create the screenshots directory
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M")
    directory = f"./screenshots/{current_time}"
    os.makedirs(directory, exist_ok=True)

    # Retrieve the robot tasks
    res = get_robot_tasks(screen_shot_robot_id)

    # Extract PNG filenames and download them
    count = 1  # Counter for the filename
    for item in res["result"]['robotTasks']['items'][-1]['capturedScreenshots'].values():
        url = item['src']
        extension = os.path.splitext(url)[1]
        filename = f"{count}{extension}"
        filepath = os.path.join(directory, filename)

        # Download the PNG file
        response = requests.get(url)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
                print(f"Downloaded: {filepath}")
        else:
            print(f"Failed to download: {url}")

        count += 1  # Increment the counter

def generate_affiliate_link(product_link, affiliate_id):
    """
    Generate affiliate link using product link and affiliate id.

    Args:
        product_link (str): The link of the product.
        affiliate_id (str): Your affiliate id.

    Returns:
        str: The affiliate link.
    """
    return product_link + "?tag=" + affiliate_id
def generate_short_link(affiliate_link):
    """
    Generate short link using Bitly API.

    Args:
        affiliate_link (str): The affiliate link.

    Returns:
        str: The short link.
    """
    url = f"https://api-ssl.bitly.com/v4/shorten"
    headers = {
        "Authorization": f"Bearer {bitly_key}",  # Replace with your Bitly API key
        "Content-Type": "application/json"
    }
    payload = {
        "long_url": affiliate_link,
        "domain": "bit.ly",
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()['link']

def print_product_info_in_md(robot_id):
    """
    Prints the position, discount rate, product name, affiliate link, and short link in markdown format
    for the given robot id, and saves the output in markdown and CSV format.

    Args:
        robot_id (str): The id of the robot for which product info is printed.

    """
    res = get_robot_tasks(robot_id)
    markdown_output = "| Position | Discount Rate | Product Name | Affiliate Link | Short Link |\n| --- | --- | --- | --- | --- |\n"
    csv_output = []

    for item in res['result']['robotTasks']['items'][-1]['capturedLists']['amazon product list parser']:
        affiliate_link = generate_affiliate_link(item['product link'], 'schentop5amaz-20')
        short_link = generate_short_link(affiliate_link)
        markdown_output += f"| {item['Position']} | {item['discount rate']} | {item['product name']} | {affiliate_link} | {short_link} |\n"
        csv_output.append([item['Position'], item['discount rate'], item['product name'], affiliate_link, short_link])

    print(markdown_output)

    # Write markdown output to .md file
    md_filename = input("Enter the markdown filename (without extension): ")
    os.makedirs('./markdown_output', exist_ok=True)  # Create directory if it doesn't exist
    with open(f'./markdown_output/{md_filename}.md', 'w') as f:
        f.write(markdown_output)

    # Write CSV output to .csv file
    csv_filename = input("Enter the CSV filename (without extension): ")
    os.makedirs('./csv_output', exist_ok=True)  # Create directory if it doesn't exist
    df = pd.DataFrame(csv_output, columns=['Position', 'Discount Rate', 'Product Name', 'Affiliate Link', 'Short Link'])
    df.to_csv(f'./csv_output/{csv_filename}.csv', index=False)
# Usage
deal_list_robot_id = "fa361dc9-4801-4c6c-8e46-907865508e05"
print_product_info_in_md(deal_list_robot_id)