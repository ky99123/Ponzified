# from config import apikey
from dataprocessing import apikey
import requests
from datetime import datetime
from dash import Dash, html, dcc
import dash_cytoscape as cyto
from dash.dependencies import Input, Output,State
import json

dash_app = Dash(__name__)


def get_data(address):
    req = requests.get("https://api.etherscan.io/api?module=account&action=txlist&address=" + address + "&startblock=0&endblock=99999999&page=1&offset=10000&sort=desc&tag=latest&apikey=" + apikey).json()
    return req['result']


def get_netgraph_elements(address):
    r = get_data(address)
    print(r)
    elements = []
    added_edges = []
    count_transactions = {}

    for node in r:
        source = str(node['from'])
        dest = str(node['to'])
        uid = source + dest
        if uid not in count_transactions:
            count_transactions[uid] = 1
        elif uid in count_transactions:
            count_transactions[uid] += 1

    for node in r:
        source = str(node['from'])
        dest = str(node['to'])
        uid = source + dest

        if (source and dest) and (uid not in added_edges):
            elements.append({'data': {'id': source, 'label': source}})
            elements.append({'data': {'id': dest, 'label': dest}})
            if max(count_transactions, key=count_transactions.get) == uid:
                elements.append({'data': {'source': source, 'target': dest, 'label': str(count_transactions[uid]), 'weight': 10}, 'classes': 'edge-point'})
            else:
                elements.append({'data': {'source': source, 'target': dest, 'label': str(count_transactions[uid])},'classes':'edge-point'})
            added_edges.append(uid)


    return elements


def run_app(address):
    dash_app.layout = html.Div([
        html.P("Nodes Information:"),
        cyto.Cytoscape(
            id='cytoscape',
            elements=get_netgraph_elements(address),
            layout={
                'name': 'concentric',
                'avoidOverlap': True,
                'nodeDimesionsIncludeLabels': True,
                'spacingFactor': 10,
                'minNodeSpacing': 10
            },
            style={'width': '2000px', 'height': '2000px'},
            stylesheet=[
                {
                    'selector': 'node',
                    'style': {
                        'label': 'data(id)'
                    }
                },
                {
                    'selector': 'edge-point',
                    'style': {
                        # The default curve style does not work with certain arrows
                        'label': 'data(label)',
                        'curve-style': 'bezier',
                        'target-arrow-color': 'red',
                        'target-arrow-shape': 'triangle',
                        'font-size': '50px',
                        'text-rotation': 'autorotate',
                        'text-margin-y': -20
                        # 'target-arrow-color': 'blue',
                        # 'target-arrow-shape': 'triangle',
                    }
                },
                {
                    'selector': '[weight > 9]',
                    'style': {
                        'line-color': 'red',
                    }
                },
            ]
        ),
    ])

    @dash_app.callback(Output('cytoscape', 'elements'),
                Input('cytoscape', 'tapNodeData'),
                State('cytoscape', 'elements'))
    def update_elements(data, elements):
        if data:
            new_elements = get_netgraph_elements(data['id'])
            return new_elements
        else:
            return elements

            # run_app(data['id'])

    dash_app.run_server(debug=False)
    return


# run_app("0xdb5c43a65e23481b714ef19f462d467d4eb85826")

if __name__ == "__main__":
    get_netgraph_elements('0xdb5c43a65e23481b714ef19f462d467d4eb85826')
