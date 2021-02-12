import os
from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object((os.environ['APP_SETTINGS']))


@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template("home.html")


@app.route('/main')
def main_simulation():
    return render_template("main.html")


if __name__ == '__main__':
    app.run()
