
import requests
from config import apikey
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

def get_erc20tokens(address):
    CONST_WEI_TO_ETH = 10 ** 18 
    req = requests.get("https://api.etherscan.io/api?module=account&action=tokentx&address="+address+ "&page=1&offset=100&startblock=0&endblock=27025780&sort=desc&apikey="+apikey).json()
    res = req['result']
    erc_min = int(res[0]['value']) 
    erc_max = int(res[0]['value'])
    total_received = 0
    receive_count = 0 
    total_value_sent_contract = 0
    unique_sent_addr_dict = {}
    unique_rec_addr = {}
    unique_token_names ={}
    token_prices ={}

    for item in res:

        if item['contractAddress'] not in token_prices.keys():
            price_query = cg.get_token_price(id= "ethereum",contract_addresses= item['contractAddress'],vs_currencies='eth')
            price = price_query[item['contractAddress']]['eth']
            token_prices[item['contractAddress']] = price

        #get ERC minimum and maximum value sent #31 #32
        current_val = int(item['value'])
        if  current_val < erc_min:
            erc_min = current_val
        if current_val > erc_max:
            erc_max = current_val

        #check erc 20 unique sent addresses #25
        try:
            unique_sent_addr_dict[item['from']] += 1
        except KeyError:
            unique_sent_addr_dict[item['from']] = 1
        
        #check unique erc 20 rec addresses #34 
        try: 
            unique_rec_addr[item['to']] += 1
        except KeyError:
            unique_rec_addr[item['to']] = 1

        #unique token names #33
        try:
            unique_token_names[item['tokenName']] += 1
        except KeyError:
            unique_token_names[item['tokenName']] = 1
        
     
        total_value_sent_contract += int(item['value'])

        #get value received 
        if item['to'] == address:
            val = int(item['value'])
            val += total_received 
            receive_count += 1

        avg_received = total_received/ receive_count

    return token_prices,erc_min,erc_max,len(unique_sent_addr_dict),len(unique_rec_addr),unique_token_names,avg_received,total_value_sent_contract
    

    

print(get_erc20tokens("0x4e83362442b8d1bec281594cea3050c8eb01311c"))