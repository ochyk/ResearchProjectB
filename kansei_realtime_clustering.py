import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import flask
import plotly.graph_objs as go
import dns.dns_cache as dns
import os, json, glob
import base64
import convert
from dash.dependencies import Input, Output
from datetime import datetime
import plotly.figure_factory as ff

import graph_function_tools as GFT

#GFT.write_X_array_and_command_list_and_command_text()
df, status = GFT.create_df_and_status()
locarr = df.values
flag = 1
now_command_list = []
before_command_list = []

mapbox_access_token = "pk.eyJ1Ijoic3lyIiwiYSI6ImNqcTdnajluMzBkZ3ozeGs0Nmt3cDVzZ2IifQ.XIxuYtXVVoaclR-rNGe4gw"

#画像をエンコード
image_list = [
'picture/cracker.png', #ペイロードあり
'picture/internet_f5_attack.png', #ペイロードなし
'picture/computer_hacker.png' # コマンド入力
]
encoded_image_list = []
for image_filename in image_list:
    encoded_image_list.append(GFT.encode_image(image_filename))

def make_left_top_graph():
    global df
    global locarr
    hover_text = []
    bubble_size = []
    for index, row in df.iterrows():
        hover_text.append(('セッション名: {session}<br>'+
                  'ユーザー名: {username}<br>'+
                  'パスワード: {password}<br>'+
                  'ソースIP: {src_ip}<br>'+
                  '攻撃元の国: {src_country}<br>'+
                  'ターゲットIP: {dst_ip}<br>'+
                  '攻撃先の国: {dst_country}<br>'+
                  'データ: {data}').format(session = row['session'],
                                        username=row['username'],
                                        password=row['password'],
                                        src_ip=row['src_ip'],
                                        src_country=row['src_country'],
                                        dst_ip=row['dst_ip'],
                                        dst_country=row['dst_country'],
                                        data=row['data']))
    df['text'] = hover_text
    figure = {
        'data':[
            go.Scattermapbox(
                mode = 'lines',
                line = dict(
                    width=2,
                    #color="rgb(242, 177, 172)",
                    #color=calc_color(x[0]),
                    color=GFT.calc_color2(x[10])
                ), #rgb(242, 177, 172)
                lat = [x[4], x[6]],
                lon = [x[3], x[5]],
                name = x[0],
                #showlegend=False
            ) for x in locarr
        ] + [
            go.Scattermapbox(
                mode = 'markers',
                marker = dict(size=df['markersize'], color="rgb(255, 0, 0)"),
                lat = df['lat'],
                #lat = x[4],
                lon = df['lon'],
                #lon = x[3],
                text = df['text'],
                #text = x[9],
                name = "destination"#[x[0] for x in locarr],
            ) #for x in locarr
        ] + [
            go.Scattermapbox(
                mode = 'markers',
                marker = dict(size=df['markersize_s'], color="rgb(0, 0, 255)"),
                lat = df['slat'],
                #lat = x[6],
                lon = df['slon'],
                text = df['text'],
                #lon = x[5],
                name = "attacker"#[x[0] for x in locarr],#df['session']
            ) #for x in locarr
        ],
        'layout':
            go.Layout(
                #autosize=True,
                #hovermode='closest',
                mapbox = dict(
                    accesstoken=mapbox_access_token,
                    bearing = 0,
                    center = dict(
                        lat=50,
                        lon=50
                    ),
                    #pitch = 90,
                    zoom=1,
                    style = 'dark',
                ),
                #height=700
            )
    }
    '''
    figure['layout'].update({
        'height': 600
    })
    '''
    return figure

def make_right_top_graph():
    global status
    x = ['ペイロードあり', 'ペイロードなし','コマンド入力']
    y = GFT.calc_number_of_attacker_from_status(status)

    trace0 = go.Bar(
        x=x,
        y=y,
        text=y,
        textposition = 'auto',
        hoverinfo = 'text',
        marker=dict(
            color='rgb(158,202,225)',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5,
            )
        ),
        opacity=0.6
    )

    data = [trace0]
    layout = go.Layout(
        images= [dict(
                source= 'data:image/png;base64,{}'.format(encoded_image_list[0]),
                xref= "paper",
                yref= "paper",
                x= 1/3,
                y= -0.255,
                sizex= 0.2,
                sizey= 0.2,
                xanchor= "right",
                yanchor= "bottom"
              ),dict(
                source= 'data:image/png;base64,{}'.format(encoded_image_list[1]),
                xref="paper",
                yref= "paper",
                x= 2/3,
                y= -0.255,
                sizex= 0.2,
                sizey= 0.2,

                xanchor= "right",
                yanchor= "bottom"
              ),dict(
                source= 'data:image/png;base64,{}'.format(encoded_image_list[2]),
                xref="paper",
                yref= "paper",
                x= 3/3,
                y= -0.255,
                sizex= 0.2,
                sizey= 0.2,

                xanchor= "right",
                yanchor= "bottom"
              )
            ],
        title='Current Attackers',
        autosize=False,
        #height=500, width=700,
    )
    figure = go.Figure(data=data, layout=layout)
    '''
    figure['layout'].update({
        'height': 400
    })
    '''
    return figure

