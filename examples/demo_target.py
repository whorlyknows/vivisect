"""Demo target for testing Vivisect.

Run this script, then in another terminal: vivisect <PID>

This script:
- Spawns multiple threads
- Opens files
- Listens on a socket
- Makes an HTTP connection
- Has non-trivial environment access
"""

import os
import queue
import socket
import tempfile
import threading
import time


def worker(q: queue.Queue, name: str) -> None:
    """Worker thread that processes items from a queue."""
    while True:
        try:
            item = q.get(timeout=5.0)
            if item is None:
                break
            time.sleep(0.1)  # Simulate work
            q.task_done()
        except queue.Empty:
            continue


def background_listener() -> None:
    """Runs a simple TCP listener on port 9999."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", 9999))
        sock.listen(1)
        sock.settimeout(1.0)
        while True:
            try:
                conn, addr = sock.accept()
                conn.close()
            except TimeoutError:
                continue


def main() -> None:
    print(f"Demo target running with PID: {os.getpid()}")
    print("Open another terminal and run: vivisect", os.getpid())

    # Create some temp files to have open file descriptors
    temp_files = [tempfile.NamedTemporaryFile(delete=False, suffix=f"_{i}.tmp") for i in range(5)]  # noqa: SIM115

    # Start worker threads
    q: queue.Queue = queue.Queue()
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(q, f"Worker-{i}"), name=f"Worker-{i}")
        t.daemon = True
        t.start()
        threads.append(t)

    # Start socket listener
    listener = threading.Thread(target=background_listener, name="Listener", daemon=True)
    listener.start()

    # Feed work items
    try:
        while True:
            for i in range(10):
                q.put(f"task-{i}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nShutting down...")
        # Cleanup temp files
        for f in temp_files:
            f.close()
            os.unlink(f.name)


if __name__ == "__main__":
    main()
