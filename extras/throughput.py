import subprocess
import time
import logging
import coloredlogs
from vizualizations import Vizualization

coloredlogs.install(level="INFO")


class Throughput:
    def __init__(self, duration=60, host="10.0.0.2"):
        self.duration = duration
        self.throughput_data = []
        self.host = host

    def run(self):
        start_time = time.time()
        while time.time() - start_time < self.duration:
            self.measure(duration=0.7)

            time.sleep(1)

        Vizualization.visualize_data("Throughput (Mbps)", self.throughput_data)

        return

    def measure(self, duration=0.5):
        process = subprocess.run(
            ["iperf", "-c", self.host, "-t", str(duration), "-f", "k"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5 if duration < 3 else duration + 2,
        )
        output = process.stdout
        if process.returncode == 0:
            self.throughput_data.append(float(output.split()[-2]) / 1000)
        else:
            logging.error(f"Error measuring throughput: {process.stderr}")

        return
