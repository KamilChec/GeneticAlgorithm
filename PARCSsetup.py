import numpy as np
import random
from file_read_backwards import FileReadBackwards
import matplotlib.pyplot as plt
import subprocess


file_path = "res/GEOM_FC_ASSY_TYPE_REV2"


def mod_file_path(numb):
    global file_path
    file_path = "res/Chromosome" + str(numb) + "/GEOM_FC_ASSY_TYPE_REV2"


def apply_mask(insert_array):
    text = []
    with open(file_path) as input_data:
        for line in input_data:
            if line.strip() == 'rad_conf':
                break
        for line in input_data:
            if line.strip() == '!':
                break
            text.append([int(x) for x in line.split()])

    array = np.asarray(text)
    circuit_array = np.ones([17, 17], dtype=int)
    base_array = np.zeros([17, 17], dtype=int)
    for i in range(np.shape(array)[0]):
        if i == 1 or i == 15:
            for j in range(np.shape(array)[1]):
                if 4 < j < 12:
                    base_array[i][j] = 1
                    circuit_array[i][j] = 0
        if i == 2 or i == 14:
            for j in range(np.shape(array)[1]):
                if 2 < j < 14:
                    base_array[i][j] = 1
                    circuit_array[i][j] = 0
        if 2 < i < 5 or 11 < i < 14:
            for j in range(np.shape(array)[1]):
                if 1 < j < 15:
                    base_array[i][j] = 1
                    circuit_array[i][j] = 0
        if 5 <= i <= 11:
            for j in range(np.shape(array)[1]):
                if 0 < j < 16:
                    base_array[i][j] = 1
                    circuit_array[i][j] = 0
    scrap_array = np.multiply(base_array, insert_array)
    mask_array = np.multiply(circuit_array, array)
    final_array = np.add(scrap_array, mask_array)
    return final_array


def write_array(array):
    with open(file_path, "r") as f:
        lines = f.readlines()
    string = ""
    for i in range(np.shape(array)[0]):
        string += (' ')
        for j in range(np.shape(array)[1]):
            string += (str(array[i][j]))
            string += ('\t')
        string += ('\n')
    lines[5:22] = string
    with open(file_path, "w") as f:
        for line in lines:
            f.write(line)


def get_keff(numb):
    file_path = "res/Chromosome" + str(numb) + "/WUTBEAVRS-1.DEP"
    keff = []
    day = []
    with FileReadBackwards(file_path, encoding="utf-8") as data:
        for line in data:
            if line.strip() == 79 * '=':
                break
        for line in data:
            if "Keff" in line:
                break
            keff.append(float(line.split()[3]))
            day.append(float(line.split()[2]))
    return [keff[::-1], day[::-1]]


def objective_function(keff_list):
    keff = keff_list[0]
    day = keff_list[1]
    score = 0
    const1 = 1037
    const2 = 169
    penalty = 0
    for val in keff:
        if val > 1.07:
            penalty += (const1/len(keff))/(1.26 - 1.07) * (val - 1.07)
            # penalty += math.exp(val)
        elif val < 1:
            penalty += (const2/len(keff))/(1. - 0.84) * (val - 0.84)
            # penalty += math.exp(val)
        # else:
            # score += (const/len(keff))/(1.07 - 1.) * (val - 1.)
    if max(keff) > 1:
        for i in range(len(keff)):
            if keff[i] < 1 <= keff[i - 1]:
                score += day[i - 1]
                # print(day[i - 1])            #przyjrzec sie
                break
    return score - penalty


def create_array_v1():
    text = []
    with open('res/base', 'r') as input_data:
        for line in input_data:
            if line.strip() == 'rad_conf':
                break
        for line in input_data:
            if line.strip() == '!':
                break
            text.append([int(x) for x in line.split()])
    array = np.asarray(text)
    list(range(1, 10))
    a = 0
    for i in range(np.shape(array)[0]):
        for j in range(np.shape(array)[1]):
            if random.uniform(0, 100) < 50:
                array[i][j] = random.uniform(1, 10)
                a += 1
    return apply_mask(array)


def create_array_v2():
    array = np.zeros([17, 17], dtype=int)
    probability = [0.35, 0.02, 0.15, 0.16, 0.16, 0.06, 0.02, 0.04, 0.04]
    for i in range(np.shape(array)[0]):
        for j in range(np.shape(array)[1]):
            choice = np.random.choice(list(range(1, 10)), p=probability)
            array[i][j] = int(choice)
    return apply_mask(array)


def create_array_v3():
    available_choice = [1] * 65 + [2] * 4 + [3] * 29 + [4] * 32 + [5] * 32 + [6] * 12 + [7] * 4 + [8] * 7 + [9] * 8
    array = np.ones([17, 17], dtype=int)
    array = apply_mask(array)
    for i in range(np.shape(array)[0]):
        for j in range(np.shape(array)[1]):
            if array[i][j] == 1:
                choice = random.choice(available_choice)
                array[i][j] = choice
                available_choice.remove(choice)
    return array


def create_array_v4():
    return apply_mask(np.random.randint(1, 10, size=(17, 17)))


def best_geom():
    return apply_mask(np.full((17, 17), 5))


def worst_geom():
    return apply_mask(np.full((17, 17), 1))


def plot_keff(numb):
    score = objective_function(get_keff(numb))
    keff = get_keff(numb)[0]
    x = get_keff(numb)[1]
    fig = plt.figure(figsize=(8, 7))
    plt.subplot(2, 1, 1)
    plt.plot(x, keff, linestyle='dashed', marker='.', markersize=12)
    plt.hlines(1, 0, x[-1])
    plt.hlines(1.07, 0, x[-1])
    plt.grid()
    plt.xlabel('day')
    plt.ylabel('keff')
    plt.title("score: {}".format(score))
    plt.subplot(2, 1, 2)
    x = list(range(40))
    plt.plot(x, keff, linestyle='dashed', marker='.', markersize=12)
    plt.hlines(1, 0, x[-1])
    plt.hlines(1.07, 0, x[-1])
    plt.grid()
    plt.xlabel('point')
    plt.ylabel('keff')
    plt.show()


# array = best_geom()
# mod_file_path(1)  # zmiana 25.12, usunac
# write_array(array)
# subprocess.call(['p320mXX.exe', 'BEAVRS_20_HFP_MULTI_5_2018.INP'], shell=True, cwd="res/Chromosome1")
# plot_keff(1)



