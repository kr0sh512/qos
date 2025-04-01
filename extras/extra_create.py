from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
from mininet.log import setLogLevel
import numpy as np
import matplotlib.pyplot as plt
import os

"""
Анализ влияния параметров сети с использованием сетки значений (2 балла):
    - Проведите эксперименты, изменяя параметры каналов (считать, что все каналы предоставляют одинаковое качество сервиса) в Mininet по следующей сетке (пропускную способность оставить равной 10 Мбит/с):
      - Задержка (latency): 2 мс, 4 мс, 6 мс, 8 мс, 10 мс, 12 мс, 14 мс, 16 мс, 18 мс, 20 мс.
      - Потери пакетов (packet loss): 0,2%, 0,4%, 0,6%, 0,8%, 1%, 1,2%, 1,4%, 1,6%, 1,8%, 2%.

    Для каждой комбинации параметров запустите программу и соберите данные. Постройте график зависимости скорости от задержки и потери пакетов (например, построив тепловую карту).
"""


def create_mininet(latency, loss):
    net = Mininet(controller=Controller, link=TCLink)

    net.addController("c0")
    s1 = net.addSwitch("s1")

    h1 = net.addHost("h1")
    h2 = net.addHost("h2")

    net.addLink(h1, s1, bw=10, delay=f"{latency}ms", loss=loss)
    net.addLink(h2, s1, bw=10, delay=f"{latency}ms", loss=loss)

    net.start()

    h2 = net.get("h2")
    h2.cmd("iperf -s &")
    h1 = net.get("h1")
    result = h1.cmd("iperf -c " + h2.IP() + " -t 5 -f m")
    net.stop()

    for line in result.split("\n"):
        if "Mbits/sec" in line:
            return float(line.split()[-2])

    return 0


def run_experiments():
    latencies = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    losses = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]

    results = np.zeros((len(latencies), len(losses)))

    for i, latency in enumerate(latencies):
        for j, loss in enumerate(losses):
            print(f"Running experiment with latency={latency}ms, loss={loss}%")
            bandwidth = create_mininet(latency, loss)
            results[i, j] = bandwidth
            print(f"Bandwidth: {bandwidth} Mbits/sec")

    # np.savetxt(
    #     "output/results.csv", results, delimiter=",", header=",".join(map(str, losses))
    # )

    plt.figure(figsize=(10, 8))
    plt.imshow(results, cmap="hot", interpolation="nearest", aspect="auto")
    plt.colorbar(label="Bandwidth (Mbits/sec)")
    plt.xticks(range(len(losses)), [f"{l}%" for l in losses])
    plt.yticks(range(len(latencies)), [f"{l}ms" for l in latencies])
    plt.xlabel("Packet Loss")
    plt.ylabel("Latency")
    plt.title("Bandwidth Heatmap")
    os.makedirs("output", exist_ok=True)
    plt.savefig("output/heatmap.png")
    plt.show()


if __name__ == "__main__":
    setLogLevel("info")
    run_experiments()
