from reliable_lab.core import ChannelConfig, Frame, run_simulation, compare_protocols

def test_crc_detects_corruption():
    f=Frame.create(3,b"hello")
    assert f.valid()
    assert not Frame(f.seq,b"jello",f.checksum).valid()

def test_perfect_channel_delivers_everything():
    for p in ("stop-and-wait","go-back-n","selective-repeat"):
        r=run_simulation(p,messages=20,config=ChannelConfig())
        assert r.delivered_messages == 20
        assert r.reliability == 1.0

def test_lossy_channel_recovers_within_budget():
    for r in compare_protocols(messages=40,payload_bytes=16,window=5,config=ChannelConfig(.08,.05,.01,.02,80,123)):
        assert r.delivered_messages == 40
        assert r.retransmissions >= 0

def test_invalid_parameters_rejected():
    import pytest
    with pytest.raises(ValueError): run_simulation("stop-and-wait",messages=0)
    with pytest.raises(ValueError): ChannelConfig(data_loss=1.0)
