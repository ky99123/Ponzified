#from crypt import methods
from email.policy import default
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
#tell the app where our db is
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Test.db'
db = SQLAlchemy(app)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String(200))
    #method = db.Column(db.String(200),nullable=False)

    def __repr__(self):
        return '<Task %r>' %self.hash 


@app.route('/',methods=['POST', 'GET']) #parse url string of our application

def index():
    return render_template('index.html')
    #if request.method=="POST":
     #   hash_content = request.form.get('address',None)
      #  print (hash_content)
       # new_task = Test(hash=hash_content)

        #try:
         #   db.session.add(new_task)
          #  db.session.commit()
            #return render_template('index.html')
           # return redirect('table.html')
            #return "tESTING"
        
        #except SQLAlchemyError as e:
         #   print (e)
          #  return 'fail'
    #else:
     #   return render_template('index.html')

#to search wallet
@app.route('/Search Address/')
def input():
    return render_template('charts.html')

#By right, call sy's crawling thing to pull transactions for viewing
@app.route('/Results/', methods=['POST', 'GET'])
def results():
    return render_template('table.html')


if __name__ == "__main__":
    app.run(debug=True) #debug true means error show up on the site