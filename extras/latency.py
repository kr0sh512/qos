import subprocess
import time
import logging
import coloredlogs
from vizualizations import Vizualization

coloredlogs.install(level="INFO")


class Latency:
    def __init__(self, duration=60, host="10.0.0.2"):
        self.duration = duration
        self.latency_data = []
        self.host = host

    def run(self):
        start_time = time.time()
        while time.time() - start_time < self.duration:
            self.measure(packet_number=4)

            time.sleep(1)

        Vizualization.visualize_data("Latency (ms)", self.latency_data)

        return

    def measure(self, packet_number=4):
        process = subprocess.run(
            ["ping", "-c", str(packet_number), self.host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5 if packet_number < 3 else packet_number + 2,
        )
        output = process.stdout.decode()

        if process.returncode == 0:
            latency_lines = [line for line in output.split("\n") if "time=" in line]
            latencies = [
                float(line.split("time=")[1].split(" ")[0]) for line in latency_lines
            ]
            self.latency_data.extend(latencies)
        else:
            logging.error(f"Error measuring latency and packet loss: {process.stderr}")

        return
