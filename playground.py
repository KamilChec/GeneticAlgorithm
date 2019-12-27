import numpy as np
import subprocess
import random
from file_read_backwards import FileReadBackwards

file_path = "res/GEOM_FC_ASSY_TYPE_REV2"


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


def get_days():
    with FileReadBackwards("res/WUTBEAVRS-1.DEP", encoding="utf-8") as data:
        for line in data:
            if line.strip() == 79 * '=':
                break
        line = data.readline()
        return line.split()[2]


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
            if random.uniform(0, 100) < 20:
                array[i][j] = random.uniform(1, 10)
                a += 1
    return array


def create_array_v2():
    array = np.zeros([17, 17], dtype=int)
    probability = [0.35, 0.02, 0.15, 0.16, 0.16, 0.06, 0.02, 0.04, 0.04]
    for i in range(np.shape(array)[0]):
        for j in range(np.shape(array)[1]):
            choice = np.random.choice(list(range(1, 10)), p=probability)
            array[i][j] = int(choice)
    return array


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


array = apply_mask(create_array_v1()) # wybrać między 1/2/3
write_array(array)

a = subprocess.call(['p320mXX.exe', 'BEAVRS_20_HFP_MULTI_5_2018.INP'], shell=True, cwd="res")
print(get_days())
