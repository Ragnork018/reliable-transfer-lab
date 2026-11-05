# Reliable Transfer Lab

The complete project source is in [reliable-transfer-lab-source.zip](./reliable-transfer-lab-source.zip). It contains the Python package, simulator, UDP sender/receiver, Streamlit dashboard, tests, documentation and CI workflow.

```bash
unzip reliable-transfer-lab-source.zip -d .
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
```

This is an educational simulator and LAN/loopback UDP demo, not a hardened transport protocol or replacement for TCP/QUIC. It has no encryption, authentication or congestion control. Do not expose it to the public internet.
