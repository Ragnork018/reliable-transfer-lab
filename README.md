# Reliable Transfer Lab

An experiment-first UDP reliability laboratory. Compare Stop-and-Wait, Go-Back-N, and Selective Repeat under reproducible packet loss, corruption, ACK loss, duplication, and jitter.

## What works

- Frame sequence numbers and CRC32 integrity checks.
- Deterministic, seeded impairment channel.
- Stop-and-Wait ARQ, Go-Back-N, and Selective Repeat simulation.
- Retransmission accounting, delivered bytes, estimated goodput, and packet efficiency.
- JSON benchmark output and comparative CLI.
- Unit tests for integrity and protocol recovery.

This is a simulator and teaching laboratory, not a replacement for TCP or a hardened internet transport protocol. The model is discrete-event/round based; wall-clock throughput is not network throughput.

## Run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'
python -m reliable_lab.cli compare --messages 120 --payload-bytes 1024 --loss 0.08 --ack-loss 0.04 --corruption 0.01 --seed 17
pytest
```

## Examples

```bash
python -m reliable_lab.cli simulate --protocol selective-repeat --messages 100 --loss 0.1 --seed 9
# Terminal 1
python -m reliable_lab.udp_cli receive --host 127.0.0.1 --port 5500 --output /tmp/received.bin
# Terminal 2
python -m reliable_lab.udp_cli send --file ./large-file.bin --host 127.0.0.1 --port 5500 --protocol go-back-n
```

The socket transfer demo supports Stop-and-Wait and Go-Back-N with cumulative ACKs, checksums, bounded retries and atomic output replacement. It is an educational LAN/loopback experiment only: it has no encryption, congestion control, authentication, or defense against malicious peers; do not expose it to the public internet.

Optional dashboard: `pip install -e ".[dashboard]" && streamlit run dashboard.py`.

## Design

`Frame` carries a sequence number, payload, and CRC. `ImpairedChannel` applies reproducible impairment. Each ARQ implementation owns its acknowledgement/retransmission rules. Results include the exact simulation parameters for reproducibility.
