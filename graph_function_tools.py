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

import plotly.plotly as py
import plotly.figure_factory as ff
import scipy
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import dendrogram
from sklearn.feature_extraction.text import CountVectorizer

def create_df_and_status():
    with open('server/status.json', 'r') as f:
        data = json.load(f)
    return convert.create_df(data), data

def create_df():
    with open('server/status.json', 'r') as f:
        data = json.load(f)
    return convert.create_df(data)

def just_read_json():
    with open('server/status.json', 'r') as f:
        data = json.load(f)
    return data

def encode_image(image_filename):
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())
    return encoded_image.decode()

def calc_color(str):
    session = int(str, 16)
    i = int(session * (16777215 / 281474976710655) * 0.8)
    c = "#" + format(i, 'x')
    c = (int(c[1:3],16),int(c[3:5],16),int(c[5:7],16))
    return f'rgb({c[0]}, {c[1]}, {c[2]})'

def calc_color2(flag):
    if flag is 0:
        color = 'rgb(0, 255, 0)'
    elif flag is 1:
        color = 'rgb(0, 0, 255)'
    elif flag is 2:
        color = 'rgb(255, 0, 0)'
    else:
        color = 'rgb(255, 255, 255)'
    return color

def calc_number_of_attacker():
    data = just_read_json()
    number_of_sessions = len(data)
    number_of_payload = number_of_no_payload = number_of_both_payload = number_of_command = 0
    for session in data:
        attacker = data[session]
        if attacker['command'] != []:
            number_of_command += 1
        elif attacker['dst_data'] != [] and attacker['dst_ip'] != []:
            number_of_both_payload += 1
        elif attacker['dst_data'] != []:
            number_of_payload += 1
        elif attacker['dst_ip'] != []:
            number_of_no_payload += 1
    number_of_attacker = [number_of_payload, number_of_no_payload, number_of_both_payload, number_of_command]
    return number_of_attacker

def calc_number_of_attacker_from_status(status):
    data = just_read_json()
    number_of_sessions = len(data)
    number_of_payload = number_of_no_payload = number_of_both_payload = number_of_command = 0
    for session in data:
        attacker = data[session]
        if attacker['command'] != []:
            number_of_command += 1
        elif attacker['dst_data'] != []:
            number_of_payload += 1
        elif attacker['dst_ip'] != []:
            number_of_no_payload += 1
    number_of_attacker = [number_of_payload, number_of_no_payload, number_of_command]
    return number_of_attacker

'''
## デンドログラム作成用
def create_X_array_and_command_list():
    path_r = "src/cluster/train/logdata2-5_command_hist.json"
    with open(path_r) as fp:
        command_history = json.loads(fp.read())

    command_list = []
    for key in command_history:
        command_str = " ".join(command_history[key]["command"])
        if command_str not in command_list:
            command_list.append(command_str)
    #外れ値の除去
    command_list.pop(19)
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(command_list)
    X_array = X.toarray()
    return X_array, command_list
'''

'''
def create_X_array_and_command_list_and_command_text():
    path_r = "src/cluster/train/logdata2-5_command_hist.json"
    with open(path_r) as fp:
        command_history = json.loads(fp.read())

    command_list = []
    command_text_list = []
    for key in command_history:
        command_str = " ".join(command_history[key]["command"])
        if command_str not in command_list:
            command_list.append(command_str)
            src_ip = command_history[key]["src_ip"]
            src_info = dns.cdata(src_ip)
            command_text_list.append((
            "接続元の国: {country}<br>"+
            "ソースIP: {src_ip}<br>"+
            "コマンド履歴: {command}<br>"
            ).format(
            country = src_info.country.names["ja"],
            src_ip = src_ip,
            command = command_str
            ))
    #外れ値の除去
    command_list.pop(19)
    command_text_list.pop(19)
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(command_list)
    X_array = X.toarray()
    return X_array, command_list, command_text_list
'''

