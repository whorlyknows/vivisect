"""Shared test fixtures."""

import os
import subprocess
import sys
import time

import pytest


@pytest.fixture
def demo_process():
    """Spawn a known Python process for testing and clean up after."""
    # Start a simple Python process that stays alive
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(0.5)  # Let it start

    yield proc

    proc.terminate()
    proc.wait(timeout=5)


@pytest.fixture
def own_pid():
    """Return the PID of the current test process."""
    return os.getpid()
