import subprocess
import time


class QoSMonitor:
    def __init__(self, duration=60):
        self.duration = duration
        self.latency_data = []
        self.packet_loss_data = []
        self.throughput_data = []

    def run(self):
        start_time = time.time()
        while time.time() - start_time < self.duration:
            self.measure_latency_and_packet_loss()
            self.measure_throughput()
            time.sleep(1)

        self.save_data()
        self.print_data()


if __name__ == "__main__":
    monitor = QoSMonitor()
    monitor.run()
