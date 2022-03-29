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

# Our scripts
import dataprocessing as dp
import Model as rf

app = Flask(__name__)
# tell the app where our db is
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Test.db'
db = SQLAlchemy(app)

apikey = "R63INQIAZW9HGVSG83R63M477H4YMXDH6Q"


def is_blacklisted(address):
    with open('blacklist.json') as blacklist_f:
        blacklist = json.load(blacklist_f)
        for entry in blacklist:
            if entry['address'] == address:
                return True
    return False


@app.route('/', methods=['POST', 'GET'])  # parse url string of our application
def index():
    return render_template('index.html') #change back to index
  

@app.route('/charts/', methods=['GET'])
def charts():
    return render_template('charts.html')


@app.route('/Results/', methods=['POST', 'GET'])
def results():
    fraudval = False
    if request.method == 'POST':
        address = request.form.get('Wallet Address')
        if is_blacklisted(address):
            print("ADDRESS IS: " + address)
            print("Fraud")
            fraudval = True
            data, headings, val = dp.get_data(address)
        else:
            print("In ML ")
            data, headings, val = dp.get_data(address)
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
        return render_template('table.html', headings=headings, result=val, fraud=fraudval)


@app.route('/Diagnostic', methods=['GET'])
def diagnostic():
    rf.diagnostics()
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)   # debug true means error show up on the site
