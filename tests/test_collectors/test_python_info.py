import psutil

from vivisect.collectors.python_info import collect_python_info
from vivisect.models import PythonInfo


def test_collect_python_info(own_pid):
    proc = psutil.Process(own_pid)
    info = collect_python_info(proc)

    assert info is not None
    assert isinstance(info, PythonInfo)
