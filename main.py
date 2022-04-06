# from crypt import methods
from email.policy import default
from itertools import count

from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import requests
import time
import json
import math
import dash_cytoscape as cyto
from dash.dependencies import Input, Output, State
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Our scripts
import dataprocessing as dp
import Model as rf
import netgraph as ng

# app = Flask(__name__)
flask_app = Flask(__name__)
dash_app = Flask('dash')
# tell the app where our db is
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Test.db'
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Test.db'
db = SQLAlchemy(flask_app)
# db = SQLAlchemy(app)

apikey = "R63INQIAZW9HGVSG83R63M477H4YMXDH6Q"

dash = Dash(__name__, server=dash_app, routes_pathname_prefix='/', requests_pathname_prefix='/netgraph/', external_stylesheets=[dbc.themes.BOOTSTRAP])


def is_blacklisted(address):
    with open('blacklist.json') as blacklist_f:
        blacklist = json.load(blacklist_f)
        for entry in blacklist:
            if entry['address'] == address:
                return True
    return False


def get_netgraph_elements(address):
    x, y, r, a, b, c = dp.get_data(address)
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


def init_dash(address):
    dash.layout = dbc.Container(
        children=[
            dbc.Navbar(
                dbc.Container(
                    html.A(
                        dbc.Row(
                            dbc.Col(dbc.NavbarBrand('Ponzified', className='ms-2')),
                            align='centre',
                            className='g-0',
                        ),
                        href="http://127.0.0.1:8080",
                        style={'textDecoration': 'none'},
                    )
                ),
                color='dark',
                dark=True,
            ),
            html.Div([

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
                                # The default curve style does not work with
                                # certain arrows
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
        ]
    )

    # dash.layout = html.Div([
    #
    #     html.P("Nodes Information:"),
    #     cyto.Cytoscape(
    #         id='cytoscape',
    #         elements=get_netgraph_elements(address),
    #         layout={
    #             'name': 'concentric',
    #             'avoidOverlap': True,
    #             'nodeDimesionsIncludeLabels': True,
    #             'spacingFactor': 10,
    #             'minNodeSpacing': 10
    #         },
    #         style={'width': '2000px', 'height': '2000px'},
    #         stylesheet=[
    #             {
    #                 'selector': 'node',
    #                 'style': {
    #                     'label': 'data(id)'
    #                 }
    #             },
    #             {
    #                 'selector': 'edge-point',
    #                 'style': {
    #                     # The default curve style does not work with certain arrows
    #                     'label': 'data(label)',
    #                     'curve-style': 'bezier',
    #                     'target-arrow-color': 'red',
    #                     'target-arrow-shape': 'triangle',
    #                     'font-size': '50px',
    #                     'text-rotation': 'autorotate',
    #                     'text-margin-y': -20
    #                     # 'target-arrow-color': 'blue',
    #                     # 'target-arrow-shape': 'triangle',
    #                 }
    #             },
    #             {
    #                 'selector': '[weight > 9]',
    #                 'style': {
    #                     'line-color': 'red',
    #                 }
    #             },
    #         ]
    #     ),
    # ])


@dash.callback(Output('cytoscape', 'elements'),
                Input('cytoscape', 'tapNodeData'),
                State('cytoscape', 'elements'))
def update_elements(data, elements):
    if data:
        new_elements = get_netgraph_elements(data['id'])
        return new_elements
    else:
        return elements


@flask_app.route('/', methods=['POST', 'GET'])  # parse url string of our application
def index():
    return render_template('index.html')  # change back to index
  

@flask_app.route('/charts/', methods=['GET'])
def charts():
    return render_template('charts.html')


@flask_app.route('/dashboard/', methods=['GET'])
# def netgraph():
#     print("In Netgraph")
#     args = request.args
#     address = args.get("add")
#     print(address)
#     ng.run_app(address)
#     return render_template('netgraph.html', address=address)
def render_netgraph():
    print("in NG")
    args = request.args
    address = args.get("add")
    init_dash(address)
    return redirect('/netgraph/?add={}'.format(address), code=307)


@flask_app.route('/Results/', methods=['POST', 'GET'])
def results():
    if request.method == 'POST':
        address = request.form.get('Wallet Address')
        if is_blacklisted(address):
            print("ADDRESS IS: " + address)
            print("Fraud")
            fraud_val = "Fraudulent"
            data, headings, val, sent_val, received_val, graphdeets = dp.get_data(address)
        else:
            print("In ML ")
            data, headings, val, sent_val, received_val, graphdeets = dp.get_data(address)
            prediction = rf.predict(data)
            fraud_val = prediction
            if prediction == 1:
                print("ADDRESS IS: " + address)
                print("Fraud")
                fraud_val = "Fraudulent"
            elif prediction == 0:
                print("ADDRESS IS: " + address)
                print("Not Fraud")
                fraud_val = "Not Fraudulent"

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
        return render_template('table.html', headings=headings, result=val, fraud=fraud_val, graphdata=graphdeets,
                               address=address.lower(), NGLink="/dashboard/?add="+address)


@flask_app.route('/Diagnostic', methods=['GET'])
def diagnostic():
    rf.diagnostics()
    return render_template("index.html")


@dash_app.route('/', methods=['GET'])
def show_networkgraph():
    args = request.args
    address = args.get("add")
    dash.run_server(address)


main_app = DispatcherMiddleware(flask_app, {
    '/netgraph': dash_app
})

if __name__ == "__main__":
    # server.run(debug=True)   # debug true means error show up on the site
    run_simple('127.0.0.1', 8080, main_app, use_reloader=True, use_debugger=True)
