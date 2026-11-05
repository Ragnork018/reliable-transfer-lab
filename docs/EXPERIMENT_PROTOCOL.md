# Reproducible experiment protocol

1. Fix the random seed and record payload size, packet size, window size, timeout, simulated loss/corruption/reordering rates and retry limits.
2. Run a clean baseline, then sweep one impairment at a time. Repeat each cell at least 30 times and report median, p95, throughput, retransmissions, completion rate and CPU time.
3. Compare Stop-and-Wait, Go-Back-N and Selective Repeat under the same impairment trace. Publish the raw run metadata with each benchmark.
4. Validate checksums and byte-for-byte output after every successful transfer.
5. The UDP demo is for loopback/trusted LAN experiments only. It does not implement encryption, authentication, congestion control or a hardened production transport. Never expose it to untrusted networks.
