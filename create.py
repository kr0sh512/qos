from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI

"""
Создание сети mininet из (h1, h2) хостов и 1 коммутатора

Параметры для каждого канала:
    - Задержка: 10 мс
    - Потери пакетов: 0,5%
    - Пропускная способность: 10 Мбит/с

Также:
    - сервер iperf на h2
    - подключение .venv для корректной работы питона на h1
    
Последующий запуск CLI
"""


def create_mininet():
    net = Mininet(controller=Controller, link=TCLink)

    net.addController("c0")
    s1 = net.addSwitch("s1")

    h1 = net.addHost("h1")
    h2 = net.addHost("h2")

    net.addLink(h1, s1, bw=10, delay="10ms", loss=0.5)
    net.addLink(h2, s1, bw=10, delay="10ms", loss=0.5)

    net.start()

    # Run iperf3 server on h2
    h2 = net.get("h2")
    h2.cmd("iperf -s &")
    h1 = net.get("h1")
    h1.cmd("source .venv/bin/activate")

    CLI(net)


if __name__ == "__main__":
    setLogLevel("info")
    create_mininet()