def highspeed_create_X_array_and_command_list_and_command_text():
    path_r = "src/cluster/train/logdata2-5_command_hist_highspeed.json"
    with open(path_r) as fp:
        command_info = json.loads(fp.read())
    X_array = np.array(command_info['X_array'])
    command_list = command_info['command_list']
    command_text_list = command_info['command_text_list']
    return X_array, command_list, command_text_list

def highspeed_load_command_info():
    path_r = "src/cluster/train/logdata2-5_command_hist_highspeed.json"
    with open(path_r) as fp:
        command_info = json.loads(fp.read())
    return command_info

'''
def write_X_array_and_command_list_and_command_text():
    path_r = "src/cluster/train/logdata2-5_command_hist.json"
    path_w = "src/cluster/train/logdata2-5_command_hist_highspeed.json"
    with open(path_r) as fp:
        command_history = json.loads(fp.read())
    count = 0
    command_list = []
    command_text_list = []
    command_lon_list = []
    command_lat_list = []
    for key in command_history:
        command_str = " ".join(command_history[key]["command"])
        if command_str not in command_list:
            src_ip = command_history[key]["src_ip"]
            count += 1
            src_info = dns.cdata(src_ip)
            command_list.append(command_str)
            command_text_list.append((
            "接続元の国: {country}<br>"+
            "ソースIP: {src_ip}<br>"+
            "コマンド履歴: {command}<br>"
            ).format(
            country = src_info.country.names["ja"],
            src_ip = src_ip,
            command = command_str
            ))
            command_lon_list.append(src_info.location.longitude)
            command_lat_list.append(src_info.location.latitude)
    for i, j in enumerate([2, 3, 4, 5, 14, 19, 62 ,63]):
        command_list.pop(j - i)
        command_text_list.pop(j - i)
        command_lon_list.pop(j - i)
        command_lat_list.pop(j - i)
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(command_list)
    X_array = X.toarray()
    D_array = pdist(X_array, metric = 'cosine')
    command_info_dict = {
    'X_array':X_array.tolist(),
    'D_array': D_array.tolist(),
    'command_list':command_list,
    'command_text_list': command_text_list,
    'command_lon_list': command_lon_list,
    'command_lat_list': command_lat_list
    }
    with open(path_w, mode='w') as f:
        #f.write(str(manage_log))
        json.dump(command_info_dict, f)
'''

def pdist_wrap(X):
    return pdist(X, metric = 'cosine')

def linkage_wrap(X):
    return linkage(X, method = 'ward', metric = 'cosine')

def make_X_array_from_new_command_and_old_command(new_command_list, old_command_list):
    command_list = old_command_list + new_command_list
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(command_list)
    X_array = X.toarray()
    return X_array, command_list

## 隣接行列作成用
def load_rinsetsu_df(rinsetsu_matrix_location):
    mat=pd.read_pickle(rinsetsu_matrix_location)
    rinsetsu_matrix=pd.Series(mat).unstack()
    return rinsetsu_matrix.T.describe()

def calc_rinsetsu_list(df_payload):
    lat_list = []
    lon_list = []
    mean_number_of_attack_list = []
    marker_size_list = []
    hover_text_list = []

    for attacker_src_ip in df_payload:
        attacker_src_info = dns.cdata(attacker_src_ip)
        lat_list.append(attacker_src_info.location.latitude)
        lon_list.append(attacker_src_info.location.longitude)
        country_name = attacker_src_info.country.names['ja']
        mean_number_of_attack = df_payload[attacker_src_ip]['mean']
        mean_number_of_attack_list.append(mean_number_of_attack)
        hover_text_list.append("国名: {}<br>ソースip: {}<br>平均攻撃回数: {}".format(country_name, attacker_src_ip, mean_number_of_attack))
        if mean_number_of_attack > 10000:
            marker_size_list.append(100)
        elif mean_number_of_attack > 1000:
            marker_size_list.append(50)
        elif mean_number_of_attack > 100:
            marker_size_list.append(20)
        else:
            marker_size_list.append(5)

    return lat_list, lon_list, mean_number_of_attack_list, marker_size_list, hover_text_list
