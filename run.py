from supporting import *
import multiprocessing
import random

def testing(finalfile, props:Motorprops):
    with open(finalfile, "a") as fin:
        writeall(["throat", "len", "number of grains", "grain diameter", "core diameter", "convergance angle",
             "divergance angle", "burn time", "thrust", "avg thrust", "peak pressure", "flatness"], fin, True)
    fin.close()
    while (props.grain_core) < (props.grain_diameter / 1.5):
        while (props.number_of_grains) < 7:
            eval(finalfile, props, "output")
            props.number_of_grains += 1
        props.grain_core += 0.001
        props.number_of_grains = 3

def props_to_arr(props: Motorprops):
    return [props.prop_weight, props.number_of_grains, props.grain_diameter, props.grain_core, props.conv_angle, props.div_angle, props.throatlen, props.exit]

def arr_to_props(arr) -> Motorprops:
    props = Motorprops()
    props.prop_weight = int(arr[0])
    props.number_of_grains = int(arr[1])
    props.grain_diameter = float(arr[2])
    props.grain_core = float(arr[3])
    props.conv_angle = int(arr[4])
    props.div_angle = int(arr[5])
    props.throatlen = float(arr[6])
    props.exit = float(arr[7])
    return props

def random_scale(i: int, it: int, scale=0.01):
    return (1 + random.uniform(-10,10) * scale) * (1 - (i / it))

def anneal_train(finalfile, startprops: Motorprops, iterations=100, angle_lock = True):
    with open(finalfile, "a") as fin:
        writeall(["throat", "len", "number of grains", "grain diameter", "core diameter", "convergance angle",
             "divergance angle", "burn time", "thrust", "avg thrust", "peak pressure", "flatness"], fin, True)
    fin.close()
    
    oldarr = props_to_arr(startprops) 
    newarr = []
    old = eval(finalfile, arr_to_props(oldarr), "output")

    for i in range(iterations):
        for j in range(len(oldarr)):
            if j == 0:
                continue
            if angle_lock and (j == 4 or j == 5):
                continue
        
            newarr = oldarr.copy()

            if (j == 1 or j == 4 or j == 5):
                newarr[j] = round(newarr[j] * random_scale(i, iterations, 1))
            else:
                newarr[j] = newarr[j] * random_scale(i, iterations)
                
            match j:
                case 1:
                    if (newarr[1] != bounded(round(newarr[1]), 1, 6)): continue
                case 2:
                    if (newarr[2] != bounded(newarr[2], 0.03, 0.2)): continue
                case 3:
                    if (newarr[3] != bounded(newarr[3], (newarr[2] / 6), (newarr[2] - 0.01))): continue
                case 6:
                    if (newarr[6] != bounded(newarr[6], 0.0, 0.05)): continue
                case 7:
                    throat = sqrt(sq(newarr[3]) / 3.05)
                    if (newarr[7] != bounded(newarr[7], throat * 1.1, 0.5)): continue

            if newarr[j] == oldarr[j]:
                continue

            new = eval(finalfile, arr_to_props(newarr), "output")
            if new > old:
                old = new
                oldarr[j] = newarr[j]

    return arr_to_props(newarr)

        

props = Motorprops()
props.number_of_grains = 3
props.grain_diameter = 0.075
props.grain_core = (props.grain_diameter / 3)
props.conv_angle = 30
props.div_angle = 12
props.throatlen = 0.0
props.prop_weight = 1000
props.exit = 0.1

anneal_train("outputs.csv", props)