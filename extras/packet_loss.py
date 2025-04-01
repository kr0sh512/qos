import subprocess
import time
import logging
import coloredlogs
from vizualizations import Vizualization

coloredlogs.install(level="INFO")


class PacketLoss:
    def __init__(self, duration=60, host="10.0.0.2"):
        self.duration = duration
        self.packet_loss_data = []
        self.host = host

    def run(self):
        start_time = time.time()
        while time.time() - start_time < self.duration:
            self.measure(packet_number=4)

            time.sleep(1)

        Vizualization.visualize_data("Packet Loss (%)", self.packet_loss_data)

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
            packet_loss_line = [
                line for line in output.split("\n") if "packet loss" in line
            ][0]
            packet_loss = float(packet_loss_line.split(",")[2].split("%")[0].strip())
            self.packet_loss_data.append(packet_loss)
        else:
            logging.error(f"Error measuring latency and packet loss: {process.stderr}")

        return
