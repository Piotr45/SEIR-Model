import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas
import plotly.express as px
import subprocess


class Calculator:
    def __init__(self, server, external_stylesheets, url_path="/dash/"):
        self.app = dash.Dash(
            __name__,
            server=server,
            external_stylesheets=external_stylesheets,
            url_base_pathname=url_path
        )
        self.execute_subprocess()
        self.__data = self.create_dataframe()
        self.__figure = px.line(data_frame=self.__data, x='Days', y=self.__data.columns)
        self.app.layout = self.create_layout()

    @staticmethod
    def execute_subprocess(params=None):
        subprocess.call(["gcc", "main.c", "-fopenmp"])
        if params is None:
            subprocess.call(["./a.exe", "0", "365", "2.2", "1", "0.2", "0.31429", "0.14286", "0.00549"])
        else:
            try:
                subprocess.call(["./a.exe", "0",
                                 str(params[0]),
                                 str(params[1]),
                                 str(params[2]),
                                 str(params[3]),
                                 str(params[4]),
                                 str(params[5]),
                                 str(params[6])])
            except IndexError:
                print("IndexError")

    @staticmethod
    def read_file(file_name):
        file = open(file_name, "r")
        ignore, steps = file.readline().split('\t')
        return {'Simulation_numbers': ignore,
                'Steps': int(steps),
                'Number': int(file.readline()),
                'Params': list(map(float, file.readline().split('\t'))),
                'Susceptible': list(map(float, file.readline().split('\t'))),
                'Exposed': list(map(float, file.readline().split('\t'))),
                'Infected': list(map(float, file.readline().split('\t'))),
                'Recovered': list(map(float, file.readline().split('\t')))
                }

    def create_dataframe(self, file_name="output.txt", days=365):
        __properties = self.read_file(file_name)

        dataframe = pandas.DataFrame(
            {
                'Days': [i for i in range(1, __properties['Steps'] * 5, 5)],
                'Susceptible': __properties['Susceptible'],
                'Exposed': __properties['Exposed'],
                'Infected': __properties['Infected'],
                'Recovered': __properties['Recovered']
            }
        )
        return dataframe

    def create_layout(self):
        return html.Div([
            html.H1(children="SEIR Model", style={'text-align': 'center'}),

            html.Label('Days of simulation'),
            dcc.Input(value=365, type='number', step=1, id='days_of_simulation'),

            html.Label('Basic reproduction number'),
            dcc.Input(value=2.2, type='number', step=0.1, id='reproduction'),

            html.Label('Mixing parameter'),
            dcc.Input(value=1, type='number', step=0.1, min=1, id='mixing'),

            html.Label('Latency period'),
            dcc.Input(value=5, type='number', step=1, id='latency-period', min=2, max=20),

            html.Label('Infectious period'),
            dcc.Input(value=7, type='number', step=1, id='infectious-period', min=2, max=20),

            html.Label('Immunity period'),
            dcc.Dropdown(
                id="dropdown",
                options=[
                    {'label': '1 week', 'value': '1w'},
                    {'label': '1 month', 'value': '1m'},
                    {'label': '6 months', 'value': '6m'},
                    {'label': '1 year', 'value': '1y'},
                    {'label': '5 years', 'value': '5y'},
                ],
                value='6m',
                style={"width": "32%"},
            ),

            dcc.Graph(id="test-graph", figure=self.__figure, animate=True)
        ])

    @staticmethod
    def count_days(immunity_period):
        if immunity_period == "1w":
            return 1 / 7
        if immunity_period == "1m":
            return 1 / 30
        if immunity_period == "6m":
            return 1 / (31 + 28 + 31 + 30 + 31 + 30)
        if immunity_period == "1y":
            return 1 / 365
        if immunity_period == "5y":
            return 1 / (366 + 4 * 365)
