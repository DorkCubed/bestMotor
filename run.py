from supporting import *
import random

class Motorlims:
    grainrange: any
    min_diameter: float
    max_diameter: float
    min_core_ratio: int
    max_core_ratio: int
    min_throat_len: float
    max_throat_len: float 
    pt_ratio: float

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

def anneal_train(finalfile, Startprops: Motorprops, Lims: Motorlims, iterations=100, angle_lock = True):
    with open(finalfile, "a") as fin:
        writeall(["throat", "len", "number of grains", "grain diameter", "core diameter", "convergance angle",
             "divergance angle", "burn time", "Impulse", "avg thrust", "peak pressure", "flatness"], fin, True)
    fin.close()
    
    Startprops.number_of_grains = Lims.grainrange[0]
    Startprops.exit = sqrt(sq(Startprops.grain_core) / Lims.pt_ratio) * 1.5
    oldarr = props_to_arr(Startprops) 
    newarr = []
    tp = ThrustPlot()
    old = eval(finalfile, Startprops, "output", tp, Lims.pt_ratio)
    found = 0

    for i in range(iterations):
        if found > 10:
            break

        for j in range(len(oldarr)):
            if j in [0, 1, 7]:
                continue
            if angle_lock and (j == 4 or j == 5):
                continue
            
            newarr = oldarr.copy()

            if (j == 4 or j == 5):
                newarr[j] = round(newarr[j] * random_scale(i, iterations, 1))
            else:
                newarr[j] = newarr[j] * random_scale(i, iterations)
            
            match j:
                case 2:
                    if (newarr[2] != bounded(newarr[2], Lims.min_diameter, Lims.max_diameter)): continue
                case 3:
                    if (newarr[3] != bounded(newarr[3], (newarr[2] / Lims.min_core_ratio), (newarr[2] / Lims.max_core_ratio))): continue
                    throat = sqrt(sq(newarr[3]) / Lims.pt_ratio)
                    newarr[7] = throat * 1.5
                case 6:
                    if (newarr[6] != bounded(newarr[6], Lims.min_throat_len, Lims.max_throat_len)): continue
            
            if newarr[j] == oldarr[j]:
                continue
            
            new = eval(finalfile, arr_to_props(newarr), "output", tp, Lims.pt_ratio)
            
            if new > old:
                old = new
                oldarr[j] = newarr[j]
                oldarr[1] = newarr[1]
                if j == 3:
                    oldarr[7] = newarr[7]
                found = 0
                tp.best.set_text(f'Best Performance: {new:.2f}')

                for k in range(Lims.grainrange[0], Lims.grainrange[1]+1):
                    grainarr = oldarr.copy()
                    grainarr[1] = k
                    new = eval(finalfile, arr_to_props(grainarr), "output", tp, Lims.pt_ratio)
                    if new > old:
                        old = new
                        oldarr[1] = k
                        tp.best.set_text(f'Best Performance: {new:.2f}')
                    elif k > oldarr[1] : break

            else: found += 1

    return arr_to_props(oldarr)

Props = Motorprops()

Props.grain_diameter = 0.075
Props.grain_core = (Props.grain_diameter / 3)
Props.conv_angle = 30
Props.div_angle = 12
Props.throatlen = 0.0
Props.prop_weight = 1000

Limits = Motorlims()

Limits.grainrange = [2, 5]
Limits.min_diameter = 0.025
Limits.max_diameter = 0.1
Limits.min_core_ratio = 6
Limits.max_core_ratio = 1.1
Limits.min_throat_len = 0.0
Limits.max_throat_len = 0.05
Limits.pt_ratio = 2.85

make_ric("temp.ric", anneal_train("outputs.csv", Props, Limits, 100, Limits.pt_ratio), Limits.pt_ratio)
subprocess.run(["python", "main.py", "temp.ric"])