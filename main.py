import http.client
import requests
import json
import logging

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
        print(json.dumps(pretty_data, indent=4))
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
        print(json.dumps(pretty_data, indent=4))
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
        print(json.dumps(pretty_data, indent=4))
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
