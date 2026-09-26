import psutil

from vivisect.collectors.process import collect_process_info


def test_collect_process_info(own_pid):
    proc = psutil.Process(own_pid)
    info = collect_process_info(proc)

    assert info["cpu_percent"] >= 0
    assert info["memory_rss"] > 0
    assert info["name"] != ""
    assert "status" in info
    assert "memory_vms" in info
    assert "num_threads" in info
