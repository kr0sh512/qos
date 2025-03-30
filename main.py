import subprocess
import time
import logging
import coloredlogs
import statistics
import json
import traceback
import threading
import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import os


coloredlogs.install(level="INFO")


class QoSMonitor:

    def __init__(self, duration=60, host="10.0.0.2"):
        self.duration = duration
        self.latency_data = []
        self.packet_loss_data = []
        self.throughput_data = []
        self.analysis_results = []
        # стандартный host - h2 в сети mininet
        self.host = host

    def run(self):
        start_time = time.time()
        while time.time() - start_time < self.duration:
            elapsed_time = time.time() - start_time
            progress = (elapsed_time / self.duration) * 100
            logging.info(f"Progress: {progress:.2f}%")

            self.measure_latency_and_packet_loss(
                packet_number=4
            )  # количество ping запросов
            self.measure_throughput(duration=0.5)  # продолжительность замера скорости

            time.sleep(1)

        logging.info("QoS monitoring completed")
        logging.info(f"Duration: {self.duration} seconds")
        logging.info(f"Latency data: {self.latency_data}")
        logging.info(f"Packet loss data: {self.packet_loss_data}")
        logging.info(f"Throughput data: {self.throughput_data}")

        self.save_data()
        self.print_data()
        self.visualize_data()

        return

    def measure_latency_and_packet_loss(self, packet_number=4):
        try:
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
                    float(line.split("time=")[1].split(" ")[0])
                    for line in latency_lines
                ]
                self.latency_data.extend(latencies)

                packet_loss_line = [
                    line for line in output.split("\n") if "packet loss" in line
                ][0]
                packet_loss = float(
                    packet_loss_line.split(",")[2].split("%")[0].strip()
                )
                self.packet_loss_data.append(packet_loss)
            else:
                logging.error(
                    f"Error measuring latency and packet loss: {process.stderr}"
                )
        except Exception as e:
            logging.error(f"Error measuring latency and packet loss: {e}")
            logging.info(traceback.format_exc())

        return

    def measure_throughput(self, duration=1):
        try:
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

        except Exception as e:
            logging.error(f"Error measuring throughput: {e}")
            logging.info(traceback.format_exc())

        return

    def save_data(self):
        # Сохранение данных в формате json
        qos_data = {
            "Latency": self.latency_data,
            "Packet Loss": self.packet_loss_data,
            "Throughput": self.throughput_data,
        }

        for parameter, data in qos_data.items():
            if data:
                self.analysis_results.append(
                    {
                        "QoS Parameter": parameter,
                        "Average": round(statistics.mean(data), 2),
                        "Median": round(statistics.median(data), 2),
                        "95th Percentile": round(
                            statistics.quantiles(data, n=100)[94], 2
                        ),
                        "Min": round(min(data), 2),
                        "Max": round(max(data), 2),
                        "Standard Deviation": (
                            round(statistics.stdev(data), 2) if len(data) > 1 else 0.0
                        ),
                    }
                )
            else:
                logging.warning(f"No data available for {parameter}")

        os.makedirs("output", exist_ok=True)
        with open("output/qos_analysis.json", "w") as jsonfile:
            json.dump(self.analysis_results, jsonfile, indent=4)

        return

    def print_data(self):
        if not self.analysis_results:
            logging.warning("No analysis results available")
            return

        print(
            f"{'QoS Parameter':<15}{'Average':<10}{'Median':<10}{'95th Percentile':<15}{'Min':<10}{'Max':<10}{'Std Dev':<10}"
        )
        print("-" * 70)
        for result in self.analysis_results:
            print(
                f"{result['QoS Parameter']:<15}{result['Average']:<10}{result['Median']:<10}{result['95th Percentile']:<15}{result['Min']:<10}{result['Max']:<10}{result['Standard Deviation']:<10}"
            )

        return

    def visualize_data(self):
        try:
            parameters = {
                "Latency (ms)": self.latency_data,
                "Packet Loss": self.packet_loss_data,
                "Throughput (Mb/s)": self.throughput_data,
            }

            for parameter, data in parameters.items():
                if data:
                    plt.figure(figsize=(10, 6))
                    plt.hist(
                        data,
                        bins=20,
                        color="blue",
                        alpha=0.7,
                        edgecolor="black",
                        weights=np.ones(len(data)) / len(data),
                    )
                    plt.title(f"{parameter} Distribution")
                    plt.xlabel(parameter)
                    plt.ylabel("Frequency (%)")
                    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
                    plt.grid(axis="y", alpha=0.75)
                    os.makedirs("output", exist_ok=True)
                    plt.savefig(
                        f"output/{parameter.lower().replace(' ', '_').replace('/', '')}_histogram.png"
                    )
                    plt.close()
                else:
                    logging.warning(f"No data available for {parameter} to visualize")
        except Exception as e:
            logging.error(f"Error visualizing data: {e}")
            logging.info(traceback.format_exc())
        pass


if __name__ == "__main__":
    # первый параметр командной строки - продолжительность замера
    duration = 60
    try:
        if len(sys.argv) > 1:
            duration = int(sys.argv[1])

        logging.info(f"Duration set to {duration} seconds")
    except Exception as e:
        logging.error("Invalid duration value. Using default value of 60 seconds.")

    monitor = QoSMonitor(duration=duration)
    monitor.run()

    exit(0)
