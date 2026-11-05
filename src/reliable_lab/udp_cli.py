import argparse,json
from .udp import send_file,receive_file

def main():
 p=argparse.ArgumentParser(description='Educational reliable UDP file transfer');s=p.add_subparsers(dest='cmd',required=True)
 r=s.add_parser('receive');r.add_argument('--host',default='127.0.0.1');r.add_argument('--port',type=int,required=True);r.add_argument('--output',required=True)
 t=s.add_parser(\'send');t.add_argument(\'--file',required=True);t.add_argument('--host',default='127.0.0.1');t.add_argument('--port',type=int,required=True);t.add_argument('--protocol',choices=['stop-and-wait','go-back-n'],default='go-back-n');t.add_argument('--window',type=int,default=8);t.add_argument('--chunk-size',type=int,default=1024)
 a=p.parse_args()
 if a.cmd=='receive':print(json.dumps({'bytes_received':receive_file(a.host,a.port,a.output)}))
 else:print(json.dumps(send_file(a.file,a.host,a.port,a.protocol,a.window,a.chunk_size)))
if __name__='__main__':main()
