import time
from datetime import datetime
import psutil

class Monitor:
    def __init__(self, remote: bool = False, file: str = None, username: str = None,
                 host: str = None, port: int = None, key: str = None, interval: float = 10):
        self.remote = remote
        self.file = file
        self.interval = interval
        if self.remote:
            self.username = username
            self.host = host
            self.port = port
            self.key = key

    #Simple monitoring of system resources CPU and RAM usage
    def monitor_resources(self):
        while True:
            cpu_usage = psutil.cpu_percent(interval=0.5)
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
            now = datetime.now()
            usage_data = f"{str(now)} CPU Usage: {cpu_usage}% | Memory Usage: {memory_usage}%"
            if self.file:
                self.save_to_file(usage_data)
            else:
                print(usage_data)
            time.sleep(self.interval)

    def save_to_file(self, usage_data):
        with open(self.file, 'a') as f:
            f.write(f"{usage_data}\n")