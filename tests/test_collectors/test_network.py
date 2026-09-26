import psutil

from vivisect.collectors.network import collect_connections
from vivisect.models import NetworkConnection


def test_collect_connections(own_pid):
    proc = psutil.Process(own_pid)
    conns = collect_connections(proc)

    assert isinstance(conns, list)
    if conns:
        assert isinstance(conns[0], NetworkConnection)
        assert isinstance(conns[0].local_addr, str)
