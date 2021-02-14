import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas
import plotly.graph_objects as go
from plotly.graph_objs.scatter import Line
from plotly.subplots import make_subplots
import subprocess


class Heuristics:
    def __init__(self, server, external_stylesheets, url_path="/dash/"):
        self.app = dash.Dash(
            __name__,
            server=server,
            external_stylesheets=external_stylesheets,
            url_base_pathname=url_path
        )
        self.__properties = {'Variety': 0.2, 'Iterations': 100, 'Sampling_rate': 10}
        self.execute_subprocess()
        self.__figure = make_subplots(rows=self.__properties['Sampling_rate'], cols=1)
        self.create_figure()
        self.app.layout = self.create_layout()

    def execute_subprocess(self, params=None):
        subprocess.call(["gcc", "main.c", "-fopenmp", "-o", "xd"])
        if params is None:
            subprocess.call(["./xd.exe", "1", "0.2", "100", "10"])
        else:
            try:
                subprocess.call(["./xd.exe", "1",
                                 str(params[0]),
                                 str(params[1]),
                                 str(params[2])])
                self.__properties['Variety'] = params[0]
                self.__properties['Iterations'] = params[1]
                self.__properties['Sampling_rate'] = params[1] // params[2]
            except IndexError:
                print("IndexError")

    def _read_output(self, file, days):
        list_of_dataframes = []
        for i in range(0, self.__properties['Sampling_rate']):
            ignore1 = file.readline()
            params = file.readline().split('\t')
            list_of_dataframes.append([pandas.DataFrame(
                {
                    'Days': [j for j in range(1, days, 5)],
                    'Susceptible': list(map(float, file.readline().split('\t'))),
                    'Exposed': list(map(float, file.readline().split('\t'))),
                    'Infected': list(map(float, file.readline().split('\t'))),
                    'Recovered': list(map(float, file.readline().split('\t')))
                }
            ), params])
            ignore2 = file.readline()
        return list_of_dataframes

    def read_output(self, file_name="output.txt"):
        with open(file_name, "r") as file:
            ignore, steps = file.readline().split('\t')

            return self._read_output(file, int(steps) * 5)

    def _create_figure(self, dataframes):
        figures = []
        for i in range(0, self.__properties['Sampling_rate']):
            figure = make_subplots()
            figure.update_layout(
                title_text="Alpha: {}\t Beta: {}\t Gamma: {}\t Sigma: {}\t Reproduction number: {}\t Mixing parameter: {}".format(
                    dataframes[i][1][0],
                    dataframes[i][1][1],
                    dataframes[i][1][2],
                    dataframes[i][1][3],
                    dataframes[i][1][4],
                    dataframes[i][1][5]))
            figure.append_trace(
                go.Scatter(x=dataframes[i][0]['Days'], y=dataframes[i][0]['Susceptible'],
                           name="Susceptible {}".format(i),
                           line=Line({'color': 'blue', 'width': 1})),
                row=1, col=1)
            figure.append_trace(
                go.Scatter(x=dataframes[i][0]['Days'], y=dataframes[i][0]['Exposed'], name="Exposed {}".format(i),
                           line=Line({'color': 'orange', 'width': 1})),
                row=1, col=1)
            figure.append_trace(
                go.Scatter(x=dataframes[i][0]['Days'], y=dataframes[i][0]['Infected'], name="Infected {}".format(i),
                           line=Line({'color': 'red', 'width': 1})),
                row=1, col=1)
            figure.append_trace(
                go.Scatter(x=dataframes[i][0]['Days'], y=dataframes[i][0]['Recovered'], name="Recovered {}".format(i),
                           line=Line({'color': 'green', 'width': 1})),
                row=1, col=1)

            figures.append(figure)

        return figures

    def create_figure(self):
        return self._create_figure(self.read_output())

    def create_graph_div(self):
        figures = self.create_figure()
        return html.Div([dcc.Graph(figure=fig, animate=True) for fig in figures], id='funny-graphs')

    def create_layout(self):
        return html.Div([
            html.H1(children="Top scores", style={'text-align': 'center'}),

            html.Div(children=[
                html.Label('Variety'),
                dcc.Input(value=0.2, type='number', step=0.1, id='variety', min=0.1, max=0.9),

                html.Label('Iterations'),
                dcc.Input(value=100, type='number', step=100, id='iterations', min=100),

                html.Label('Sampling rate'),
                dcc.Input(value=10, type='number', step=10, id='rate', min=10),
            ], style={'columnCount': 3, 'text-align': 'center', 'padding': 0}),

            self.create_graph_div()

        ], id="topGraphs")

    def reload_plots(self, params):
        self.execute_subprocess(params)
        self.__figure = make_subplots(rows=self.__properties['Sampling_rate'], cols=1)
        return self.create_graph_div()
