import http.client
from fileinput import filename

import requests
import json
import logging
import os
import pandas as pd
import openai
import csv
import time
from tabulate import tabulate

# API keys
with open("bitly.txt", "r") as file:
    bitly_key = file.read().strip()

def get_api_key():
    try:
        with open('key.txt', 'r') as file:
            api_key = file.read().replace('\n', '')
        return api_key
    except Exception as e:
        logging.error(f'Failed to read API key: {e}')

def get_robots():
    try:
        conn = http.client.HTTPSConnection("api.browse.ai")
        headers = {'Authorization': f"Bearer {get_api_key()}"}
        conn.request("GET", "/v2/robots", headers=headers)
        res = conn.getresponse()
        data = res.read()
        pretty_data = json.loads(data.decode("utf-8"))
        return pretty_data
    except Exception as e:
        logging.error(f'Failed to get robots: {e}')

def get_robot_tasks(robotId):
    try:
        conn = http.client.HTTPSConnection("api.browse.ai")
        headers = {'Authorization': f"Bearer {get_api_key()}"}
        conn.request("GET", f"/v2/robots/{robotId}/tasks?page=1", headers=headers)
        res = conn.getresponse()
        data = res.read()
        pretty_data = json.loads(data.decode("utf-8"))
        return pretty_data
    except Exception as e:
        logging.error(f'Failed to get robot tasks: {e}')

def post_robot_task(robotId, originUrl):
    try:
        url = f"https://api.browse.ai/v2/robots/{robotId}/tasks"
        payload = {"inputParameters": {"originUrl": originUrl}}
        headers = {"Authorization": f"Bearer {get_api_key()}"}
        response = requests.request("POST", url, json=payload, headers=headers)
        pretty_data = json.loads(response.text)
        return pretty_data
    except Exception as e:
        logging.error(f'Failed to post robot task: {e}')

def generate_affiliate_link(product_link, affiliate_id):
    return product_link + "?tag=" + affiliate_id

def generate_short_link(affiliate_link):
    url = f"https://api-ssl.bitly.com/v4/shorten"
    headers = {
        "Authorization": f"Bearer {bitly_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "long_url": affiliate_link,
        "domain": "bit.ly",
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()['link']


def print_product_info_in_md(robot_id):
    res = get_robot_tasks(robot_id)
    markdown_output = "| Position | Discount Rate | Product Name | Short Link | Description |\n| --- | --- | --- | --- | --- |\n"
    csv_output = []

    for task in res["result"]['robotTasks']['items']:
        if 'capturedLists' in task and 'amazon product list parser' in task['capturedLists']:
            for item in task['capturedLists']['amazon product list parser']:
                affiliate_link = generate_affiliate_link(item['product link'], 'schentop5amaz-20')
                short_link = generate_short_link(affiliate_link)

                # Generate description for each product
                description = f"The product, {item['product name']}, is available for purchase at this link: {short_link}"

                markdown_output += f"| {item['Position']} | {item['discount rate']} | {item['product name']} | {short_link} | {description} |\n"
                csv_output.append(
                    [item['Position'], item['discount rate'], item['product name'], short_link, description])

    timestamp = time.strftime("%Y%m%d-%H%M")
    markdown_filename = f"deal-{timestamp}"
    with open(f"{markdown_filename}.md", "w") as f:
        f.write(markdown_output)

    os.makedirs('./csv_output', exist_ok=True)
    with open(f'./csv_output/{markdown_filename}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_output)

    return markdown_filename  # Return the filename without extension
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

        # Remove undesired phrases from the lines
        lines = [line.replace("Description", "").replace("---", "") for line in lines]

        for line in lines:
            columns = line.split("|")
            if len(columns) > 1:  # Exclude lines that don't have the pipe character
                last_column = columns[-2]  # The last column is the second last element after split due to trailing "|"
                print(last_column.strip())  # strip is used to remove leading and trailing whitespace


# Usage
deal_list_robot_id = "fa361dc9-4801-4c6c-8e46-907865508e05"
markdown_filename = print_product_info_in_md(deal_list_robot_id)

# Open the markdown file and read its content
with open(f"{markdown_filename}.md", "r") as f:
    markdown_output = f.read()

# Use the markdown_output
script_filename = generate_script_with_gpt(markdown_output)

iterate_last_column(f"result/{script_filename}.md")
