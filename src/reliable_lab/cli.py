import argparse, json
from .core import ChannelConfig, run_simulation, compare_protocols

def main():
    p = argparse.ArgumentParser(description="Reproducible ARQ protocol simulator")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("simulate", "compare"):
        q=sub.add_parser(name); q.add_argument("--protocol", choices=["stop-and-wait","go-back-n","selective-repeat"], default="selective-repeat")
        q.add_argument("--messages", type=int, default=100); q.add_argument("--payload-bytes", type=int, default=512)
        q.add_argument("--window", type=int, default=8); q.add_argument("--loss", type=float, default=0.04)
        q.add_argument("--ack-loss", type=float, default=0.02); q.add_argument("--corruption", type=float, default=0.005)
        q.add_argument("--duplication", type=float, default=0.01); q.add_argument("--max-retries", type=int, default=30)
        q.add_argument("--seed", type=int, default=7)
    a=p.parse_args(); cfg=ChannelConfig(a.loss,a.ack_loss,a.corruption,a.duplication,a.max_retries,a.seed)
    args=dict(messages=a.messages,payload_bytes=a.payload_bytes,window=a.window,config=cfg)
    output=compare_protocols(**args) if a.command=="compare" else [run_simulation(a.protocol,**args)]
    print(json.dumps([x.to_dict() for x in output],indent=2))
if __name__ == "__main__": main()
