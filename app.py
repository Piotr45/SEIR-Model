from flask import Flask, render_template, url_for, request
import plotly.express as px
from dash.dependencies import Output, Input, State
import subprocess
from src.main_app_dash import Calculator
from heuristics_app_dash import Heuristics

server = Flask(__name__)

server.config.from_pyfile('config.py')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

calc = Calculator(server=server, external_stylesheets=external_stylesheets)
app = calc.app

heuristic = Heuristics(server=server, external_stylesheets=external_stylesheets, url_path="/top10/")
heuristic_app = heuristic.app


@app.callback(Output("test-graph", 'figure'),
              Input('days_of_simulation', 'value'),
              Input('reproduction', 'value'),
              Input('latency-period', 'value'),
              Input('infectious-period', 'value'),
              Input('mixing', 'value'),
              Input('dropdown', 'value'))
def update_output(days, reproduction, latency, infectious, mixing, immunity):
    subprocess.call(["./a.exe", "0", str(days), str(reproduction),
                     str(mixing), str(1 / latency), str(reproduction * (1 / infectious)), str(1 / infectious),
                     str(calc.count_days(immunity))])
    calc.__data = calc.create_dataframe(days=days)
    return px.line(data_frame=calc.__data, x='Days', y=calc.__data.columns)


@server.route('/')
@server.route('/dash/')
def my_dash_app():
    return app.index()


@server.route('/top10/')
def main_simulation():
    return heuristic_app.index()


if __name__ == '__main__':
    server.run()
