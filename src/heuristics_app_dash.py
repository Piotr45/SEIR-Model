import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas
import plotly.express as px
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
        self.__properties = {'Variety': 0.2, 'Iterations': 100, 'Top_score_number': 10}
        self.execute_subprocess()
        self.__figure = make_subplots(rows=self.__properties['Top_score_number'], cols=1)
        self.create_figure()
        self.app.layout = self.create_layout()

    def execute_subprocess(self, params=None):
        subprocess.call(["gcc", "main.c", "-fopenmp", "-o", "xd"])
        if params is None:
            subprocess.call(["./xd.exe", "1", "0.2", "100", "10"])
        else:
            try:
                subprocess.call(["./a.exe", "0",
                                 str(params[0]),
                                 str(params[1]),
                                 str(params[2])])
                self.__properties['Variety'] = params[0]
                self.__properties['Iterations'] = params[1]
                self.__properties['Top_score_number'] = params[2]
            except IndexError:
                print("IndexError")

    def _read_output(self, file, days):
        list_of_dataframes = []
        for i in range(0, self.__properties['Top_score_number']):
            ignore1 = file.readline()
            params = file.readline()

            list_of_dataframes.append(pandas.DataFrame(
                {
                    'Days': [j for j in range(1, days, 5)],
                    'Susceptible': list(map(float, file.readline().split('\t'))),
                    'Exposed': list(map(float, file.readline().split('\t'))),
                    'Infected': list(map(float, file.readline().split('\t'))),
                    'Recovered': list(map(float, file.readline().split('\t')))
                }
            ))
            ignore2 = file.readline()
        file.close()
        return list_of_dataframes

    def read_output(self, file_name="output.txt"):
        file = open(file_name, "r")
        ignore, steps = file.readline().split('\t')

        return self._read_output(file, int(steps) * 5)

    def _create_figure(self, dataframes):
        figures = []
        for i in range(0, self.__properties['Top_score_number']):
            figure = make_subplots()

            figure.append_trace(
                go.Scatter(x=dataframes[i]['Days'], y=dataframes[i]['Susceptible'], name="Susceptible {}".format(i),
                           line=Line({'color': 'blue', 'width': 1})),
                row=1, col=1)
            figure.append_trace(
                go.Scatter(x=dataframes[i]['Days'], y=dataframes[i]['Exposed'], name="Exposed {}".format(i),
                           line=Line({'color': 'orange', 'width': 1})),
                row=1, col=1)
            figure.append_trace(
                go.Scatter(x=dataframes[i]['Days'], y=dataframes[i]['Infected'], name="Infected {}".format(i),
                           line=Line({'color': 'red', 'width': 1})),
                row=1, col=1)
            figure.append_trace(
                go.Scatter(x=dataframes[i]['Days'], y=dataframes[i]['Recovered'], name="Recovered {}".format(i),
                           line=Line({'color': 'green', 'width': 1})),
                row=1, col=1)

            figures.append(figure)

        return figures

    def create_figure(self):
        return self._create_figure(self.read_output())

    def create_layout(self):
        figures = self.create_figure()
        return html.Div([
            html.H1(children="Top {}".format(self.__properties['Top_score_number']), style={'text-align': 'center'}),

            # dcc.Graph(id="top10-graph", figure=self.__figure, animate=False, config={'autosizable': True})

            dcc.Graph(figure=figures[0]),
            dcc.Graph(figure=figures[1]),
            dcc.Graph(figure=figures[2]),
            dcc.Graph(figure=figures[3]),
            dcc.Graph(figure=figures[4]),
            dcc.Graph(figure=figures[5]),
            dcc.Graph(figure=figures[6]),
            dcc.Graph(figure=figures[7]),
            dcc.Graph(figure=figures[8]),
            dcc.Graph(figure=figures[9])
        ])
