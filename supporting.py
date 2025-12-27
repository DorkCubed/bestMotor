from app import App
from PyQt6.QtCore import Qt
from math import sqrt
import csv
import subprocess

class Motorprops:
    prop_weight: int
    number_of_grains: int
    grain_diameter: float
    grain_core: float
    conv_angle: int
    div_angle: int
    throatlen: float
    exit: float

def sq(x):
    return (x*x)

def rms(arr):
    rms = 0
    for i in arr:
        rms = rms + sq(i)
    rms = rms / len(arr)
    return sqrt(rms)


def writeall(arr, fin, last=False):
    for i in arr:
        fin.write(str(i) + ", ")
    if last == True:
        fin.write("\n")


def make_ric(output, props: Motorprops):
    prop_w = props.prop_weight / 1000
    with open("boiler.txt", "r") as f:
        g = f.read().split("\n\n")
    density = float(g[1].split(": ")[1].split("\n")[0]) / 1000
    with open(output, "w") as f:
        f.write(g[0])
        length = (prop_w / density) / (3.14 * sq(props.grain_diameter/2) -
                                 3.14 * sq(props.grain_core / 2)) / props.number_of_grains / 1000
        throat = sqrt(sq(props.grain_core) / 3.05)
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


def eval(finalfile: str, props: Motorprops, qid = "output"):
    burntime = 0
    thrust = 0
    avgthrust = 0
    flatness = []
    peakpressure = 0
    items = 0

    throat, len = make_ric("temp.ric", props)
    subprocess.run(["python", "main.py", "-o", qid + ".txt", "-h", "temp.ric"])
    with open((qid + ".txt"), "r") as csvfiled:
        csv_data = csv.reader(csvfiled)
        skip = 0
        for row in csv_data:
            if skip == 0:
                skip = 1
                continue
            thrust = thrust + ((float(row[0]) - burntime) * float(row[3]))
            burntime = float(row[0])
            avgthrust = avgthrust + float(row[3])
            if float(row[2]) > peakpressure:
                peakpressure = float(row[2])
            items = items + 1
            flatness.append(float(row[2]))
        avgthrust = avgthrust / items
        for i in flatness:
            i = i - avgthrust
    flatness = rms(flatness)

    with open(finalfile, "a") as fin:
        writeall([throat, len, props.number_of_grains, props.grain_diameter, props.grain_core, props.conv_angle, props.div_angle], fin)
        writeall([burntime, thrust, avgthrust, peakpressure, flatness], fin, True)
        fin.close()
    
    return ((thrust * flatness * burntime) / peakpressure)
