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
    return render_template('index.html')
  

@app.route('/charts/', methods=['GET'])
def charts():
    return render_template('charts.html')


@app.route('/Results/', methods=['POST', 'GET'])
def results():
    if request.method == 'POST':
        address = request.form.get('Wallet Address')
        if is_blacklisted(address):
            print("ADDRESS IS: " + address)
            print("Fraud")
            data, headings, val = dp.get_data(address)
        else:
            data, headings, val = dp.get_data(address)
            if rf.predict(data):
                print("ADDRESS IS: " + address)
                print("Fraud")
            else:
                print("ADDRESS IS: " + address)
                print("Not Fraud")

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
            i += 1
        return render_template('table.html', headings=headings, result=val)


if __name__ == "__main__":
    app.run(debug=True)   # debug true means error show up on the site
