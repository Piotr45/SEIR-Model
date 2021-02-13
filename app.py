import os
from flask import Flask, render_template, url_for, request
import dash
import pandas

app = Flask(__name__)

app.config.from_pyfile('config.py')


@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        latency_period = request.form['latencyPeriod']
        infection_period = request.form['infectiousPeriod']
        immunity_period = request.form['immunityPeriod']
        print(f"{latency_period} {infection_period} {immunity_period}")
        return render_template("home.html", title="home",
                               alpha="{}".format(round((1 / latency_period)), 5),
                               beta="{}".format(0.31429),
                               sigma="{}".format(round(count_days(immunity_period), 5)),
                               gamma="{}".format(round((1 / infection_period), 5)))
    else:
        print("in")
        return render_template("home.html", title="home",
                               alpha="{}".format(round((1 / 5), 5)),
                               beta="{}".format(0.31429),
                               sigma="{}".format(0.00549),
                               gamma="{}".format(round((1 / 7), 5)))


@app.route('/main')
def main_simulation():
    return render_template("main.html")


def count_days(immunity_period):
    if immunity_period == "6 Months":
        return 1 / (31 + 28 + 31 + 30 + 31 + 30)


if __name__ == '__main__':
    app.run()
