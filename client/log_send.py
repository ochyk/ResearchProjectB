#-*- coding: utf-8 -*-
import time
import os
import sys
from stat import *
import socket

def init(filename):
    file = open(filename,'r')
    return file

def tail_f(file, usec):
    msec = 1.5
    while 1:
        #fpos = file.tell()
        line = file.readline()
        time.sleep(msec)
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

    #filename = "/Users/ochikei/prokenB_kohan/src/cowrie.json"
    filename = "/Users/ochikei/honeypot/logdata5/cowrie.json"
    file = init(filename)
    tail_f(file, 500)
