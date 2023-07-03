import http.client
import requests
import json
import logging

import os
import requests
from datetime import datetime
logging.basicConfig(level=logging.INFO)

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



deal_list_robot_id = "fa361dc9-4801-4c6c-8e46-907865508e05"
screen_shot_robot_id = "da5987ee-0d04-4b70-96f9-6ae0fb5ec391"
# download_screenshots(screen_shot_robot_id)
res = get_robot_tasks(deal_list_robot_id)
# print(res['result']['robotTasks']['items'][-1]['capturedLists']['amazon product list parser'])
for item in res['result']['robotTasks']['items'][-1]['capturedLists']['amazon product list parser']:
    print(item['Position'], item['discount rate'], item['product name'])