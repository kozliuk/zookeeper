import os
import time
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import as_completed

from kazoo.client import KazooClient

# os.environ["ZOOKEEPER_HOSTS"] = "127.0.0.1:2182"
HOSTS = os.getenv("ZOOKEEPER_HOSTS")
if not HOSTS:
    raise Exception("ZOOKEEPER_HOSTS env variable has not been specified")


def make_listener(idx):
    def listener(ev):
        print(f"{idx}: ZOOKEEPER CLIENT STATE -> {ev}")

    return listener


def _process(idx, file_name):
    time.sleep(1)
    print(f"{idx}: Processing {file_name} file")
    time.sleep(2)
    print(f"{idx}: Processed {file_name} file")
    return idx, file_name


def client(idx, file_name):
    cli = KazooClient(hosts=HOSTS)
    cli.add_listener(make_listener(idx))
    cli.start()
    try:
        lock = cli.Lock(f"/processing/{file_name}")
        lock.acquire()
        return _process(idx, file_name)
    finally:
        cli.stop()


def main():
    print(f"HOSTS: {HOSTS}")
    futures = []
    pool = ThreadPoolExecutor(max_workers=2)
    for idx in range(4):
        f = pool.submit(lambda: client(idx, "`file_to_be_processed.txt`"))
        futures.append(f)
    for future in as_completed(futures):
        idx, file_name = future.result()
        print(f"{idx}: Completed -> {file_name}")


if __name__ == "__main__":
    main()
