# from crypt import methods
from email.policy import default
from itertools import count
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import requests
import time
import json
import math
from dash import Dash, html,dcc
import dash_cytoscape as cyto
from dash.dependencies import Input, Output,State
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Our scripts
import dataprocessing as dp
import Model as rf

server = Flask(__name__)
# tell the app where our db is
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Test.db'
db = SQLAlchemy(server)

apikey = "R63INQIAZW9HGVSG83R63M477H4YMXDH6Q"

app = Dash(__name__, server=server, url_base_pathname='/dashboard/')

def is_blacklisted(address):
    with open('blacklist.json') as blacklist_f:
        blacklist = json.load(blacklist_f)
        for entry in blacklist:
            if entry['address'] == address:
                return True
    return False


def get_data(address):
    req = requests.get(
        "https://api.etherscan.io/api?module=account&action=txlist&address=" + address + "&startblock=0&endblock=99999999&page=1&offset=10000&sort=desc&tag=latest&apikey=" + apikey).json()
    return req['result']


def get_netgraph_elements(address):
    r = get_data(address)
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
                elements.append(
                    {'data': {'source': source, 'target': dest, 'label': str(count_transactions[uid]), 'weight': 10},
                     'classes': 'edge-point'})
            else:
                elements.append({'data': {'source': source, 'target': dest, 'label': str(count_transactions[uid])},
                                 'classes': 'edge-point'})
            added_edges.append(uid)

    return elements

app.layout = html.Div([
        html.P("Nodes Information:"),
        cyto.Cytoscape(
            id='cytoscape',
            elements=get_netgraph_elements("0xdb5c43a65e23481b714ef19f462d467d4eb85826"),
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

@server.route('/', methods=['POST', 'GET'])  # parse url string of our application
def index():
    return render_template('index.html') #change back to index
  

@server.route('/charts/', methods=['GET'])
def charts():
    return render_template('charts.html')


@server.route('/dashboard', methods=['GET'])
# def netgraph():
#     print("In Netgraph")
#     args = request.args
#     address = args.get("add")
#     print(address)
#     return render_template('netgraph.html', address=address)
def render_netgraph():
    args =request.args
    address = args.get("add")
    return Flask.redirect('/netgraph', args1=address)

# @server.route('/netgraph')


@server.route('/Results/', methods=['POST', 'GET'])
def results():
    fraudval = False
    if request.method == 'POST':
        address = request.form.get('Wallet Address')
        if is_blacklisted(address):
            print("ADDRESS IS: " + address)
            print("Fraud")
            fraudval = True
            data, headings, val, graphdeets = dp.get_data(address)
        else:
            print("In ML ")
            data, headings, val,graphdeets = dp.get_data(address)
            print(data)
            prediction = rf.predict(data)
            fraudval = prediction
            if prediction == 1:
                print("ADDRESS IS: " + address)
                print("Fraud")
                fraudval = True
            elif prediction == 0:
                print("ADDRESS IS: " + address)
                print("Not Fraud")
                fraudval = False

        i = 0
        while i < len(val):
            for key, value in val[i].items():
                # Get the time difference thing first
                # Convert timestamp
                if key == "timeStamp":
                    time_str = time.strftime('%Y-%m-%d %H:%M',
                                             time.localtime(int(value)))
                    value = value.replace(value, time_str)
                    val[i].update({"timeStamp": value})
                if key == "value":
                    value = int(value)/1000000000000000000
                    val[i].update({"value": value})
                
                if key == "gasPrice":
                    value = int(value)/1000000000
                    val[i].update({"gasPrice": value})
            i += 1
<<<<<<< Updated upstream
        return render_template('table.html', headings=headings, result=val, fraud=fraudval, graphdata=graphdeets,NGLink="/Netgraph/?add="+address)
=======
        return render_template('table.html', headings=headings, result=val, fraud=fraud_val, graphdata=graphdeets,
                               address=address.lower(), NGLink="/dashboard/?add="+address)
>>>>>>> Stashed changes


@server.route('/Diagnostic', methods=['GET'])
def diagnostic():
    rf.diagnostics()
    return render_template("index.html")

# with app.app_context():
#     from netgraph import run_app
#     app = run_app(app)
#     return app

main_app = DispatcherMiddleware(server, {
    '/netgraph' : app.server
})

if __name__ == "__main__":
    run_simple('0.0.0.0', 8080, main_app, use_reloader=True, use_debugger=True)  # debug true means error show up on the site
