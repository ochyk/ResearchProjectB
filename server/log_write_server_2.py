import socket
from time import sleep
import json as js

#path_w = "status.txt"
path_w = "status.json"
#path = "test.json"

manage_log = {}
count = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # IPアドレスとポートを指定
    s.bind(('127.0.0.1', 50007))
    #s.bind(('10.138.0.2', 50007))
    # 1 接続
    s.listen(1)
    # connection するまで待つ
    while True:
        # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
        conn, addr = s.accept()
        with conn:
            # データを受け取る
            data_sum = b''
            while True:
                data = conn.recv(1024) #1024バイトづつ分割して受信する
                data_sum = data_sum + data #受信した分だけ足していく
                if not data:
                    break
            #print('data : {}, addr: {}'.format(data_sum, addr))

            #バイト列を文字列に変換する
            data_sum = data_sum.decode()

            '''
            #改行文字なしのリストに変換
            s_line = data_sum.split("\n")


            #文字列に変換
            s_line = "".join(s_line)

            #辞書に変換
            s_line = js.loads(s_line)
            '''

            s_line = js.loads(data_sum)

            #新規接続でセッションをキーとして辞書を作成
            if s_line['eventid'] == "cowrie.session.connect":
                manage_log[s_line['session']] = {
                'username':"",
                'password':"",
                'src_ip':s_line['src_ip'],
                'timestamp':s_line['timestamp'],
                'command':[],
                'dst_ip':[],
                'dst_ip_port':[],
                'dst_data_ip':[],
                'dst_data_ip_port':[],
                'dst_data':[]
                }
            #ユーザー名/パスワードを追加
            if s_line['eventid'] == "cowrie.login.success":
                if s_line['session'] in manage_log:
                    manage_log[s_line['session']]['username'] = s_line['username']
                    manage_log[s_line['session']]['password'] = s_line['password']
            #ポートフォワーディングで単に接続するだけの場合
            if s_line['eventid'] == "cowrie.direct-tcpip.request":
                if s_line['session'] in manage_log:
                    manage_log[s_line['session']]['dst_ip'].append(s_line['dst_ip'])
                    manage_log[s_line['session']]['dst_ip_port'].append(s_line['dst_port'])
            #ポートフォワーディングでペイロードなどが付与されている場合
            if s_line['eventid'] == "cowrie.direct-tcpip.data":
                if s_line['session'] in manage_log:
                    manage_log[s_line['session']]['dst_data_ip'].append(s_line['dst_ip'])
                    manage_log[s_line['session']]['dst_data_ip_port'].append(s_line['dst_port'])
                    manage_log[s_line['session']]['dst_data'].append(s_line['data'])
            # コマンド入力履歴追加
            if s_line['eventid'] == "cowrie.command.input":
                if s_line['session'] in manage_log:
                    manage_log[s_line['session']]['command'].append(s_line['input'])
            #セッションを削除
            if s_line['eventid'] == "cowrie.session.closed":
                if s_line['session'] in manage_log:
                    manage_log.pop(s_line['session'])

            with open(path_w, mode='w') as f:
                #f.write(str(manage_log))
                js.dump(manage_log, f)
