import psutil

from vivisect.collectors.threads import collect_threads


def test_collect_threads(own_pid):
    proc = psutil.Process(own_pid)
    threads = collect_threads(proc)

    assert isinstance(threads, list)
    assert len(threads) >= 1
    assert isinstance(threads[0].id, int)
