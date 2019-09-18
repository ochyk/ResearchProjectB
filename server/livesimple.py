import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
#from log_management_server import manage_log

import socket
import json as js

#path_w = "status.txt"
path_w = "status.json"

app = dash.Dash()

app.layout = html.Div([
    html.Div(id='my-div'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000, # in milliseconds
        n_intervals=0
    ),
])

def test():
    with open(path_w) as f:
        test = js.loads(f.read())
    return "{}".format(test)

@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input('interval-component', 'n_intervals')]
)
def update_output_div(input_value):
    return "{}".format(test())

if __name__ == '__main__':
    app.run_server()
