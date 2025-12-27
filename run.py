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

def grad(finalfile, oldprops, oldarr, newprops, newarr):
    gradarr = []
    dy = eval(finalfile, newprops) - eval(finalfile, oldprops)
    for i in range(len(oldarr)):
        gradarr.append(dy / (newarr[i] - oldarr[i] + 1e-6))
    return gradarr

def descent_train(finalfile, startprops: Motorprops, learningrate=0.1, iterations=10, angle_lock = True):
    oldarr = props_to_arr(startprops) 
    newarr = oldarr.copy()
    for i in range(iterations):

        for j in range(len(oldarr)): 
            newarr[j] = (oldarr[j] * (1 + random.uniform(-1,1) * 0.1))   
     
        newarr[0] = oldarr[0]
        newarr[1] = max(1, round(newarr[1]))
        newarr[1] = min(6, newarr[1])
        newarr[2] = max(0.03, newarr[2])
        newarr[2] = min(0.2, newarr[2])
        newarr[3] = max((newarr[2] / 6), newarr[3])
        newarr[3] = min(newarr[2] - 0.01, newarr[3])
        if angle_lock:
            newarr[4] = oldarr[4]
            newarr[5] = oldarr[5]
        newarr[6] = max(0.0, newarr[6])
        newarr[6] = min(0.05, newarr[6])
        throat = sqrt(sq(newarr[3]) / 3.05)
        newarr[7] = max((throat * 1.1), newarr[7])
        newarr[7] = min(0.5, newarr[7])

        print(newarr)
        print()
        print()

        oldprops = arr_to_props(oldarr)
        newprops = arr_to_props(newarr)
        gradarr = grad(finalfile, oldprops, oldarr, newprops, newarr)
        oldarr = newarr.copy()
        for j in range(len(oldarr)):
            newarr[j] = newarr[j] - learningrate * gradarr[j]

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
descent_train("outputs.csv", props)