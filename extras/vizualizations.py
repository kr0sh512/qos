import logging
import coloredlogs
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import os


coloredlogs.install(level="INFO")


class Vizualization:
    def visualize_data(parameter, data):
        if not data:
            logging.warning(f"No data available for {parameter} to visualize")

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

        return
