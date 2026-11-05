# Deployment and acceptance checklist

Build with `docker build -t reliable-transfer-lab .` and expose Streamlit on port 8501. The dashboard is a simulator and experiment console. Run the sender/receiver only on loopback or a trusted isolated LAN.

Before any network exposture: design authenticated encryption, congestion control, abuse controls, robust framing, resource limits and protocol review. This research protocol is not a safe TCP/QUIC replacement.
