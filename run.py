from supporting import *
import multiprocessing

def testing(finalfile, props):
    with open(finalfile, "a") as fin:
        while (props.grain_core) < (props.grain_diameter / 1.5):
            while (props.number_of_grains) < 7:
                eval(finalfile, props, "output")
                props.number_of_grains += 1
            props.grain_core += 0.001
            props.number_of_grains = 3
            writeall(["throat", "len", "number of grains", "grain diameter", "core diameter", "convergance angle",
                 "divergance angle", "burn time", "thrust", "avg thrust", "peak pressure", "flatness"], fin, True)
        fin.close()

props = Motorprops()
props.number_of_grains = 3
props.grain_diameter = 0.075
props.grain_core = (props.grain_diameter / 3)
props.conv_angle = 30
props.div_angle = 12
props.throatlen = 0.0
props.prop_weight = 1000
props.exit = 0.1
testing("outputs.csv", props)