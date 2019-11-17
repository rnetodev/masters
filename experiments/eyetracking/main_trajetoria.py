import argparse
import os

import matplotlib

matplotlib.use("TKAgg", warn=False, force=True)

import matplotlib.pyplot as plt
plt.style.use('seaborn-white')

import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D

import rbf

import dede_clusterfix
import juju_clusterfix

# --
# Argument parser
# --
args_parser = argparse.ArgumentParser(
    description="Track some primatal friends \U0001F435"
)
args_parser.add_argument(
    "-d", "--dataset", nargs=1, type=str, choices=("dede", "juju"), required=True
)
args_parser.add_argument(
    "-f",
    "--feature",
    nargs=1,
    type=str,
    choices=("dist_filt", "vel_filt"),
    required=True,
)

args = args_parser.parse_args()

dataset, = args.dataset
feature, = args.feature

# --
# Reading dataset
# --

filepaths = {
    "dede": os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "sample_trials_preprocessed",
        "ded005a06",
        "ded005a06-Export-ReplaceEyeOut.txt",
    ),
    "juju": os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "sample_trials_preprocessed",
        "juj003b06",
        "juj003b06-Export-ReplaceEyeOut.txt",
    ),
}

clusterfixs = {
    "dede": dede_clusterfix,
    "juju": juju_clusterfix
}

plot_limits = {
    "dede": {
        "xlim": (0, 3.5),
        "ylim": (-2.5, 0)
    },
    "juju": {
        "xlim": (-1, 2.5),
        "ylim": (-3.5, 0)
    },
}

# --
# Define clusterfix module for comparisons
# --
clusterfix = clusterfixs[dataset]

# --
# Read, split and parse the lines
# --
fp = open(filepaths[dataset], "r")
file_lines = list(fp.readlines())
fp.close()

# Lines that should be converted to int
cleaned_data = []
for index, line in enumerate(file_lines):
    # indexes <= 1 should be convert to int
    parser = int if index <= 1 else float
    cleaned_data.append(list(map(parser, line.split())))

# Unpack dataset
x, y, x_filt, y_filt, vel_x, vel_y, vel, acc, velx_filt, vely_filt, vel_filt, acc_filt = (
    cleaned_data
)

# --
# Creating "dist_filt" through the euclidian distance cauculus
# --
dist_filt = []
for _x, _y in zip(x_filt, y_filt):
    d = np.sqrt(np.power(_x, 2) + np.power(_y, 2))
    dist_filt.append(d)


# --
# Which feature will be analyzed? And which params should be aplied to the RBF ?
# --
features = {
    "dist_filt": {
        "data": dist_filt,
        "kwargs": {"sigma": 0.005, "lambda_": 0.5, "alpha": 0.05, "delta": 0.75},
    },
    "vel_filt": {
        "data": vel_filt,
        "kwargs": {"sigma": 0.25, "lambda_": 0.005, "alpha": 0.001, "delta": 0.250},
    },
}

# --
# Setup RBF
# --
rbf = rbf.RBF(**features[feature]["kwargs"])

# --
# Plot setup
# --
fig = plt.figure()

# Title
fig.gca().set_title(dataset + " - " + feature)

# Datasets
xdata, ydata = [], []
start_x, start_y = [], []
end_x, end_y = [], []

# Lines/Points
ln, = plt.plot(xdata, ydata, "-", color=(0, 1, 0), linewidth=0.5)
start, = plt.plot(start_x, start_y, marker="$Início$", color="red", markersize=20)
end, = plt.plot(end_x, end_y, marker="$Fim$", color="gold", markersize=20)

custom_legends = [
    Line2D([0], [0], color=(0, 1, 0), ls="-", linewidth=1),
    Line2D([0], [0], color="r", ls="-", linewidth=1),
    Line2D([0], [0], color="gold", ls="-", linewidth=1),
]
fig.legend(
    custom_legends,
    ["Trajetória", "Início", "Fim"],
    ncol=1,
    borderaxespad=0,
    loc="lower center",
)

# Setup matplotlib font size and figure title
font = {"size": 8}
plt.rc("font", **font)
plt.rc("text", usetex=True)

def init():
    fig.gca().set_xlim(*plot_limits[dataset]["xlim"])
    fig.gca().set_ylim(*plot_limits[dataset]["ylim"])
    return (ln,)


# --
# Detecting fixations and updating canvas
# --
def handle(frame_index):
    # Scale down
    scale_factor = 10 ** 4
    scaled_x = x[frame_index] / scale_factor
    scaled_y = y[frame_index] / scale_factor

    xdata.append(scaled_x)
    ydata.append(scaled_y)
    ln.set_data(xdata, ydata)

    start_x, start_y = [xdata[0]], [ydata[0]]
    start.set_data(start_x, start_y)

    end_x, end_y = [xdata[-1]], [ydata[-1]]
    end.set_data(end_x, end_y)

    return (ln, start, end)


ani = FuncAnimation(
    fig, handle, frames=len(x), init_func=init, interval=0.000000001, blit=True, repeat=False
)

plt.show()
