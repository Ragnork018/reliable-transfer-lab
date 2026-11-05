# Reliable Transfer Lab

A reproducible UDP reliability and ARQ protocol laboratory.

## Complete source

The full project is in [reliable-transfer-lab-source.zip](./reliable-transfer-lab-source.zip). The archive contains the Python package, simulator, UDP sender/receiver, Streamlit dashboard, tests, documentation and GitHub Actions workflow.

Extract and run:

```bash
unzip reliable-transfer-lab-source.zip -d .
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
```

This is an educational simulator and LAN/loopback UDP demo, not a hardened transport protocol or replacement for TCP/QUIC. It has no encryption, authentication or congestion control; do not expose it to the public internet.
