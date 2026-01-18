from math import sqrt
import pandas as pd
import numpy as np
import subprocess
import matplotlib.pyplot as plt

class Motorprops:
    prop_weight: int
    number_of_grains: int
    grain_diameter: float
    grain_core: float
    conv_angle: int
    div_angle: int
    throatlen: float
    
    def __init__(self):
        self.exit = 0.1

class ThrustPlot:
    def __init__(self):
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'b-', linewidth=2)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Thrust')
        self.ax.grid(True)
        self.best = plt.text(0.05, 0.3, '')

def sq(x):
    return (x*x)

def rms(arr):
    rms = 0
    for i in arr:
        rms = rms + sq(i)
    rms = rms / len(arr)
    return sqrt(rms)

def bounded(a, lower, upper):
    if a < lower:
        return lower
    elif a > upper:
        return upper
    else:
        return a

def writeall(arr, fin, last=False):
    for i in arr:
        fin.write(str(i) + ", ")
    if last == True:
        fin.write("\n")


def make_ric(output, props: Motorprops, pt_ratio = 3.05):
    prop_w = props.prop_weight / 1000
    with open("boiler.txt", "r") as f:
        g = f.read().split("\n\n")
    density = float(g[1].split(": ")[1].split("\n")[0]) / 1000
    with open(output, "w") as f:
        f.write(g[0])
        length = (prop_w / density) / (3.14 * sq(props.grain_diameter/2) -
                                 3.14 * sq(props.grain_core / 2)) / props.number_of_grains / 1000
        throat = sqrt(sq(props.grain_core) / pt_ratio)
        f.write("\n")
        for i in range(props.number_of_grains):
            f.write("  - properties:\n")
            f.write("      coreDiameter: " + str(props.grain_core) + "\n")
            f.write("      diameter: " + str(props.grain_diameter) + "\n")
            f.write("      inhibitedEnds: Neither\n")
            f.write("      length: " + str(length) + "\n")
            f.write("    type: BATES\n")

        f.write("  nozzle:\n")
        f.write("    convAngle: " + str(props.conv_angle) + "\n")
        f.write("    divAngle: " + str(props.div_angle) + "\n")
        f.write("    efficiency: 0.95\n")
        f.write("    erosionCoeff: 0.0\n")
        f.write("    exit: " + str(props.exit) + "\n")
        f.write("    slagCoeff: 0.0\n")
        f.write("    throat: " + str(throat) + "\n")
        f.write("    throatLength: " + str(props.throatlen) + "\n")
        f.write(g[1])

    return throat, length


def eval(finalfile: str, props: Motorprops, qid = "output", tp: ThrustPlot = None, pt_ratio = 3.05):
    throat, len = make_ric("temp.ric", props, pt_ratio)

    if tp is not None: plt.pause(0.1)
    subprocess.run(["python", "main.py", "-o", qid + ".txt", "-h", "temp.ric"])

    with open((qid + ".txt"), "r") as csvfiled:
        csv_data = pd.read_csv(csvfiled)

        if tp is not None:
            tp.line.set_data(csv_data['Time(s)'], csv_data['Thrust(N)'])
            tp.ax.relim()
            tp.ax.autoscale_view()
            tp.fig.canvas.draw()
            tp.fig.canvas.flush_events()

        burntime = float(csv_data.iloc[-1, 0])
        avgthrust = (csv_data.iloc[:, 3]).astype(float)
        avgthrust = np.mean(avgthrust)
        peakpressure = max((csv_data.iloc[:, 2]).astype(float))
        flatness = rms((csv_data.iloc[:, 3]).astype(float) - avgthrust)
        imp = sum((csv_data.iloc[:, 3]).astype(float) * 0.03)

    with open(finalfile, "a") as fin:
        writeall([throat, len, props.number_of_grains, props.grain_diameter, props.grain_core, props.conv_angle, props.div_angle], fin)
        writeall([burntime, imp, avgthrust, peakpressure, flatness], fin, True)
        fin.close()
    
    perf = (imp * flatness * burntime) / (peakpressure + 1e-5)
    print(perf)
    return perf