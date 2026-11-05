"""Small, educational reliable file transfer over UDP (loopback/LAN experiments only).

Stop-and-Wait and Go-Back-N use cumulative ACKs. Not encrypted, congestion controlled,
or suitable for public internet deployment. Use TCP/QUIC for real applications.
"""
from __future__ import annotations
import os,socket,struct,zlib,tempfile,time
from pathlib import Path
MAGIC=b'RTL1';DATA=struct.Struct('!4sIIII');ACK=struct.Struct('!4sI');MAX_CHUNK=60_000
class TransferError(RuntimeError):pass

def _packet(seq,total,payload):return DATA.pack(MAGIC,seq,total,len(payload),zlib.crc32(payload))+payload

def receive_file(bind_host:str,port:int,destination:str,timeout:float=30.0,final_ack_linger:float=1.0)->int:
    if timeout<=0 or final_ack_linger<0: raise ValueError('timeout must be positive and final_ack_linger non-negative')
    dest=Path(destination);dest.parent.mkdir(parents=True,exist_ok=True);expected=0;total=None;bytes_written=0;peer_locked=None
    fd,tmp=tempfile.mkstemp(prefix=dest.name+'.',suffix='.part',dir=dest.parent)
    try:
      with os.fdopen(fd,'wb') as out, socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        sock.bind((bind_host,port));sock.settimeout(timeout)
        complete_at=None
        while total is None or expected<total or (complete_at is not None and time.monotonic()-complete_at<final_ack_linger):
          if complete_at is not None:
            sock.settimeout(max(.01,final_ack_linger-(time.monotonic()-complete_at)))
          try:data,peer=sock.recvfrom(65_535)
          except socket.timeout as e:
            if complete_at is not None: break
            raise TransferError(f'Timed out waiting for packet {expected}') from e
          if peer_locked is None: peer_locked=peer
          if peer != peer_locked: continue
          if len(data)<DATA.size:continue
          magic,seq,t,n,crc=DATA.unpack(data[:DATA.size]);payload=data[DATA.size:]
          if magic!=MAGIC or len(payload)!=n or zlib.crc32(payload)!=crc:continue
          if total is None:total=t
          if t!=total or seq>=total:continue
          if seq==expected and expected<total:
            out.write(payload);bytes_written+=len(payload);expected+=1
            if expected==total: complete_at=time.monotonic()
          # Re-ACK duplicates (including the final packet during the linger period).
          sock.sendto(ACK.pack(MAGIC,expected),peer)
        out.flush();os.fsync(out.fileno())
      os.replace(tmp,dest);return bytes_written
    except Exception:
      try:os.unlink(tmp)
      except OSError:pass
      raise

def send_file(source:str,host:str,port:int,protocol:str='go-back-n',window:int=8,
              chunk_size:int=1024,timeout:float=.25,max_retries:int=30)->dict:
    path=Path(source);data=path.read_bytes()
    if not data:raise ValueError('Empty files are not supported')
    if timeout<=0: raise ValueError('timeout must be positive')
    if not 1<=chunk_size<=MAX_CHUNK:raise ValueError(f'chunk_size must be between 1 and {MAX_CHUNK}')
    if protocol not in {'stop-and-wait','go-back-n'}:raise ValueError('UDP file transfer supports stop-and-wait or go-back-n')
    if protocol=='stop-and-wait':window=1
    if window<1 or max_retries<1:raise ValueError('window and max_retries must be positive')
    chunks=[data[i:i+chunk_size] for i in range(0,len(data),chunk_size)];total=len(chunks)
    attempts=0;retries=0;base=0;next_seq=0
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
      sock.settimeout(timeout)
      while base<total:
        while next_seq<total and next_seq<base+window:
          sock.sendto(_packet(next_seq,total,chunks[next_seq]),(host,port));attempts+=1;next_seq+=1
        try:
          ackdata,_=sock.recvfrom(ACK.size+8)
          if len(ackdata)!=ACK.size:continue
          magic,next_expected=ACK.unpack(ackdata)
          if magic!=MAGIC or next_expected>total:continue
          if next_expected>base:
            base=next_expected;retries=0
        except socket.timeout:
          retries+=1
          if retries>max_retries:raise TransferError(f'Exceeded {max_retries} retransmission rounds at packet {base}')
          # GBN retransmits the whole outstanding window; Stop-and-Wait has one packet.
          for seq in range(base,min(total,base+window)):
            sock.sendto(_packet(seq,total,chunks[seq]),(host,port));attempts+=1
    return {'file':path.name,'bytes':len(data),'packets':total,'datagrams_sent':attempts,'retransmissions':attempts-total,'protocol':protocol}
