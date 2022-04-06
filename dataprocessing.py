import requests
import time
from config import apikey


def get_data(address):
    """
    Overall Wrapper function for getting and processing data from Etherscan API
    :param str address:         Address to be queried
    :return: data, headings, txn_data, sent_vals, received_vals, graphdict
    """

    address = address.lower()

    # Get Transaction Data
    txn_req = requests.get(
        "https://api.etherscan.io/api?module=account&action=txlist&address="
        + address + "&startblock=0&endblock=99999999&page=1&offset=200&sort"
                    "=desc&tag=latest&apikey=" + apikey)
    txn_data = txn_req.json()["result"]

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
    sent_count, min_sent, max_sent, avg_sent, total_ether_sent, sent_vals, \
        received_count, min_received, max_received, avg_received, total_ether_received, received_vals,\
        unique_received_from_address = get_txn_data(txn_data, address)

    # Get Processed Timestamp Data
    avg_time_between_sent_tnx, avg_time_between_received_tnx, \
        first_last_time_diff, sent_ts, received_ts = get_time_between_txn(txn_data, address)

    # Get Ether Balance
    total_ether_balance = int(balance_data)

    # Assemble Data into list
    data = [avg_time_between_sent_tnx, avg_time_between_received_tnx,
            first_last_time_diff, sent_count, received_count,
            unique_received_from_address, min_received,
            max_received, avg_received, min_sent, max_sent, avg_sent,
            sent_count + received_count, total_ether_sent, total_ether_received,
            total_ether_balance]
    sent_avg = []
    received_avg = []

    sent_vals = list(map(lambda x: x / 1000000000000000000, sent_vals))
    received_vals = list(map(lambda x: x / 1000000000000000000, received_vals))

    for txn in sent_vals:
        sent_avg.append(avg_sent / 1000000000000000000)

    for txn in received_vals:
        received_avg.append(avg_received / 1000000000000000000)

    graphdict = [sent_vals[::-1], sent_ts, sent_avg, received_vals[::-1], received_ts, received_avg]

    return data, headings, txn_data, sent_vals, received_vals, graphdict


def get_txn_data(transactions, address):
    """
    Process Transaction data and perform aggregation of various attributes
    :param transactions:    list of Transactions
    :param address:         Address being explored
    :return:
    """
    sent_count = received_count = 0
    sent_txn_values = []
    received_txn_values = []
    received_address = []

    # Get Count of sent and received transactions and the value of each transaction
    for txn in transactions:
        if txn['from'] == address:
            sent_count += 1
            if txn['value'] is not None:
                sent_txn_values.append(int(txn['value']))
            else:
                sent_txn_values.append(0)

        elif txn['to'] == address:
            received_count += 1
            if txn['value'] is not None:
                received_txn_values.append(int(txn['value']))
            else:
                received_txn_values.append(0)
            received_address.append(txn['from'])

    # Perform aggregation of Data
    if len(sent_txn_values) == 0:
        sent_txn_values = [0]
    min_sent = min(sent_txn_values)
    max_sent = max(sent_txn_values)
    total_ether_sent = sum(sent_txn_values)
    avg_sent = total_ether_sent / len(sent_txn_values)

    if len(received_txn_values) == 0:
        received_txn_values = [0]
    min_received = min(received_txn_values, default=0)
    max_received = max(received_txn_values, default=0)
    total_ether_received = sum(received_txn_values)
    avg_received = total_ether_received / len(received_txn_values)
    received_address = list(set(received_address))

    return sent_count, min_sent, max_sent, avg_sent, total_ether_sent, sent_txn_values, \
        received_count, min_received, max_received, avg_received, total_ether_received, received_txn_values,\
        len(received_address)


def get_time_between_txn(transactions, address):
    """
    Process time related Transaction data and perform aggregation
    :param transactions:    list of Transactions
    :param address:         Address being explored
    :return:
    """
    sent_timestamps = []
    received_timestamps = []
    all_timestamps = []
    avg_time_between_sent_tnx = avg_time_between_received_tnx = 0

    # Get Timestamps of transactions
    for txn in transactions:
        if txn['from'] == address:
            sent_timestamps.append(int(txn['timeStamp']))
            all_timestamps.append(int(txn['timeStamp']))
        elif txn['to'] == address:
            received_timestamps.append(int(txn['timeStamp']))
            all_timestamps.append(int(txn['timeStamp']))

    prev_sent_time = prev_received_time = None
    sent_time_diff = received_time_diff = 0

    # Get average time between Sent Transactions
    for timestamp in sent_timestamps:
        if prev_sent_time is None:
            prev_sent_time = timestamp
        else:
            sent_time_diff += timestamp - prev_sent_time
            prev_sent_time = timestamp
        if len(sent_timestamps) > 1:
            avg_time_between_sent_tnx = round(
                (sent_time_diff / (len(sent_timestamps) - 1)) / 60,
                2)
        elif len(sent_timestamps) == 1:
            avg_time_between_sent_tnx = 0

    # Get average time between Received Transactions
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

    # Get Time Difference between First and Last Transaction
    all_timestamps.sort()
    first_last_time_diff = round((all_timestamps[-1] - all_timestamps[0]) / 60, 2)

    # Normalize timestamps from epoch to local timezone
    temp_arr = []

    for value in sent_timestamps:
        time_str = time.strftime('%Y-%m-%d %H:%M',
                                 time.localtime(int(value)))
        temp_arr.append(time_str)

    sent_timestamps = temp_arr

    temp_arr = []

    for value in received_timestamps:
        time_str = time.strftime('%Y-%m-%d %H:%M',
                                 time.localtime(int(value)))
        temp_arr.append(time_str)

    received_timestamps = temp_arr

    return avg_time_between_sent_tnx, avg_time_between_received_tnx, first_last_time_diff, sent_timestamps[::-1],\
        received_timestamps[::-1]
