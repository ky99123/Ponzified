from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_nav import Nav

app = Flask(__name__)
#tell the app where our db is
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'

@app.route('/', methods=['POST','GET']) #parse url string of our application

def index():
    if request.method=='POST':
        return render_template('input.html')
    else:
        return render_template('index.html')

def userinput():
    return render_template('input.html')

#here we define our menu items
topbar = Navbar(logo,
                View('News', 'get_news'),
                View('Live', 'get_live'),
                View('Programme', 'get_programme'),
                View('Classement', 'get_classement'),
                View('Contact', 'get_contact'),
                )

# registers the "top" menubar
nav = Nav()
nav.register_element('top', topbar)

if __name__ == "__main__":
    app.run(debug=True) #debug true means error show up on the site