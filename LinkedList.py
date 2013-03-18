import pygame, sys, math
from Node import *

class LinkedList:
    
    head = None
    
    def __init__(self):
        self.head = None
    
    def add(self, data):
        newNode = Node(data, None, None)
        
        # If list is empty, make new node the head
        if self.head == None:
            self.head = newNode
        
        # Otherwise, add to front
        else:
            temp = self.head.next
            self.head = newNode
            temp.prev = newNode
            newNode.next = temp
    
    def remove(self, nodeData):
            current = self.head
            
            while (current != None):
                if (current.data) == nodeData:
                    break
                current = current.next
            
            
            # Remove current if it is non-null
            if current != None:
                
                if current == self.head:
                    self.head = current.next
                elif current.next == None:
                    current.prev = None
                else:
                    temp = current.next
                    current.prev.next = temp
                    temp.prev = current.prev
            else:
                print "Cannot find node to remove", nodeData
        
        
    
    
