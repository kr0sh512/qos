import subprocess
import re
from datetime import datetime
import matplotlib.pyplot as plt
import logging
import coloredlogs
import time
import threading

from latency import Latency
from packet_loss import PacketLoss
from throughput import Throughput


coloredlogs.install(level="INFO")

"""
Реализация многопоточности, функции для работы с tshark и постройки нужной визуализации
"""


class Extra:
    def __init__(self, duration=60, host="10.0.0.2"):
        self.duration = duration
        self.retransmissions_timestamps = []
        self.retransmissions_count = []
        self.latency = Latency(duration=self.duration, host=host)
        self.packet_loss = PacketLoss(duration=self.duration, host=host)
        self.throughput = Throughput(duration=self.duration, host=host)

    def run(self, with_traffic_capture=False):
        thread_latency = threading.Thread(target=self.latency.run)
        thread_latency.start()

        thread_packet_loss = threading.Thread(target=self.packet_loss.run)
        thread_packet_loss.start()

        thread_throughput = threading.Thread(target=self.throughput.run)
        thread_throughput.start()

        if with_traffic_capture:
            self.capture_traffic(duration=self.duration)

        while (
            thread_latency.is_alive()
            or thread_packet_loss.is_alive()
            or thread_throughput.is_alive()
        ):
            time.sleep(1)

        return

    def capture_traffic(self, duration=10):

        command = [
            "tshark",
            "-a",
            f"duration:{duration}",
            "-Y",
            "tcp.analysis.retransmission",
            "-T",
            "fields",
            "-e",
            "frame.time",
        ]

        process = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if process.returncode != 0:
            logging.error(f"Error capturing traffic: {process.stderr.decode()}")
            return

        output = process.stdout.decode()

        self.analyze_retransmissions(output)
        self.plot_retransmissions()

        return

    def analyze_retransmissions(self, output):
        self.retransmissions_timestamps = []
        self.retransmissions_count = []

        for line in output.split("\n"):
            timestamp = re.search(r"\d{2}:\d{2}:\d{2}\.\d{6}", line)
            if timestamp:
                self.retransmissions_count.append(
                    datetime.strptime(timestamp.group(), "%H:%M:%S.%f")
                )
                self.retransmissions_timestamps.append(len(self.retransmissions_count))

        return

    def plot_retransmissions(self):
        plt.figure(figsize=(10, 6))
        plt.plot(
            self.retransmissions_timestamps,
            self.retransmissions_count,
            marker="o",
            label="Retransmissions",
        )
        plt.xlabel("Time")
        plt.ylabel("Retransmissions")
        plt.title("TCP Retransmissions Over Time")
        plt.legend()
        plt.grid()
        plt.show()
        plt.savefig("output/retransmissions_plot.png")
        logging.info(f"Plot saved to output/retransmissions_plot.png")

        return


if __name__ == "__main__":
    extra = Extra(duration=60, host="10.0.0.2")
    extra.run(with_traffic_capture=True)
