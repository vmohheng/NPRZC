import pygame, sys, math

class PolygonGraph:
    
    adj_matrix = None # Adjacency matrix to store edges
    
    def __init__(self):
        adj_matrix = []
    
    #def addNode(self, polygon_node):
        
    
    
    class PolygonNode:
        
        point_list = None # List of points representing the polygon
        
        def _init_(self, point_list):
            self.point_list = point_list