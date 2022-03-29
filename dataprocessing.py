import requests

apikey = "R63INQIAZW9HGVSG83R63M477H4YMXDH6Q"


def get_data(address):
    """
    Overall wrapper function for the retrieval and processing of data
    obtained from Etherscan API.

    Keyword arguments:
        address -- The address of the wallet to be queried
    """
    address = address.lower()

    # Get Transaction Data
    txn_req = requests.get(
        "https://api.etherscan.io/api?module=account&action=txlist&address="
        + address + "&startblock=0&endblock=99999999&page=1&offset=50&sort"
                    "=desc&tag=latest&apikey=" + apikey)
    txn_data = txn_req.json()["result"]
    print(txn_data)
    # Get Balance Data
    balance_req = requests.get(
        "https://api.etherscan.io/api?module=account&action=balance&address="
        + address + "&tag=latest&apikey=" + apikey).json()
    balance_data = balance_req["result"]

    # Get example of keys from first transaction block
    headings = []
    for key in txn_data[0].keys():
        headings.append(key)
    headings = tuple(headings)

    # Get Processed Transaction Data
    sent_count, min_sent, max_sent, avg_sent, total_ether_sent, \
        received_count, min_received, max_received, avg_received, total_ether_received, \
        unique_received_from_address = get_txn_data(txn_data, address)

    # Get Processed Timestamp Data
    avg_time_between_sent_tnx, avg_time_between_received_tnx, \
        first_last_time_diff = get_time_between_txn(txn_data, address)

    # Get Ether Balance
    total_ether_balance = int(balance_data)

    # Assemble Data into list
    data = [avg_time_between_sent_tnx, avg_time_between_received_tnx,
            first_last_time_diff, sent_count, received_count,
            unique_received_from_address, min_received,
            max_received, avg_received, min_sent, max_sent, avg_sent,
            sent_count+received_count, total_ether_sent, total_ether_received,
            total_ether_balance]
    return data, headings, txn_data


def get_txn_data(transactions, address):
    sent_count = received_count = 0
    sent_txn_values = []
    received_txn_values = []
    received_address = []

    for txn in transactions:
        if txn['from'] == address:
            sent_count += 1
            sent_txn_values.append(int(txn['value']))

        elif txn['to'] == address:
            received_count += 1
            received_txn_values.append(int(txn['value']))
            received_address.append(txn['from'])

    try:
        min_sent = min(sent_txn_values)
        max_sent = max(sent_txn_values)
        total_ether_sent = sum(sent_txn_values)
        avg_sent = total_ether_sent/len(sent_txn_values)


        min_received = min(received_txn_values)
        max_received = max(received_txn_values)
        total_ether_received = sum(received_txn_values)
        print(type(total_ether_received))
        print("Total Ether received: " + str(total_ether_received))
        avg_received = total_ether_received/len(received_txn_values)

        received_address = list(set(received_address))
        return sent_count, min_sent, max_sent, avg_sent, total_ether_sent, \
        received_count, min_received, max_received, avg_received, total_ether_received, \
        len(received_address)
    except Exception:
        pass
    


def get_time_between_txn(transactions, address):
    sent_timestamps = []
    received_timestamps = []
    all_timestamps = []
    avg_time_between_sent_tnx = avg_time_between_received_tnx = 0

    for txn in transactions:
        if txn['from'] == address:
            sent_timestamps.append(int(txn['timeStamp']))
            all_timestamps.append(int(txn['timeStamp']))
        elif txn['to'] == address:
            received_timestamps.append(int(txn['timeStamp']))
            all_timestamps.append(int(txn['timeStamp']))

    print("Sent_TS" + str(sent_timestamps))
    print("Ordered_Sent_TS " + str(sent_timestamps.sort()))
    print("received_TS" + str(received_timestamps))

    prev_sent_time = prev_received_time = None
    sent_time_diff = received_time_diff = 0

    for timestamp in sent_timestamps:
        if prev_sent_time is None:
            prev_sent_time = timestamp
        else:
            sent_time_diff += timestamp - prev_sent_time
            prev_sent_time = timestamp
        if len(sent_timestamps) > 1:
            avg_time_between_sent_tnx = round(
                (sent_time_diff / (len(sent_timestamps)-1)) / 60,
                2)
        elif len(sent_timestamps) == 1:
            avg_time_between_sent_tnx = 0

    for timestamp in received_timestamps:
        if prev_received_time is None:
            prev_received_time = timestamp
        else:
            received_time_diff += timestamp - prev_received_time
            prev_received_time = timestamp

        if len(received_timestamps) > 1:
            avg_time_between_received_tnx = round(
                (received_time_diff / (len(received_timestamps) - 1)) / 60,
                2)
        elif len(received_timestamps) == 1:
            avg_time_between_received_tnx = 0

    all_timestamps.sort()
    first_last_time_diff = round((all_timestamps[-1] - all_timestamps[0])/60, 2)
    print(first_last_time_diff)

    return avg_time_between_sent_tnx, avg_time_between_received_tnx, first_last_time_diff
