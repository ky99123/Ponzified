import requests
import json
from datetime import datetime

apikey = "R63INQIAZW9HGVSG83R63M477H4YMXDH6Q"


def get_account_balance(address):
    return requests.get(
        "https://api.etherscan.io/api?module=account&action=balance&address=" + address + "&tag=latest&apikey=" + apikey)


def get_address_normal_transactions(address):
    req = requests.get(
        "https://api.etherscan.io/api?module=account&action=txlist&address=" + address + "&startblock=0&endblock=99999999&page=1&offset=10&sort=desc&tag=latest&apikey=" + apikey).json()
    val = req['result']
    return val


def get_address_internal_transactions(address):
    req = requests.get("https://api.etherscan.io/api?module=account&action=txlistinternal&address=" + address + "&startblock=0&endblock=99999999&page=1&offset=10&sort=desc&apikey=" + apikey).json()
    val = req['result']
    return val


def filter_address(address):
    with open('blacklist.json') as blacklist:
        data = json.load(blacklist)
        for item in data:
            if item['address'] == address:
                return item['comment']
        return "Address not blacklisted!"

filter_address("0x2da8703d18AFeD53B303119E4fF06CF035a9fadB")

address = str(input("input address:\n"))

x = get_address_internal_transactions(address)
print(x)
# count = 1
# for item in x:
#     count += 1
#     print(datetime.fromtimestamp(int(item['timeStamp'])))
#
# print(count)

# for key,val in x:
#     print(key,val)



