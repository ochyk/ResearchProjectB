import json
import pandas as pd
import time
import geoip2.database
import socket
import dns.dns_cache as dns

def create_df(status):
    rt = [['session', 'src_ip', 'dst_ip', 'lon', 'lat', 'slon', 'slat', 'username', 'password', 'data', 'flag', 'markersize', 'markersize_s', 'src_country', 'dst_country']]
    #rt = [['session', 'src_ip', 'dst_ip', 'lon', 'lat', 'slon', 'slat']]
    count_ip = {}
    for session_name in status.keys():
        js = status[session_name]
        if 'src_ip' in js.keys():
            srcip = js['src_ip']
            #キーカウント
            if srcip in count_ip.keys():
                count_ip[srcip] += 1
            else:
                count_ip[srcip] = 5

            try:
                xxx = dns.cdata(srcip)
            except:
                continue
            markersize_s = count_ip[srcip]
            slon, slat = [xxx.location.longitude, xxx.location.latitude]
            src_country = xxx.country.names['ja']
            if 'dst_ip' in js.keys():
                for x in js['dst_ip']:
                    try:
                        xx = dns.cdata(x)
                    except:
                        continue
                    try:
                        username = js['username']
                        password = js['password']
                    except:
                        continue
                    flag = 1
                    data = 'null'
                    if x in count_ip.keys():
                        count_ip[x] += 1
                    else:
                        count_ip[x] = 5
                    markersize = count_ip[x]
                    lon, lat = [xx.location.longitude, xx.location.latitude]
                    dst_country = xx.country.names['ja']
                    #rt.append(['3a30f3dbed1a', srcip, x, lon, lat, slon, slat])
                    rt.append([session_name, srcip, x, lon, lat, slon, slat, username, password, data, flag, markersize, markersize_s, src_country, dst_country])
                for x in js['dst_data_ip']:
                    try:
                        xx = dns.cdata(x)
                    except:
                        continue
                    try:
                        username = js['username']
                        password = js['password']
                    except:
                        continue
                    try:
                        #data = str(js['dst_data'])
                        data = "payload"
                    except:
                        continue
                    flag = 2
                    if x in count_ip.keys():
                        count_ip[x] += 1
                    else:
                        count_ip[x] = 5
                    markersize = count_ip[x]
                    lon, lat = [xx.location.longitude, xx.location.latitude]
                    dst_country = xx.country.names['ja']
                    #rt.append(['10893fd229122', srcip, x, lon, lat, slon, slat])
                    rt.append([session_name, srcip, x, lon, lat, slon, slat, username, password, data, flag, markersize, markersize_s, src_country, dst_country])
                if js['command'] != []:
                    try:
                        data = " ".join(js['command'])
                    except:
                        data = 'null'
                        continue
                    try:
                        username = js['username']
                        password = js['password']
                    except:
                        continue
                    flag = 0
                    lon, lat = [140.0, 36.0]
                    dst_country = "日本"
                    dstip = '13.114.26.81'
                    x = dstip
                    '''
                    if x in count_ip.keys():
                        count_ip[x] += 1
                    else:
                        count_ip[x] = 1
                    '''
                    count_ip[x] = 5
                    markersize = count_ip[x]
                    rt.append([session_name, srcip, dstip, lon, lat, slon, slat, username, password, data, flag, markersize, markersize_s, src_country, dst_country])
            else:
                flag = 0
                lon, lat = [140.0, 36.0]
                dstip = '13.114.26.81'
                dst_country = '日本'
                data = 'null'
                #count_ip[dstip] += 1
                count_ip[dstip] = 1
                markersize = count_ip[dstip]
                try:
                    username = js['username']
                    password = js['password']
                except:
                    continue
                #rt.append(['3a30f3dbed1a', srcip, dstip, lon, lat, slon, slat])
                rt.append([session_name, srcip, dstip, lon, lat, slon, slat, username, password, data, flag, markersize, markersize_s, src_country, dst_country])
    # print(rt, len(rt))
    #print(rt)
    #print(pd.DataFrame(rt[1:], columns=rt[0]))
    return pd.DataFrame(rt[1:], columns=rt[0])


def main():
    path = 'testdata/cowrie.json'
    with open(path, "r") as f:
        js = f.read().split('\n')
    data = []
    for x in js[:100]:
        data.append(json.loads(x) if x != '' else {})
    create_df_old(data).to_csv('testdata/cowrie_test.csv', index=None)

def create_df_old(data):
    rt = [['session', 'src_ip', 'dst_ip', 'lon', 'lat', 'slon', 'slat']]
    for js in data:
        if 'src_ip' in js.keys():
            srcip = js['src_ip']
            try:
                xxx = dns.cdata(srcip)
            except:
                continue
            slon, slat = [xxx.location.longitude, xxx.location.latitude]
            if 'dst_ip' in js.keys():
                dstip = js['dst_ip']
                try:
                    xx = dns.cdata(dstip)
                except:
                    continue
                lon, lat = [xx.location.longitude, xx.location.latitude]
            else:
                lon, lat = [140.0, 36.0]
                dstip = '486.486.486.486'
            rt.append([js['session'], srcip, dstip, lon, lat, slon, slat])
    # print(rt, len(rt))
    return pd.DataFrame(rt[1:], columns=rt[0])



if __name__ == '__main__':
    main()
