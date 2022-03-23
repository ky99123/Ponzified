#from crypt import methods
from email.policy import default
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import requests
import time
import json
import math


app = Flask(__name__)
#tell the app where our db is
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Test.db'
db = SQLAlchemy(app)

apikey = "R63INQIAZW9HGVSG83R63M477H4YMXDH6Q"


def filter_address(address):
    notblacklisted = True
    with open('blacklist.json') as blacklist:
        data = json.load(blacklist)
        for item in data:
            if item['address'] == address:
                notblacklisted=False
                return notblacklisted
                #return item['comment']
        #return "Address not blacklisted!"
        return notblacklisted


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
        if (filter_address(address)):
            print ("ADDRESS IS: " + address)
            #then call the Machine learning process
        #else:
            #skip the machine learning process
            #continue
    req = requests.get(
        "https://api.etherscan.io/api?module=account&action=txlist&address=" + address + "&startblock=0&endblock=99999999&page=1&offset=50&sort=desc&tag=latest&apikey=" + apikey).json()
    val = req['result']
    balreq=requests.get("https://api.etherscan.io/api?module=account&action=balance&address=" + address + "&tag=latest&apikey=" + apikey).json()
    bal=balreq['result']
    index = 0
    headings = []
    test = val[0]
 #for data cleaning portion
    findmax=[]
    findreceived=[]
    findsent=[]
    avgtracker=0
    total=0
    senttrans =0
    tracker=0
    timestamp=[]
    uniquesender=[]
    difference = 0 
    rectrans=0
    for key1 in test.keys():
        headings.append(key1)

    for i in val:
        if (i["from"] == address.lower()):
            senttrans+=1 #To get total number of sent transactions
            findmax.append(int(i["value"]))
            #timeval = datetime.strptime(i["timeStamp"], '%Y-%m-%d %H:%M')
            timestamp.append(int(i["timeStamp"]))
            avgtracker+=1
            total+=int(i["value"])
            if (i["to"] not in findsent):
                findsent.append(i["to"])
       
        else:
            rectrans+=1
            if (i["from"] not in uniquesender):
                uniquesender.append(i["from"])
            findreceived.append(int(i["value"]))    

    while index < len(val):
        for key,value in val[index].items():
            #Get the time difference thing first
            #Convert timestamp
            if (key == "timeStamp"):
                testtime=time.strftime('%Y-%m-%d %H:%M', time.localtime(int(value)))
                value = value.replace(value,testtime)
                val[index].update({"timeStamp": value})        
        index += 1    
            
    headings = tuple(headings)
    for x in range(len(timestamp)): 
        if (tracker < senttrans-1):
            diff = timestamp[x] - timestamp[x+1]
            print(diff)
            difference += diff
        tracker +=1            

    #convert difference from seconds to minutes
    difference = math.ceil((difference/60)/senttrans)
    alltrans = rectrans+ senttrans

    try:
        print("max sent:", max(findmax)/1000000000000000000)
        print("min sent:", min(findmax)/1000000000000000000)
        print("max received", max(findreceived)/1000000000000000000)
        print("min received", min(findreceived)/1000000000000000000)
        print("avg sent:", (total/avgtracker)/1000000000000000000)
        print("total:", total/1000000000000000000)
        print("unique recieved addresses:", uniquesender) #can just use count if need the number of unique received address instead
        #print("unique sents:", findsent)
        print("acc balance",int(bal)/1000000000000000000,"ether")
        print("total number of sent trans:", senttrans)
        #print("Timestamps:", timestamp)
        print("Average min between sent transactions (minutes):", difference)
        print("Number of received transactions:", rectrans)
        print("Total of ALL transactions:",alltrans )
    except:
        print("something went wrong")

    return render_template('table.html', headings= headings, result=val)


if __name__ == "__main__":
    app.run(debug=True) #debug true means error show up on the site