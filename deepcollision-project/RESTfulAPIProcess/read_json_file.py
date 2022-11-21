import json
import requests


def load_restful_api(action_id):
    json_file = open('RESTful_API.json', 'r')
    content = json_file.read()
    # print(content)
    restful_api = json.loads(content)
    # print(restful_api['status'][action_id])
    return restful_api


if __name__ == "__main__":
    api = load_restful_api(str(0))
    print(api['command']['0'])
    r = requests.post(api['command']['5'])
    print(api['command']['num'])