def make_left_bottom_graph():
    global status
    new_command_list = []
    new_command_text_list = []

    #新規入力コマンドのリストを作成
    #新規入力コマンドの付加情報を作成
    for session_name in status:
        user_info = status[session_name]
        if user_info['command'] != []:
            command_str = " ".join(user_info['command'])
            new_command_list.append(command_str)
            src_ip = user_info['src_ip']
            src_info = dns.cdata(src_ip)
            new_command_text_list.append((
            "接続元の国: {country}<br>"+
            "ソースIP: {src_ip}<br>"+
            "コマンド履歴: {command}<br>"
            ).format(
            country = src_info.country.names["ja"],
            src_ip = src_ip,
            command = command_str
            ))

    #print(new_command_text_list)

    X_array, old_command_list, old_command_text_list = GFT.highspeed_create_X_array_and_command_list_and_command_text()
    X_array, command_list = GFT.make_X_array_from_new_command_and_old_command(new_command_list, old_command_list)
    command_text_list = old_command_text_list + new_command_text_list

    label_list = [i for i in range(len(command_list))]
    dendro = ff.create_dendrogram(X_array, orientation='bottom', distfun = GFT.pdist_wrap, linkagefun = lambda x: GFT.linkage_wrap(x), labels = label_list)
    dendro['layout'].update({'width':1200})
    new_command_index_list = []
    new_command_x_list = []

    for i, number in enumerate(dendro['layout']['xaxis']['ticktext']):
        if number > (len(old_command_list) - 1):
            #新規コマンド入力のインデックスを作成
            new_command_index_list.append(number)
            #x軸の座標を作成
            new_command_x_list.append(dendro['layout']['xaxis']['tickvals'][i])
    #dendro_x_list = [i for i in dendro['layout']['xaxis']['tickvals']]
    #print(dendro_x_list)


    trace = go.Scatter(
        x = [i for i in dendro['layout']['xaxis']['tickvals'] if i not in new_command_x_list],
        y = [0 for i in dendro['layout']['xaxis']['ticktext'] if i not in new_command_index_list],
        text = [command_text_list[i] for i in dendro['layout']['xaxis']['ticktext']],
        mode = 'markers',
        hoverinfo = 'text',
        marker = dict(
        size = 2,
        color = 'rgba(0, 0, 0, .8)',
        line = dict(
            width = 2,
            color = 'rgb(0, 0, 0)'
            )
        ),
        showlegend = False
    )
    #text_list = [command_text_list[i] for i in new_command_index_list]

    trace1 = go.Scatter(
        x = [i for i in new_command_x_list],
        y = [0 for i in range(len(new_command_x_list))],
        text = [command_text_list[i] for i in new_command_index_list],
        mode = 'markers',
        hoverinfo = 'text',
        marker = dict(
        size = 10,
        color = 'rgb(255, 0, 0)',
        line = dict(
            width = 2,
            color = 'rgb(255, 0, 0)'
            )
        ),
        showlegend = False
    )

    dendro['layout']['xaxis'].update({'showticklabels':False})
    dendro_data_list = list(dendro['data'])
    dendro_data_list.append(trace)
    dendro_data_list.append(trace1)
    #print(dendro_data_list)
    dendro_new = {}
    dendro_new['data'] = dendro_data_list
    dendro_new['layout'] = dendro['layout']
    '''
    dendro_new['layout'].update({
        'height': 400
    })
    '''
    return dendro_new

