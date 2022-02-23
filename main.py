from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return """<form action="" method="get">
                <input type="text" name="celsius">
                <input type="submit" value="Convert">
              </form>"""