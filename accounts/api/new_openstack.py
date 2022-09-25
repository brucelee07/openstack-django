import os
import json
import requests
import datetime
import time

scoped_token = ""
expired_time = datetime.datetime.now()


def get_scoped_token():
    global scoped_token, expired_time
    Base = os.path.dirname(os.path.abspath(__file__))
    filepath = Base + "/config.json"
    expired_time = datetime.datetime.now() + datetime.timedelta(hours=1)
    curl_token = f"""curl -si -d @{filepath} -H "Content-type: application/json" http://10.0.0.194:5000/v3/auth/tokens"""
    responses = os.popen(curl_token).readlines()
    scoped_token = responses[4].split(":")[1].strip()

    # admin_detain = json.loads(responses[9])["token"]
    # expired_time = admin_detain["expires_at"].replace("T", " ").replace(".000000Z", "")
    # expired_time = datetime.datetime.strptime(expired_time, "%Y-%m-%d %H:%M:%S")

    return scoped_token


def get_server_ids(scoped_token):
    servers_url = "http://10.0.0.6:8774/v2.1/servers"
    headers = {"X-Auth-Token": scoped_token}
    servers = requests.get(servers_url, headers=headers)
    server_list = json.loads(servers.content.decode("utf-8"))["servers"]
    for server in server_list:
        print(server["id"], server["name"])


def get_server_details(token):
    servers_url = "http://10.0.0.6:8774/v2.1/servers/detail"
    headers = {"X-Auth-Token": token}
    servers = requests.get(servers_url, headers=headers)
    server_list = json.loads(servers.content.decode("utf-8"))["servers"]
    return server_list[0]
    # for server in server_list:
    #     print("id", "name", "state", "ip")
    #     print(
    #         server["id"],
    #         server["name"],
    #         server["status"],
    #         server["addresses"]["Pub_Net"][0]["addr"],
    #     )


def server_action(token, server_id, action):
    """ action : os-start  , os-stop"""
    print(token, server_id, action)
    servers_url = "http://10.0.0.6:8774/v2.1/servers/" + server_id + "/action"
    headers = {"X-Auth-Token": token}
    data = {action: None}
    response = requests.post(servers_url, headers=headers, data=json.dumps(data))
    response = response.content.decode("utf-8")
    if response == "":
        return True
    try:
        result = json.loads(response)
        if result["conflictingRequest"]:
            return True
    except Exception:
        return False


def create_server(token, name, image, flavor):
    servers_url = "http://10.0.0.6:8774/v2.1/servers"
    headers = {"X-Auth-Token": token}
    data = {
        "server": {
            "name": name,
            "imageRef": image,
            "flavorRef": flavor,
            "networks": [{"uuid": "6966aae2-2784-4c9a-a26e-a657bcded49d"}],
        }
    }
    # data = {
    #     "server": {
    #         "name": name,
    #         "imageRef": "9ba70288-8dac-464c-af4c-97920b103f00",
    #         "flavorRef": "ed32da40-33a8-42d9-8689-a2e1bde9eb84",
    #         "networks": [{"uuid": "6966aae2-2784-4c9a-a26e-a657bcded49d"}],
    #     }
    # }
    response = requests.post(servers_url, headers=headers, data=json.dumps(data))
    result = response.content.decode("utf-8")
    try:
        result = json.loads(result)
        server_id = result["server"]["id"]
        password = result["server"]["adminPass"]

        for i in range(5):
            try:
                server = get_server_details(token)
                ip = server["addresses"]["Pub_Net"][0]["addr"]
                break
            except Exception:
                time.sleep(10)
                continue
        ip = ip if ip else ""
        return server_id, password, ip
    except Exception:
        print("somthing is wrong")
        return None, None, None


def delete_server(token, server_id):
    headers = {"X-Auth-Token": token}
    servers_url = "http://10.0.0.6:8774/v2.1/servers/" + server_id
    response = requests.delete(servers_url, headers=headers)
    return response.content.decode("utf-8") == ""


def checktoken():
    global expired_time, scoped_token
    now = datetime.datetime.now()
    if expired_time < now:
        return get_scoped_token()
    elif scoped_token == "":
        return get_scoped_token()
    else:
        return scoped_token


def get_images(token):
    servers_url = "http://10.0.0.13:9292/v2/images"
    headers = {"X-Auth-Token": token}
    response = requests.get(servers_url, headers=headers)
    result = json.loads(response.content.decode("utf-8"))
    images = []
    for image in result["images"]:
        images.append({"name": image["name"], "id": image["id"]})
    return images


def get_flavors(token):
    servers_url = "http://10.0.0.6:8774/v2.1/flavors"
    headers = {"X-Auth-Token": token}
    response = requests.get(servers_url, headers=headers)
    result = json.loads(response.content.decode("utf-8"))
    flavors = []
    for flavor in result["flavors"]:
        flavors.append({"name": flavor["name"], "id": flavor["id"]})
    return flavors


def get_spice(token, vmid):
    servers_url = "http://10.0.0.6:8774/v2.1/servers/" + vmid + "/action"
    data = {"os-getSPICEConsole": {"type": "spice-html5"}}
    headers = {"X-Auth-Token": token}
    response = requests.post(servers_url, headers=headers, data=json.dumps(data))
    result = json.loads(response.text)
    result = result["console"]["url"]
    ip = result.split("&")[0].split("=")[1]
    port = result.split("&")[1].split("=")[1]
    return ip, port
