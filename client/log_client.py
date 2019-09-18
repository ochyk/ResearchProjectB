#-*- coding: utf-8 -*-
import time
import os
import sys
from stat import *
import socket

def usage():
    print("Usage: # python %s filename" % argv[0])
    quit()


def init(filename):
    file = open(filename,'r')

    #ファイル末尾へ移動
    st_results = os.stat(filename)
    st_size = st_results[ST_SIZE]
    file.seek(st_size)

    return file

def tail_f(file, usec):
    msec = usec / 1000
    while 1:
        fpos = file.tell()
        line = file.readline()
        if not line:
            time.sleep(msec)
            file.seek(fpos)
        else:
            #print line,
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # サーバを指定
                s.connect(('127.0.0.1', 50007))
                # サーバにメッセージを送る encode()で文字列をバイト列に変換
                s.sendall(line.encode())
                # ネットワークのバッファサイズは1024。サーバからの文字列を取得する
                #data = s.recv(1024)
                #
                #print(repr(data))
    # 未到達
    file.close()
    pass

if __name__ == '__main__':
    argv  = sys.argv
    argc  = len(argv)
    if( argc != 2 ):
        usage()

    filename = argv[1]
    file = init(filename)
    tail_f(file, 500)
