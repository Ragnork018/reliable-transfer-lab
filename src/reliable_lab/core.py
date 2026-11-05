from __future__ import annotations
from dataclasses import dataclass, asdict
import random, zlib
from typing import Literal

Protocol = Literal["stop-and-wait", "go-back-n", "selective-repeat"]

@dataclass(frozen=True)
class Frame:
    seq: int
    payload: bytes
    checksum: int

    @classmethod
    def create(cls, seq: int, payload: bytes) -> "Frame":
        return cls(seq, payload, zlib.crc32(seq.to_bytes(8, "big") + payload))

    def valid(self) -> bool:
        return self.checksum == zlib.crc32(self.seq.to_bytes(8, "big") + self.payload)

@dataclass(frozen=True)
class ChannelConfig:
    data_loss: float = 0.0
    ack_loss: float = 0.0
    corruption: float = 0.0
    duplication: float = 0.0
    max_retries: int = 30
    seed: int = 7

    def __post_init__(self):
        for name in ("data_loss", "ack_loss", "corruption", "duplication"):
            value = getattr(self, name)
            if not 0 <= value < 1:
                raise ValueError(f"{name} must be in [0, 1)")
        if self.max_retries < 1:
            raise ValueError("max_retries must be positive")

class ImpairedChannel:
    def __init__(self, config: ChannelConfig):
        self.config, self.rng = config, random.Random(config.seed)
        self.data_attempts = self.ack_attempts = 0
        self.sequences_attempted: set[int] = set()
        self.data_drops = self.ack_drops = self.corruptions = self.duplicates = 0

    def send_data(self, frame: Frame) -> list[Frame]:
        self.data_attempts += 1
        self.sequences_attempted.add(frame.seq)
        if self.rng.random() < self.config.data_loss:
            self.data_drops += 1
            return []
        delivered = frame
        if self.rng.random() < self.config.corruption:
            self.corruptions += 1
            altered = bytearray(frame.payload or b"\x00")
            altered[0] ^= 0x01
            delivered = Frame(frame.seq, bytes(altered), frame.checksum)
        packets = [delivered]
        if self.rng.random() < self.config.duplication:
            self.duplicates += 1
            packets.append(delivered)
        return packets

    def send_ack(self) -> bool:
        self.ack_attempts += 1
        if self.rng.random() < self.config.ack_loss:
            self.ack_drops += 1
            return False
        return True

@dataclass
class SimulationResult:
    protocol: str
    messages: int
    delivered_messages: int
    payload_bytes: int
    delivered_bytes: int
    data_attempts: int
    ack_attempts: int
    data_drops: int
    ack_drops: int
    corruptions: int
    duplicates: int
    retransmissions: int
    rounds: int
    goodput_per_round: float
    reliability: float
    parameters: dict

    def to_dict(self): return asdict(self)

def run_simulation(protocol: Protocol, messages: int = 100, payload_bytes: int = 256,
                   window: int = 8, config: ChannelConfig | None = None) -> SimulationResult:
    if messages < 1 or payload_bytes < 1 or window < 1:
        raise ValueError("messages, payload_bytes and window must be positive")
    config = config or ChannelConfig()
    channel = ImpairedChannel(config)
    payloads = [bytes([i % 251]) * payload_bytes for i in range(messages)]
    acked: set[int] = set()
    delivered: set[int] = set()
    rounds = 0

    def deliver(frame: Frame, expected: int | None = None):
        if not frame.valid() or frame.seq in delivered:
            return
        if protocol == "go-back-n":
            if frame.seq == len(delivered): delivered.add(frame.seq)
        elif protocol == "stop-and-wait":
            if frame.seq == len(delivered): delivered.add(frame.seq)
        else:
            delivered.add(frame.seq)

    if protocol == "stop-and-wait":
        for seq, payload in enumerate(payloads):
            retries = 0
            while seq not in acked and retries < config.max_retries:
                rounds += 1; frame = Frame.create(seq, payload)
                for received in channel.send_data(frame): deliver(received)
                # Receiver's cumulative ACK is generated only for an in-order frame.
                if seq in delivered and channel.send_ack(): acked.add(seq)
                retries += 1
            if seq not in acked: break
    elif protocol == "go-back-n":
        base = 0; retries = 0
        while base < messages and retries < config.max_retries:
            rounds += 1
            end = min(messages, base + window)
            for seq in range(base, end):
                if seq in acked: continue
                for received in channel.send_data(Frame.create(seq, payloads[seq])):
                    deliver(received)
                # Cumulative ACK represents the next expected sequence number.
                if len(delivered) > base and channel.send_ack():
                    highest_contiguous = len(delivered) - 1
                    for n in range(base, highest_contiguous + 1): acked.add(n)
            # If the first outstanding sequence got through, advance its base.
            while base in acked: base += 1
            retries += 1
    elif protocol == "selective-repeat":
        retries_by_seq = [0] * messages
        while len(acked) < messages and rounds < config.max_retries * messages:
            rounds += 1
            active = [n for n in range(messages) if n not in acked][:window]
            if not active: break
            for seq in active:
                for received in channel.send_data(Frame.create(seq, payloads[seq])):
                    deliver(received)
                if seq in delivered and channel.send_ack(): acked.add(seq)
                retries_by_seq[seq] += 1
        
    delivered_messages = len(delivered)
    return SimulationResult(
        protocol=protocol, messages=messages, delivered_messages=delivered_messages,
        payload_bytes=payload_bytes, delivered_bytes=delivered_messages * payload_bytes,
        data_attempts=channel.data_attempts, ack_attempts=channel.ack_attempts,
        data_drops=channel.data_drops, ack_drops=channel.ack_drops,
        corruptions=channel.corruptions, duplicates=channel.duplicates,
        retransmissions=max(0, channel.data_attempts - len(channel.sequences_attempted)), rounds=rounds,
        goodput_per_round=(delivered_messages * payload_bytes / rounds) if rounds else 0.0,
        reliability=delivered_messages / messages,
        parameters={"window": window, **asdict(config)})

def compare_protocols(**kwargs) -> list[SimulationResult]:
    config = kwargs.pop("config", None) or ChannelConfig()
    results = []
    # Same seed per protocol keeps experiments reproducible; algorithms consume random draws differently.
    for protocol in ("stop-and-wait", "go-back-n", "selective-repeat"):
        results.append(run_simulation(protocol, config=config, **kwargs))
    return results
