# Imports
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from flask import Flask, render_template, request, redirect, url_for,flash
import time
import json
import dash_cytoscape as cyto
from dash.dependencies import Input, Output, State
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from web3 import Web3

# Our scripts
from config import secretkey
import dataprocessing as dp
import Model as rf

# Constants
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

# Initialise main Flask app and
# Flask app to contain Dash app
flask_app = Flask(__name__)
dash_app = Flask('dash')
flask_app.secret_key = secretkey

# Initialise Dash app, contained under the server 'dash_app'
dash = Dash(__name__,
            server=dash_app,
            routes_pathname_prefix='/',
            requests_pathname_prefix='/netgraph/',
            external_stylesheets=[dbc.themes.BOOTSTRAP]
            )


def is_blacklisted(address):
    """
    Checks if a particular address is known to be Fraudulent
    :param str address:     Address to check for in blacklist
    :return:                Boolean of whether the address is in the black list
    """
    with open('blacklist.json') as blacklist_f:
        blacklist = json.load(blacklist_f)
        for entry in blacklist:
            if entry['address'] == address:
                return True
    return False


def get_netgraph_elements(address):
    """
    Gets all the addresses associated with the provided address
    :param str address:     Address to explore
    -----------------------------------------------------------
    :return elements:       list of elements to plot network graph
    """
    r = dp.get_data(address)[2]
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
    """
    Initialises Dash Application for rendering of Network graphs
    :param str address:     Wallet Address to be explored
    """

    # Define the Markup for the Search Bar
    search_bar = dbc.Row(
        [
            dbc.Col(dcc.Input(id='in_address', type='text')),
        ],
        className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
        align="center",
    )

    # Define the Markup for the Navigation bar
    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                            dbc.Col(
                                dbc.NavbarBrand("Ponzified", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="http://127.0.0.1:8080",       # Redirects back to landing page
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                dbc.Collapse(
                    search_bar,
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                ),
            ]
        ),
        color="dark",
        dark=True,
    )

    # Defining the layout of the Dash app
    dash.layout = dbc.Container(
        children=[
            navbar,
            html.Div([
                html.P("Nodes Information:"),

                # Defining the Network Graph built with Dash Cytoscape
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

                                'label': 'data(label)',
                                'curve-style': 'bezier',
                                'target-arrow-color': 'red',
                                'target-arrow-shape': 'triangle',
                                'font-size': '50px',
                                'text-rotation': 'autorotate',
                                'text-margin-y': -20
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


@dash.callback(Output('cytoscape', 'elements'),
               Output('in_address', 'value'),
               Input('in_address', 'value'),
               Input('cytoscape', 'tapNodeData'),
               State('cytoscape', 'elements'))
def update_elements(in_address, data, elements):
    """
    Updates the Network Graph based on existing elements and various Inputs
    :param str in_address:      Search string within the search bar
    :param list data:           Data of the existing nodes
    :param list elements:       State of the elements within the Network Graph
    ----------------------------------------------------------------------
    :return:                    Data to populate the network graph and
    an empty string to clear the search bar
    """
    # Checks for valid input in the search bar
    if in_address:
        new_data = get_netgraph_elements(in_address)
        return new_data, ''
    else:
        # Checks if User has selected an existing node
        if data:
            new_elements = get_netgraph_elements(data['id'])
            return new_elements, ''
        else:
            return elements, ''


@dash.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@flask_app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')


@flask_app.route('/dashboard/', methods=['GET'])
def render_netgraph():
    """
    Prepare the Network Graph
    :return:
    """
    args = request.args
    address = args.get("add")
    # Check if someone tried to pass an empty parameter
    if address is None:
        # Replace with placeholder wallet address
        address = '0x949d4a80dd439d66d88406C0AB903C2B17eD2061'
    init_dash(address)
    return redirect('/netgraph/?add={}'.format(address), code=307)


@flask_app.route('/Results/', methods=['POST', 'GET'])
def results():
    if request.method == 'POST':
        address = request.form.get('Wallet Address')
        # address input validation
        
        if Web3.isAddress(address):
            print("valid")
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
        else:
            flash("Invalid Ethereum address provided. Please try again")
            return redirect('/Flash')
        return render_template('table.html', headings=headings, result=val, fraud=fraud_val, graphdata=graphdeets,
                               address=address.lower(), NGLink="/dashboard/?add="+address)


@flask_app.route('/Flash')
def flashmsg():
    return render_template("flashmsg.html")

# Legacy

# @flask_app.route('/Diagnostic', methods=['GET'])
# def diagnostic():
#     rf.diagnostics()
#     return render_template("index.html")


@dash_app.route('/', methods=['GET'])
def show_networkgraph():
    args = request.args
    address = args.get("add")
    dash.run_server(address)


main_app = DispatcherMiddleware(flask_app, {
    '/netgraph': dash_app
})

if __name__ == "__main__":
    run_simple('127.0.0.1', 8080, main_app, use_reloader=True, use_debugger=False)
