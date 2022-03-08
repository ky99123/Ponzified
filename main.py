#from crypt import methods
from email.policy import default
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import requests
import time


app = Flask(__name__)
#tell the app where our db is
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Test.db'
db = SQLAlchemy(app)

apikey = "R63INQIAZW9HGVSG83R63M477H4YMXDH6Q"


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String(200))
    #method = db.Column(db.String(200),nullable=False)

    def __repr__(self):
        return '<Task %r>' %self.hash 


@app.route('/',methods=['POST', 'GET']) #parse url string of our application

def index():
    return render_template('index.html')
  

@app.route('/charts/', methods=['GET'])
def input():
    return render_template('charts.html')

@app.route('/Results/', methods=['POST', 'GET'])
def results():
    if request.method == 'POST':
        address = request.form.get('Wallet Address')
        print ("ADDRESS IS: " + address)
    req = requests.get(
        "https://api.etherscan.io/api?module=account&action=txlist&address=" + address + "&startblock=0&endblock=99999999&page=1&offset=50&sort=desc&tag=latest&apikey=" + apikey).json()
    val = req['result']
    index = 0
    headings = []
    test = val[0]
    for key1,value1 in test.items():
        headings.append(key1)

    while index < len(val):
        for key,value in val[index].items():
            #Convert timestamp
            if (key == "timeStamp"):
                testtime=time.strftime('%Y-%m-%d %H:%M', time.localtime(int(value)))
                value = value.replace(value,testtime)
                val[index].update({"timeStamp": value})
        index += 1
    headings = tuple(headings)
    
    return render_template('table.html', headings= headings, result=val)


if __name__ == "__main__":
    app.run(debug=True) #debug true means error show up on the site