def make_left_bottom2_graph():
    df_payload = GFT.load_rinsetsu_df("src/cluster/rinsetsu_matrix_payload.pkl")
    df_never_payload = GFT.load_rinsetsu_df("src/cluster/rinsetsu_matrix_never_payload.pkl")
    command_info = GFT.highspeed_load_command_info()

    lat_list = []
    lon_list = []
    mean_number_of_attack_list = []
    marker_size_list = []
    hover_text_list = []
    lat_list, lon_list, mean_number_of_attack_list, marker_size_list, hover_text_list = GFT.calc_rinsetsu_list(df_payload)

    lat_list_non = []
    lon_list_non = []
    mean_number_of_attack_list_non = []
    marker_size_list_non = []
    hover_text_list_non = []
    lat_list_non, lon_list_non, mean_number_of_attack_list_non, marker_size_list_non, hover_text_list_non = GFT.calc_rinsetsu_list(df_never_payload)

    command_lat_list = command_info['command_lat_list']
    command_lon_list = command_info['command_lon_list']
    command_text_list = command_info['command_text_list']
    command_length = len(command_lat_list)
    command_marker_size_list = [5 for i in range(command_length)]
    for i in range(command_length):
        for j in range(command_length):
            if command_lat_list[i] == command_lat_list[j] and command_lon_list[i] == command_lon_list[j]:
                command_marker_size_list[i] += 1
    figure = {
        'data':[
            go.Scattermapbox(
                mode = 'markers',
                marker = dict(size=marker_size_list, color="rgb(255, 0, 0)"),
                lat = lat_list,
                #lat = x[4],
                lon = lon_list,
                #lon = x[3],
                text = hover_text_list,
                #text = x[9],
                name = "Payload Attackers"#[x[0] for x in locarr],
            )
        ] +
        [
            go.Scattermapbox(
                mode = 'markers',
                marker = dict(size=marker_size_list_non, color="rgb(0, 0, 255)"),
                lat = lat_list_non,
                #lat = x[4],
                lon = lon_list_non,
                #lon = x[3],
                text = hover_text_list_non,
                #text = x[9],
                name = "No Payload Attackers"#[x[0] for x in locarr],
            )
        ] +
        [
            go.Scattermapbox(
                mode = 'markers',
                marker = dict(size=command_marker_size_list, color="rgb(0, 255, 0)"),
                lat = command_lat_list,
                #lat = x[4],
                lon = command_lon_list,
                #lon = x[3],
                text = command_text_list,
                #text = x[9],
                name = "Command Attackers"#[x[0] for x in locarr],
            )
        ],
        'layout':
            go.Layout(
                #autosize=True,
                #hovermode='closest',
                mapbox = dict(
                    accesstoken=mapbox_access_token,
                    bearing = 0,
                    center = dict(
                        lat=50,
                        lon=50
                    ),
                    #pitch = 90,
                    zoom=1,
                    style = 'dark',
                ),
                #height=700
            )
    }
    '''
    figure['layout'].update({
        'height': 600
    })
    '''
    return figure

app = dash.Dash()

server = app.server

app.layout = html.Div([
    html.H1(children='リアルタイムハニーポット分析'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000, # in milliseconds
        n_intervals=0
    ),
    html.Div(id='my-flag'),
    html.Div([
        #攻撃者数棒グラフ
        #html.H2(children='攻撃者数棒グラフ'),
        dcc.Graph(
            id='right-top-graph',
            figure=make_right_top_graph(),
            #style = {"grid-row": "1/2", "grid-column":"2/3"}
            #style = {"width": "50vw"}
        ),
        #リアルタイムマップ
        #html.H2(children='リアルタイムマップ'),
        dcc.Graph(
            id='left-top-graph',
            figure=make_left_top_graph(),
            #style = {"grid-row": "1/2", "grid-column":"1/2"}
            #style = {"height": "600", "width": "100vw"}
        ),
        #デンドログラム
        #html.H2(children='デンドログラム'),
        dcc.Graph(
            id='left-bottom-graph',
            figure=make_left_bottom_graph(),
            #style = {"grid-row": "2/3", "grid-column":"1/2"}
            #style = {"height": "400", "width": "100vw"}
        ),
        #攻撃地域マップ
        #html.H2(children='攻撃地域マップ'),
        dcc.Graph(
            id='left-bottom-graph2',
            figure=make_left_bottom2_graph(),
            #style = {"grid-row": "3/4", "grid-column":"1/2"}
            #style = {"height": "600", "width": "100vw"}
        )
    ], #style={ "display": "grid", "grid-template-rows": "40vw 50vw 40vw", 'grid-template-columns': '80vw 20vw'}
    )
])

@app.callback(
    Output(component_id='left-top-graph', component_property='figure'),
    [Input('interval-component', 'n_intervals')]
)
def realtime_map(input_value):
    global df
    global status
    global locarr
    global dendrogram_flag
    global now_command_list
    global before_command_list

    df, status = GFT.create_df_and_status()
    locarr = df.values

    return make_left_top_graph()

@app.callback(
    Output(component_id='right-top-graph', component_property='figure'),
    [Input('interval-component', 'n_intervals')]
)
def realtime_map_current_attackers(input_value):
    return make_right_top_graph()

@app.callback(
    Output(component_id='my-flag', component_property='children'),
    [Input(component_id='interval-component', component_property='n_intervals')]
)
def update_output_div(input_value):
    global status
    global now_command_list
    global dendrogram_flag
    global before_command_list

    status = GFT.just_read_json()

    new_command_list = []
    for session_name in status:
        user = status[session_name]
        now_command_list.append(user['command'])
    if before_command_list != now_command_list:
        dendrogram_flag = 1
        before_command_list = now_command_list
        now_command_list = []
    else:
        dendrogram_flag = 0
        now_command_list = []
    return 'flag is {}'.format(dendrogram_flag)


@app.callback(
    Output(component_id='left-bottom-graph', component_property='figure'),
    [Input(component_id='my-flag', component_property='children')]
)
def remake_dendrogram(input_value):
    return make_left_bottom_graph()


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(debug=True)
