# -*- coding: utf-8 -*-
'''
  _______________________________________________________________________
 |                                                                       |
 | Time Matrix MPI Implementation                                        |
 | Multipurpose implementation                                           |
 | Authors: -Andrei Bartra (andreibartra)                                |
 | Date: April 2021                                                      |
 |_______________________________________________________________________|

'''

#  ________________________________________
# |                                        |
# |               1: Settings              |
# |________________________________________|


import numpy as np
import pandas as pd
import json
import os

#Local Parallelization
from mpi4py import MPI

#Time Duration Utilities
import time 
from functools import wraps

#Path Algorithm
from skimage import graph


#  ________________________________________
# |                                        |
# |            2: Time Decorator           |
# |________________________________________|

#Timer Decorator
# From https://stackoverflow.com/questions/3620943/measuring-elapsed-time-with-the-time-module 
PROF_DATA = {}

def profile(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        start_time = time.time()

        ret = fn(*args, **kwargs)

        elapsed_time = time.time() - start_time

        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = [0, []]
        PROF_DATA[fn.__name__][0] += 1
        PROF_DATA[fn.__name__][1].append(elapsed_time)

        return ret

    return with_profiling


def print_prof_data():
    for fname, data in PROF_DATA.items():
        max_time = max(data[1])
        avg_time = sum(data[1]) / len(data[1])
        print ("Function %s called %d times. " % (fname, data[0]))
        print ('Execution time max: %.3f, average: %.3f' % (max_time, avg_time))


def clear_prof_data():
    global PROF_DATA
    PROF_DATA = {}


#  ________________________________________
# |                                        |
# |             3: Load Data               |
# |________________________________________|

def get_inputs(file):
    with open(file) as json_file:
        input_data =  json.load(json_file)
    return input_data


def loading_data(query_file, raster_file):
    query = pd.read_csv(query_file)
    query = query.drop(query.columns[0], axis=1)
    raster = np.genfromtxt(raster_file, delimiter=',')
    raster = raster[1:,1:]
    return query, raster


#  ________________________________________
# |                                        |
# |                 4: MPI                 |
# |________________________________________|


def travel_time(x_1, y_1, x_2, y_2, array, cost_only=True):
    route, cost = graph.route_through_array(array, (x_1, y_1), (x_2, y_2), geometric=True)
    if cost_only:
        return cost
    else:
        return route, cost


@profile
def run_mpi_local(query, array):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    ini = int(rank*query.shape[0]/size)
    end = int((rank+1)*query.shape[0]/size)
    temp = query.iloc[ini:end]
    temp['cost'] = temp[['pixel_x_x', 'pixel_y_x', 'pixel_x_y', 'pixel_y_y']]. \
    apply(lambda x:  travel_time(x[0], x[1], x[2], x[3], array), axis=1)
    
    gather = None
    
    _list = comm.gather(temp,root=0)

    if rank ==0:
        gather = pd.concat(_list)

    return gather


def outputs(gather):
    if gather is not None:
        gather.to_csv('mpi_query.csv')
        exec_time = {'time': PROF_DATA['run_mpi_local'][1][0]}

        with open('mpi_times.json', 'w') as fp:
            json.dump(exec_time, fp)

#  ________________________________________
# |                                        |
# |        5: Compiling and Wrapping       |
# |________________________________________|

def mpi_wrapper():
    inputs = get_inputs('inputs.json')
    df, array = loading_data(inputs['query'], inputs['raster'])
    rv = run_mpi_local(df, array)
    outputs(rv)
def main():
    mpi_wrapper()

if __name__ == '__main__':
    main()

#mpirun -n 5 mpi_code.py 