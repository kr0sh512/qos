from main import QoSMonitor
import subprocess
import re
from datetime import datetime
import threading
import matplotlib.pyplot as plt
import os

"""
Реализация многопоточности, функции для работы с tcpdump и постройки нужной визуализации
"""


class Extra:
    import matplotlib.pyplot as plt

    def capture_traffic(interface="eth0", duration=10, output_file="traffic.pcap"):
        """
        Capture network traffic using tcpdump.
        """
        try:
            subprocess.run(
                [
                    "tcpdump",
                    "-i",
                    interface,
                    "-w",
                    output_file,
                    "-G",
                    str(duration),
                    "-W",
                    "1",
                ],
                check=True,
            )
            print(f"Traffic captured in {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error capturing traffic: {e}")

    def analyze_retransmissions(pcap_file="traffic.pcap"):
        """
        Analyze the captured traffic for retransmissions.
        """
        try:
            result = subprocess.run(
                ["tcpdump", "-r", pcap_file, "-n", "-tt"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            retransmissions = []
            for line in result.stdout.splitlines():
                if "[R]" in line:
                    timestamp = line.split()[0]
                    retransmissions.append(datetime.fromtimestamp(float(timestamp)))
            return retransmissions
        except subprocess.CalledProcessError as e:
            print(f"Error analyzing traffic: {e}")
            return []

    def visualize_retransmissions(retransmissions):
        """
        Visualize retransmissions over time.
        """
        if not retransmissions:
            print("No retransmissions to visualize.")
            return

        times = [t.strftime("%H:%M:%S") for t in retransmissions]
        counts = {time: times.count(time) for time in set(times)}

        plt.figure(figsize=(10, 6))
        plt.bar(counts.keys(), counts.values(), color="blue")
        plt.xlabel("Time")
        plt.ylabel("Retransmissions")
        plt.title("Retransmissions Over Time")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    pass
