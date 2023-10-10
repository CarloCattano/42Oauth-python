#!/usr/bin/env python3

import time
import requests
import json
import os

# read uid and secret from environment variables
UID = os.environ.get("INTRA_UID")
SECRET = os.environ.get("INTRA_SECRET")

if UID is None or SECRET is None:
    print("Please set INTRA_UID and INTRA_SECRET environment variables")
    exit(1)

def post42(url, payload):
    url = "https://api.intra.42.fr" + url
    payload = payload
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

def get42(url, payload):
    url = "https://api.intra.42.fr" + url
    payload = payload
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()

wtoken = post42("/oauth/token", {"grant_type": "client_credentials", \
                                "client_id": UID, "client_secret": SECRET})
campus_users = []
temp = []

campus_users_general = '/v2/campus/51'  # Berlin campus id 51
campus_users_total = get42(campus_users_general, {"access_token": wtoken["access_token"]})
total_users = campus_users_total["users_count"]

total_pages = ( total_users // 100 + 1 ) + 1

for i in range(1, total_pages):  
    campus_users += get42("/v2/campus/51/users?page[number]=" + str(i) + "&page[size]=100", \
                                                   {"access_token": wtoken["access_token"]})

def get_floor(location):
    floor_mapping = {
        "c4": "4",
        "c1": "1",
        "c0": "0",
    }
    prefix = location[:2]
    return floor_mapping.get(prefix, "Unknown")

for user in campus_users:
    if user.get("location") is not None and user.get("kind") == "student":
        temp.append({
            "id": user.get("id"),
            "login": user.get("login"),
            "name": user.get("first_name"),
            "correction_point":  user.get("correction_point"),
            "pool_year": user.get("pool_year"),
            "location": user.get("location"),  
            "updated_at": user.get("updated_at").split("T")[1].split(".")[0],
            "wallet": user.get("wallet"),
            "avatar": user.get("image").get("versions").get("medium"),
            "profile": user.get("url"),
            "floor": get_floor(user.get("location"))
        })

temp.sort(key=lambda x: x["pool_year"], reverse=True)

with open("campus_users.json", "w") as f:
     json.dump(temp, f, indent=4, sort_keys=True)

# For debugging
with open("raw_users.json", "w") as f:
     json.dump(campus_users, f, indent=4, sort_keys=True)
