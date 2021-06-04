# -*- coding: utf-8 -*-
'''
  _______________________________________________________________________
 |                                                                       |
 | Fibonacci Heap Implementation                                         |
 | Multipurpose implementation                                           |
 | Authors: -Andrei Bartra (andreibartra)                                |
 | Inspired by https://github.com/mikepound/mazesolving and              |
 | http://staff.ustc.edu.cn/~csli/graduate/algorithms/book6/chap21.htm   |
 | Date: April 2021                                                      |
 |_______________________________________________________________________|

'''

'''  ________________________________________
    |                                        |
    |               1: Settings              |
    |________________________________________|'''

import numpy as np #just for the log and int operation

'''  ________________________________________
    |                                        |
    |         2: Fibonacci Heap Class        |
    |________________________________________|'''


class FibHeap:
    '''
    Fibonacci Heap implementation
    Minor changes from https://github.com/mikepound/mazesolving
    details: http://staff.ustc.edu.cn/~csli/graduate/algorithms/book6/chap21.htm
    '''

    class Node:
        '''
        Circular doubly linked list for Fibonacci Heap.
        Each node start referencing itself
        Insert goes "after" (to the right) of the node
        each node can have a child
        New children are inserted into the original child
        '''
        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.degree = 0
            self.mark = False
            self.parent = self.child = None
            self.prev = self.next = self

        def issingle(self):
            return self == self.next

        def addnode(self, node):
            '''
            Cuts the linked list to the right of the node and inserts the new
            node (with its connections) in that space, reconnecting properly
            '''
            if node == None:
                return

            #This implementation ensures multiple nodes in the linked list
            #The order is important to avoid inconsistency in the pointers
            node.prev.next = self.next
            self.next.prev = node.prev
            node.prev = self
            self.next = node


        def remove(self):
            '''
            Removes connections of this node and connects the previous with next node
            '''
            #left of self to right new node
            self.prev.next = self.next
            self.next.prev = self.prev

            #Remove self connections
            self.next = self.prev = self

        def addchild(self, node):
            '''
            Adds a child to the Node. If the node has already a child, the new node
            is inserted next to the original child
            '''
            if self.child == None:
                self.child = node
            else:
                self.child.addnode(node)
            node.parent = self
            node.mark = False
            self.degree += 1

        def removechild(self, node):
            '''
            Removes the child node node and assign the next node (if exists) as the
            new child
            '''
            if node.parent != self:
                raise AssertionError("Parent of child is not self")

            if node.issingle():
                if self.child != node:
                    raise AssertionError("Node to remove is not self child")
                self.child = None
            else:
                if self.child == node:
                    self.child = node.next
                node.remove()

            node.parent = None
            node.mark = False
            self.degree -= 1

        def __repr__(self):
            parent = (self.parent.key) if self.parent else "None"
            child = (self.child.key) if self.child else "None"

            rv = (f"({self.prev.key}) <-- ({self.key}) --> ({self.next.key}) \n"
                  f"parent: {parent} \\ child: {child} \n"
                  f" degree: {self.degree} \\ mark: {self.mark}")
            return rv

        def __str__(self):
            return self.__repr__()

        def traverse(self):
            '''
            Simple circular doubly linked list traversal
            Task: Print
            '''
            print(self)
            node = self.next
            while node != self:
                node = node.next
                print(node)
        ## End of Node Class ##

    def __init__ (self):
        self.minnode = None
        self.count = 0
        self.maxdegree = 0


    def isempty(self):
        return self.count == 0


    def insert(self, node, count=True):
        '''


        Parameters
        ----------
        node : Fibonacci Heap Node object
        count : Boolean, optional
            If true is adding a new node to the heap. If false is just linking
            the node to the minimum node. The default is True.

        Returns
        -------
        None.

        '''
        if count:
            self.count += 1

        if self.minnode == None:
            self.minnode = node
        else:

            self.minnode.addnode(node)
            if node.key < self.minnode.key:
                self.minnode = node
        # return node

    def minimum(self):
        '''
        Simple return of the minimum mode
        '''
        if self.minnode == None:
            raise AssertionError("Cannot return minimum of empty heap")
        return self.minnode

    def merge(self, heap):
        '''
        Adds new heap as "next" node of minmode. Verifies if minmode changes

        '''
        self.minnode.addnode(heap.minnode)
        if self.minnode == None or (heap.minnode != None and heap.minnode.key < self.minnode.key):
            self.minnode = heap.minnode
        self.count += heap.count

    def update_max_degree(self):
        '''
        Updates the maximum degree of the heap:
            floor(log_{phi}(n))
        Returns
        -------
        None.

        '''

        self.maxdegree =  np.int(np.log(self.count)/np.log((1+5**(1/2))/2)) + 10
        #self.maxdegree = int(1e4)


    def remove_min(self):
        '''
        Performs the remove minimun function of the Fibonacci Heap
        Stage 1:
            Set all the minimun node children to roots
        Stage 2:
            Consolidate the heap merging all roots with equal degree
        Stage 3:
            Find the new minimum with a simple root traversal

        Raises
        ------
        AssertionError
            The heap must not be empty.

        Returns
        -------
        removed_node : Fibonacci heap node
            The minimum node of the fibonacci heap

        '''
        self.update_max_degree()

        if self.minnode == None:
            raise AssertionError("Cannot remove from an empty heap")

        removed_node = self.minnode
        self.count -= 1

        next_min = self.minnode.next

        # 1: Assign all old root children as new roots
        if self.minnode.child:
            c = self.minnode.child

            while True:
                c.parent = None
                c = c.next
                if  c == self.minnode.child:
                    break
            self.minnode.child = None
            self.minnode.addnode(c)


        # 2.1: If we have removed the last key
        if self.minnode.next == self.minnode:
            if self.count != 0:
                raise AssertionError("Heap error: Expected 0 keys, count is " + str(self.count))
            self.minnode = None
            return removed_node

        # Remove Min Node from root
        #self.minnode.remove()
        #self.minnode = next_min

        # 2.2: Merge any roots with the same degree (consolidate)
        degree_pointer = [None] * self.maxdegree
        next_root = self.minnode
        end = self.minnode.prev

        
        while True:  # Changing style to allow evaluation condition in the end
            degree = next_root.degree
            root = next_root
            next_root = next_root.next

            while degree_pointer[degree] != None:
                # Swap if required
                pointed = degree_pointer[degree]
                if root.key >  pointed.key:
                    root, pointed = pointed, root

                pointed.remove()
                root.addchild(pointed)
                degree_pointer[degree] = None
                degree += 1
                print(degree)
            degree_pointer[degree] = root
            print(degree_pointer)
            if root == end:
                    break

        print(degree_pointer)
        # 3: Remove current root and find new minnode
        self.minnode = None
        for pointed in degree_pointer:
            if pointed:
                pointed.next = pointed.previous = pointed
                self.insert(pointed, count=False)
                print(self.minnode)
                #if self.minnode == None or pointed.key < self.minnode.key:
                    #self.minnode = pointed
        return removed_node


    def decreasekey(self, node, newkey):
        '''
        Performns he decrease key function for Fibonacci Heap.

        Changes the key of the node
        If the key is lower than parent key, the node is set to root
        If parent node is marked, parent node is set to root:
                repeat until all marked parent nodes are roots or the parent is
                a root

        Parameters
        ----------
        node : Fibonacci heap node
            The node we want to decrease the key
        newkey : Integer
            The new value of the key

        Raises
        ------
        AssertionError
            New key must be lower than current key

        Returns
        -------
        None.

        '''
        if newkey > node.key:
            raise AssertionError("Cannot decrease a key to a greater value")
        elif newkey == node.key:
            return

        node.key = newkey

        parent = node.parent

        if parent == None and newkey < self.minnode.key:
            self.minnode = node
            return

        elif parent.key <= newkey:
            return

        while True: #has parent and newkey < parent.key
            parent.removechild(node)
            self.insert(node, count=False)

            if parent.parent == None:
                 break
            elif parent.mark == False:
                parent.mark = True
                break
            else:
                node = parent
                parent = node.parent
                continue




