import socket,threading,time
from pathlib import Path
from reliable_lab.udp import send_file,receive_file

def free_port():
 s=socket.socket();s.bind(('127.0.0.1',0));p=s.getsockname()[1];s.close();return p

def test_udp_gbn_file_roundtrip(tmp_path):
 source=tmp_path/'source.bin';dest=tmp_path/'copy.bin';payload=bytes(range(256))*160;source.write_bytes(payload);port=free_port();received=[]
 def receiver():received.append(receive_file('127.0.0.1',port,str(dest),timeout=5))
 th=threading.Thread(target=receiver,daemon=True);th.start();time.sleep(.08)
 result=send_file(str(source),'127.0.0.1',port,'go-back-n',window=6,chunk_size=1200,timeout=.1)
 th.join(5);assert not th.is_alive();assert dest.read_bytes()==payload;assert result['bytes']==len(payload);assert received==[len(payload)]
