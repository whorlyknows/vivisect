import psutil

from vivisect.collectors.filesystem import collect_open_files
from vivisect.models import FileDescriptor


def test_collect_open_files(own_pid):
    proc = psutil.Process(own_pid)
    files = collect_open_files(proc)

    assert isinstance(files, list)
    if files:
        assert isinstance(files[0], FileDescriptor)
        assert isinstance(files[0].path, str)
