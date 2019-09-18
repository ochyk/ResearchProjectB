import geoip2.database
import socket, os, time
from glob import glob
import pickle

def main():
    m = cdata('ya.ru')
    print(m)

def cdata(domain):
    abspath = os.path.dirname(os.path.abspath(__file__))
    with open(f'{abspath}/dns.pickle', 'rb') as f:
        d = pickle.load(f)
    if domain not in d.keys():
        reader = geoip2.database.Reader(abspath + "/../database/geodb/GeoLite2-City.mmdb")
        x = socket.gethostbyname(domain)
        rt = reader.city(x)
        print(domain, rt.location)
        d[domain] = rt
        with open(f'{abspath}/dns.pickle', 'wb') as f:
            pickle.dump(d, f)
        time.sleep(2)
    else:
        rt = d[domain]
        # print(domain, "exists")
    return rt

if __name__ == '__main__':
    main()
