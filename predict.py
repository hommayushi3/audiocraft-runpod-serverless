import os
import requests
from time import sleep
import logging
import argparse
import sys
import json

endpoint_id = os.environ["RUNPOD_ENDPOINT_ID"]
URI = f"https://api.runpod.ai/v2/{endpoint_id}/run"


def run(params={}, stream=False):
    request = params

    response = requests.post(URI, json=dict(input=request), headers = {
        "Authorization": f"Bearer {os.environ['RUNPOD_AI_API_KEY']}"
    })

    if response.status_code == 200:
        data = response.json()
        task_id = data.get('id')
        return stream_output(task_id, stream=stream)


def stream_output(task_id, stream=False):
    try:
        url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{task_id}"
        headers = {
            "Authorization": f"Bearer {os.environ['RUNPOD_AI_API_KEY']}"
        }

        previous_output = ''

        while True:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(data)
                if data.get('status') == 'COMPLETED':
                    new_output = data['output']
                    return new_output
                    
            elif response.status_code >= 400:
                logging.error(response.json())
            # Sleep for 0.1 seconds between each request
            sleep(0.1 if stream else 1)
    except Exception as e:
        print(e)
        cancel_task(task_id)
    

def cancel_task(task_id):
    url = f"https://api.runpod.ai/v2/{endpoint_id}/cancel/{task_id}"
    headers = {
        "Authorization": f"Bearer {os.environ['RUNPOD_AI_API_KEY']}"
    }
    response = requests.get(url, headers=headers)
    return response


def decode_b64_to_file(b64, filename):
    import base64
    decoded = base64.b64decode(b64.encode('utf-8'))
    with open(filename + ".wav", 'wb') as f:
        f.write(decoded)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runpod AI CLI')
    parser.add_argument('-p', '--params_json', type=str, help='JSON string of generation params')
    args = parser.parse_args()
    params = json.loads(args.params_json) if args.params_json else "{}"
    outputs = json.loads(run(params=params))
    for k, v in outputs.items():
        decode_b64_to_file(outputs[k], k)
