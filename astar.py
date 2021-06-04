# -*- coding: utf-8 -*-
'''
  _______________________________________________________________________
 |                                                                       |
 | A-Star Implementation                                                 |
 | Multipurpose implementation                                           |
 | Authors: -Andrei Bartra (andreibartra)                                |
 | Inspired by https://github.com/mikepound/mazesolving                  |
 | Date: April 2021                                                      |
 |_______________________________________________________________________|

'''
import numpy as np
from fib_heap import FibonacciHeap as fh
node = fh.Node
import copy

class vert():
    def __init__(self, array, xy, end, min_t, parent=None):
        '''
        array: The grid
        xy: grid coordinates of current vertex
        end: grid coordinates of end point
        maxv: max speed (min time) in the area
        parent: previous vertex
        '''
        dist = (((np.subtract(xy, end)**2).sum())**(1/2))*min_t
        if parent:
            cost = parent.value['cost'] + array[xy]
        else:
            cost = 0
        self.key = cost + dist
        self.value = {'xy': xy, 'cost': cost, 'parent': parent}


def get_links(current, array, avail, end, min_t, th):
        #make sure within limits and transitable
    l, w = array.shape
    links = []
    for i in [-1, 0 ,1]:
        for j in [-1, 0 ,1]:
            x, y = current.value['xy']
            avail[x, y] = False
            xy = x + i, y + j
            if avail[xy] and\
               xy != (0, 0) and\
               0 <= x <= l and\
               0 <= y <= w and\
               array[xy] < th:
                links += [vert(array, xy, end, min_t, current)]
               # avail[xy] = False
    return links


def path(cur, array, ini):
    path = []
    tot_time = 0
    while True:
        path += [cur.value['xy']]
        cur = cur.value['parent']
        tot_time += array[cur.value['xy']]
        if cur.value['xy'] == ini:
            break
    return path, tot_time

def solve(array, ini, end, th, min_t=10):

    avail = np.ones_like(array, dtype=bool)
    avail[ini] = True
    o_list = fh()
    start = vert(array, ini, end, min_t=min_t)
    o_list.insert(start.key, start.value)
    
    while True:
        bu = copy.deepcopy(o_list)
        try:
            current = o_list.extract_min()
        except:
            return bu, False
        #print(current.value['xy'], current.key, current.value['cost'])
        if current.value['xy'] == end:
            return path(current, array, ini)

        for adj in get_links(current, array, avail, end, min_t, th):
            o_list.insert(adj.key, adj.value)

        if o_list.total_nodes == 0:
            break
    return path(current, array, ini)