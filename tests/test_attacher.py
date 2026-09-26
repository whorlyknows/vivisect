import pytest

from vivisect.attacher import ProcessNotFoundError, resolve_pid


def test_resolve_pid_valid(own_pid):
    pid = resolve_pid(str(own_pid))
    assert pid == own_pid


def test_resolve_pid_invalid_string():
    with pytest.raises(ProcessNotFoundError):
        resolve_pid("not_a_number")


def test_resolve_pid_not_found():
    # 999999 is likely not a PID
    with pytest.raises(ProcessNotFoundError):
        resolve_pid("999999")


def test_find_by_name(own_pid):
    # Search for "pytest" or "python"
    pid = resolve_pid("python", by_name=True)
    assert isinstance(pid, int)


def test_find_by_name_not_found():
    with pytest.raises(ProcessNotFoundError):
        resolve_pid("this_process_should_never_exist_12345", by_name=True)
