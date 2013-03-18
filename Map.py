'''
Created on Aug 21, 2012

Class to process collison map. Processes B/W collision map, taking filled black areas are non-travellable (obstacles),
and creates a graph of movable grid squares on the map.

@author: Sam
'''

import pygame, sys, math, Queue
from LinkedList import *
from Vertex import *
from string import center
from maxPQ import *


class Map:
    
    collision_map = None # 3D array that stores the map, each pixel being a 3-integer array of RGB values
    tile_size = 0 # length of side of tile used for initial polygon approximation
    vertex_array = [] # 2D array that stores vertex objects representing movable grid squares
    vertex_map = {} # Dictionary of movable vertices ( vertex : center (x,y) coordinate tuple)
    
    def __init__(self, collision_map, tile_size):
        self.collision_map = pygame.surfarray.pixels3d(collision_map)
        self.tile_size = tile_size
        self._makeGrid_(collision_map, tile_size)
        
    '''
    Function: straight_line_distance
    
    Description: Helper function to calculate straight line distance between two points
    
    Inputs: Two points represented as (x,y) tuples
    Output: Straight line distance between two points
    '''
    def straight_line_distance(self, point1, point2):
        return math.sqrt(math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1], 2) )
    
    '''
    Function: makeGrid
    
    Description: Parse a collision map into a graph
    
    Inputs: A collision map (collision_map), dimension of each square tile (tile_size)
    Output: 2D array of vertex objects
    '''
    def _makeGrid_(self, collision_map, tile_size):
        
        pixelarray = pygame.surfarray.pixels3d(collision_map)
        
        # Input validation
        if pixelarray[0] is None or pixelarray[0][0] is None:
            print "Invalid map given"
            sys.exit(0)
        if len(pixelarray) % tile_size != 0 or len(pixelarray[0]) % tile_size != 0:
            print "Tile size does not perfectly divide map"
            print "Map is " + str(len(pixelarray)) + "x" + str(len(pixelarray[0]))
            sys.exit(0)
            
        map_width = len(pixelarray)
        map_height = len(pixelarray[0])
        vertices = []
        
        # Instantiate 2D vertex list
        for i in range(map_width/tile_size):
            new_list = []
            for j in range(map_height/tile_size):
                new_list.append(None)
            vertices.append(new_list)
                
        x = 0
        y = 0
        
        while x < map_width:
            while y < map_height:
                
                # Check for black pixels in a tile
                black_pixel_found = False
                for col in range(x, x + tile_size):
                    for row in range(y, y + tile_size):
                        # Black pixel found
                        if (pixelarray[col][row][0] == 0 and pixelarray[col][row][1] == 0 and pixelarray[col][row][2] == 0):
                            black_pixel_found = True
                            break
                
                # Tile contains no black pixels
                if black_pixel_found == False:
                    # Create a new vertex and add it to vertices matrix
                    tile_center_x = x + (tile_size/2)
                    tile_center_y = y + (tile_size/2)
                    center = (tile_center_x, tile_center_y)
                    newNode = Vertex(center)
                    vertices[x/tile_size][y/tile_size] = newNode
                    self.vertex_map[newNode] = (tile_center_x, tile_center_y)

                y += tile_size
            x += tile_size
            y = 0
        
        # Populate adjacency lists
        for x in range(len(vertices)):
            for y in range(len(vertices[0])):
                
                if vertices[x][y] != None:
                    node = vertices[x][y]
                    
                    # Check tile above
                    if ( (y-1) >= 0 ) and ( vertices[x][y-1] != None ):
                        node.adj_list.append(vertices[x][y-1])
                        assert(vertices[x][y-1] != None)
                    # Check tile below
                    if ( (y+1) < len(vertices[0]) ) and ( vertices[x][y+1] != None ):
                        node.adj_list.append(vertices[x][y+1])
                        assert(vertices[x][y+1] != None)
                    # Check tile on the left
                    if ( (x-1) >= 0 ) and ( vertices[x-1][y] != None ):
                        node.adj_list.append(vertices[x-1][y])
                        assert(vertices[x-1][y] != None)
                    # Check tile on the right
                    if ( (x+1) < len(vertices) ) and ( vertices[x+1][y] != None ):
                        node.adj_list.append(vertices[x+1][y])
                        assert(vertices[x+1][y] != None)
        
        self.vertex_array = vertices
        return vertices
    

    
    '''
    Function: findPath
    
    Description: Find the shortest path that does not meet any obstacles from one point on the map
    to another 
    
    Inputs: A start point (x,y tuple), an end point (x,y tuple)
    Output: List of coordinates (x,y tuples) of points to move to along the shortest path, False otherwise
    
    A* Search algorithm adopted from pseudocode on Wikipedia (http://en.wikipedia.org/wiki/A*_search_algorithm)
    '''   
    def _findPath_(self, start, end):
        
        start_vertex = self.vertex_array[start[0] / self.tile_size][start[1] / self.tile_size]
        end_vertex = self.vertex_array[end[0] / self.tile_size][end[1] / self.tile_size]
        
        # Input validation
        if start_vertex == None:
            print "Invalid starting coordinate. Cannot travel here!"
            return False
        if end_vertex == None:
            print "Invalid destination coordinate. Cannot travel here!"
            return False
        
        g_score = {} # cost for starting along best known path
        f_score = {} # cost with heuristic included
        
        closedset = set([])
        openset = maxPQ()
        came_from = {}
      
        g_score[start_vertex] = 0
        f_score[start_vertex] = g_score[start_vertex] + self.straight_line_distance(start, end)
        openset.add((-f_score[start_vertex], start_vertex)) # Open set bootstrapped with start vertex. Negative priority used for maxPQ
        
        while not openset.isEmpty():
            current = openset.extract_max()
            assert (current != None)
            if current == end_vertex:
                return self.reconstruct_path(came_from, end_vertex, start_vertex)
            
            closedset.add(current)
            for neighbor in current.adj_list:
                assert (neighbor != None)
                if neighbor in closedset:
                    continue
                tentative_g_score = g_score[current] + self.tile_size # constant distance between neighbors
                
                if (not openset.contains(neighbor)) or (tentative_g_score <= g_score[neighbor]):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.straight_line_distance(neighbor.center, end)
                    if not openset.contains(neighbor):
                        openset.add((-f_score[neighbor], neighbor))
        
        print "ERROR, A* SEARCH FAILED TO FIND GOAL!!!!!"
    
    def reconstruct_path(self, came_from, current_vertex, start_vertex):
        path = []
        current = current_vertex
        while current != start_vertex:
            path.insert(0, current.center)
            current = came_from[current]
        return path
        
    
    '''
    Function: checkStraightPath
    
    Given a start and end point, checks if the straight line going from the start to end point
    crosses only movable tiles
    
    Input: A start point, an end point (both represented as (x,y) tuples)
    Output: True if all tiles along straight line are movable, False otherwise
    '''
    def checkStraightPath(self, start, end):
        
        start_vertex = self.vertex_array[start[0] / self.tile_size][start[1] / self.tile_size]
        end_vertex = self.vertex_array[end[0] / self.tile_size][end[1] / self.tile_size]
        
        if start_vertex == None or end_vertex == None:
            return False
        
        gradient = float( ( float(end[1]) - float(start[1]) ) / ( float(end[0]) - float(start[0]) ) ) # dy/dx
        
        current_vertex = start_vertex
        current_x = start[0]
        current_y = start[1]
        
        # TO BE COMPLETED: NEED TO FIGURE OUT HOW TO MOVE ALONG THE LINE (ALGEBRA)
        while current_vertex != end_vertex:
            current_x += self.tile_size
            current_y += self.tile_size 
    
    '''
    Function: fitToGrid
    
    Description: Parse a collision map into a list of adjacent tiles that contain the collision boundaries.
    Collision map must be at least 1x1 pixels and tile size must perfectly divide both the width and height of map
    Collision pixels must be in black, and rest of map must be non-black
    
    Inputs: A collision map (collision_map), dimension of each square tile (tile_size)
    Output: List of top left coordinates of tiles containing the collision boundaries
    '''
    def _fitToGrid_(self, collision_map, tile_size):
        
        pixelarray = pygame.surfarray.pixels3d(collision_map)
        
        # Input validation
        if pixelarray[0] is None or pixelarray[0][0] is None:
            print "Invalid map given"
            sys.exit(0)
        if len(pixelarray) % tile_size != 0 or len(pixelarray[0]) % tile_size != 0:
            print "Tile size does not perfectly divide map"
            print "Map is " + str(len(pixelarray)) + "x" + str(len(pixelarray[0]))
            sys.exit(0)
        
        map_width = len(pixelarray)
        map_height = len(pixelarray[0])
        boundary_tile_list = []
        
        # Loop through each tile and store top-left x,y coordinates in list
        # if it contains any black pixels
        x = 0
        y = 0
        move_to_next_tile = False
    
        while x < map_width:
            while y < map_height:
                for col in range(x, x + tile_size):
                    for row in range(y, y + tile_size):
                        if pixelarray[col][row][0] == 0 and pixelarray[col][row][1] == 0 and pixelarray[col][row][2] == 0:
                            boundary_tile_list.append([x, y])
                            move_to_next_tile = True
                            #print "Black pixel found in tile" + str((x,y))
                            break
                    if move_to_next_tile is True:
                        move_to_next_tile = False
                        break
                y += tile_size
            x += tile_size
            y = 0
        
        #print boundary_tile_list
        print 'fitToGrid: Returning...'
        return boundary_tile_list

    '''
    Function: extractEdges
    
    Description: Detect the interior edges of adjacent tiles tiles and return a list of
    polygons representing the edges of these adjacent tiles. The inner edge of the outermost
    polygon will be detected and the outer edge of the other polygons it contains will be detected.
    
    IMPORTANT NOTE: Assumes that the tile size and collision mapping is such that tiles that bound a
    continuous collision boundary will not be adjacent to tiles bounding any other collision boundary
    
    Inputs: A list of top-left x,y tile coordinates (tile_list), the dimensions of a tile (tile_size),
    and an optional input for the degree of simplification to apply to the edges of the final polygons
    Output: List of lists of polygons, each polygon being a 2D list of x,y point coordinates ordered by adjacency
    '''
    def _extractEdges_(self, tile_list, tile_size, edge_simplify=4):
        
        # edges will be simplified according to edge_simplify (i.e. connect each edge to the edge (n-1)-edges away from it)
        
        # First, sort adjacent tiles into lists
        adjacent_tiles = []
        current_polygon = -1
        while len(tile_list) > 0:
            
            # If possible, find a tile with only one other tile adjacent to it (for boundaries whose end points do not connect)
            next_head = 0
            current_tile = 0
            head_found = False
            while next_head < len(tile_list):
                head_found = False
                current_tile = 0
                while current_tile < len(tile_list):
                    found_first_adjacent_tile = False
                    if current_tile != next_head:
                        if self._tilesAreAdjacent_(tile_list[next_head], tile_list[current_tile], tile_size) != 0:
                            found_first_adjacent_tile = True
                            current_tile2 = 0
                            while current_tile2 < len(tile_list):
                                if current_tile2 != current_tile and current_tile2 != next_head:
                                    if self._tilesAreAdjacent_(tile_list[next_head], tile_list[current_tile2], tile_size) != 0:
                                        break
                                current_tile2 += 1
                            # If we ran off the list, we have found a tile with only one other tile adjacent to it
                            if current_tile2 >= len(tile_list):
                                head_found = True
                    
                    if found_first_adjacent_tile is True:
                        break
                    else:
                        current_tile += 1
                if head_found is True:
                    break
                else:
                    next_head += 1
                        
            if head_found is False:
                next_head = 0
            
            # Now take the next head and find all tiles continuously adjacent to it
            find_next_adjacent_tile = False
            adjacent_tiles.append([])
            current_polygon += 1
            adjacent_tiles[current_polygon].append(tile_list[next_head])
            tile_list.pop(next_head)
            current_tile = 0
            while True:
                for tile in tile_list:
                    # If an adjacent tile is found, remove it from tile_list, append it to the current polygon list and search for the next tile adjacent to it
                    if self._tilesAreAdjacent_(adjacent_tiles[current_polygon][current_tile], tile, tile_size) != 0:
                        
                        # If the tiles are diagonally adjacent, check if there is a NSEW adjacent tile instead
                        if self._tilesAreAdjacent_(adjacent_tiles[current_polygon][current_tile], tile, tile_size) > 4:
                            for tile2 in tile_list:
                                if not (tile2[0] == tile[0] and tile2[1] == tile[1]):
                                    if self._tilesAreAdjacent_(adjacent_tiles[current_polygon][current_tile], tile2, tile_size) < 5 and \
                                    self._tilesAreAdjacent_(adjacent_tiles[current_polygon][current_tile], tile2, tile_size) != 0:
                                        tile = tile2
                                        break
                        
                        tile_list.remove(tile)
                        adjacent_tiles[current_polygon].append(tile)
                        current_tile += 1
                        find_next_adjacent_tile = True
                        break
                # If an adjacent tile can no longer be found, we have already found a complete polygon. Find next complete polygon
                if find_next_adjacent_tile is True:
                    find_next_adjacent_tile = False
                else:
                    break
            
        

        
        # Walk through each list of adjacent tiles and extract list of points representing its perimeter
        list_of_edge_lists = []
        tile_list_number = -1
        for tile_list in adjacent_tiles:
            list_of_edge_lists.append([])
            tile_list_number += 1
            list_of_edge_lists[tile_list_number].append(tile_list[0])
            tile_number = 0
            
            while tile_number < (len(tile_list) - 1):
                adjacency = self._tilesAreAdjacent_(tile_list[tile_number + 1], tile_list[tile_number], tile_size)
                # If the next tile is N, E, S or W of the first tile, next point is its top left corner
                if adjacency == 1 or adjacency == 2 or adjacency == 3 or adjacency == 4:
                    list_of_edge_lists[tile_list_number].append(tile_list[tile_number + 1])
                # If the next tile is NE or SE of the first tile, append first tile's top right corner and next tile's top left corner
                elif adjacency == 6 or adjacency == 7:
                    list_of_edge_lists[tile_list_number].append([tile_list[tile_number][0] + tile_size, tile_list[tile_number][1]])
                    list_of_edge_lists[tile_list_number].append(tile_list[tile_number + 1])
                # If the next tile is SW of the first tile, append first tile's bottom left corner and next tile's top left corner
                elif adjacency == 8:
                    list_of_edge_lists[tile_list_number].append([tile_list[tile_number][0], tile_list[tile_number][1] + tile_size])
                    list_of_edge_lists[tile_list_number].append(tile_list[tile_number + 1])
                # If the next tile is NW of the first tile, append second tile's top right corner and next tile's top left corner
                elif adjacency == 5:
                    list_of_edge_lists[tile_list_number].append([tile_list[tile_number + 1][0] + tile_size, tile_list[tile_number][1]])
                    list_of_edge_lists[tile_list_number].append(tile_list[tile_number + 1])
                    
                tile_number += 1
            
            # For a non-singleton list, join first and last tiles
            #if tile_number != 0:   
                #if self._tilesAreAdjacent_(tile_list[tile_number], tile_list[0], tile_size):
                #list_of_edge_lists[tile_list_number].append(tile_list[0])
                    

        # Simplify Edges
        if edge_simplify > 2:
            for edge_list in list_of_edge_lists:
                current_edge = 0
                while current_edge < (len(edge_list) - (edge_simplify - 2)):
                    for i in range(edge_simplify - 2):
                        edge_list.pop(current_edge+1)
                    current_edge += 1
        
        # Join ends
        for edge_list in list_of_edge_lists:
            if len(edge_list) != 1:
#                if self._tilesAreAdjacent_(edge_list[0], edge_list[len(edge_list)-1], tile_size):
                edge_list.append(edge_list[0])
        
        return list_of_edge_lists
        #return adjacent_tiles

    '''
    Function: createPolygon
    
    Description: Creates a single polygon from a list of polygons
    Assumes that the first polygon in the list is the outermost polygon, that
    all other polygons are combined in it, but that none contain another, and
    that all polygons are closed (i.e. first and last points adjacent)
    
    Inputs: A list of lists of points representing polygons
    Output: A single list of points representing a polygon (this represents walkable space in the map
    '''
    def _createPolygon_(self, list_of_polygons):
        
        # Boot-strapping
        polygon = list(list_of_polygons[0])
        
        current_interior_polygon = 1
        prv_splice_inner = list([0,0]) # saves splice point of previous loop
        prv_splice_outer = list([0,0])
        while current_interior_polygon < len(list_of_polygons):
            #print "Current interior polygon:", current_interior_polygon
            #print "Polygon:", polygon
            
            # Find splice point
            #print "Finding splice point"
            min_distance = sys.maxint
            splice_point_outer = list([0,0])
            splice_point_inner = list([0,0])
            for point1 in polygon:
                for point2 in list_of_polygons[current_interior_polygon]:
                    distance_between_points = math.sqrt(math.pow(math.fabs(point1[0]-point2[0]),2)+math.pow(math.fabs(point1[1]-point2[1]),2))
                    
                    # Added second condition to prevent either splice point from previous loop iteration (i.e. a point repeated within a list) from being
                    # chosen. This ensures that the current_point_counter later will be assigned a unique point in the list
                    if (distance_between_points < min_distance) and not (point1[0] == prv_splice_outer[0] and point1[1] == prv_splice_outer[1]) \
                    and not (point1[0] == prv_splice_inner[0] and point1[1] == prv_splice_inner[1]):
                        min_distance = distance_between_points
                        splice_point_outer = point1
                        splice_point_inner = point2
                        
            
            #print "Splice point outer:", splice_point_outer
            #print "Splice point inner:", splice_point_inner
                
            # Form new polygon
            #print "Forming new polygon"
            new_polygon = list([])
            new_polygon.append(splice_point_outer)
            current_point_counter = polygon.index(splice_point_outer)
            current_point = polygon[current_point_counter+1] # Start one point after the splice point
            
            #print "New polygon before outer walk:", new_polygon
            
            # First, walk around outer polygon starting from and ending at splice point
            #print "Walking around outer polygon"
            while not (current_point[0] == splice_point_outer[0] and current_point[1] == splice_point_outer[1]):
                new_polygon.append(current_point)
                current_point_counter += 1
                #print "Current point:", current_point
                #print "Splice point outer:", splice_point_outer
                if current_point_counter >= len(polygon):
                    current_point_counter = 0 # wrap if we hit the end of the list
                current_point = polygon[current_point_counter]
            
            #print "New polygon after outer walk:", new_polygon
            
            # Next, walk along splice line, around the inner polygon, and back along the splice line to complete polygon
            #print "Walking around inner polygon"
            new_polygon.append(splice_point_outer)
            new_polygon.append(splice_point_inner)
            current_point_counter = list_of_polygons[current_interior_polygon].index(splice_point_inner)
            current_point = list_of_polygons[current_interior_polygon][current_point_counter + 1]
            while not (current_point[0] == splice_point_inner[0] and current_point[1] == splice_point_inner[1]):
                new_polygon.append(current_point)
                current_point_counter += 1
                if current_point_counter >= len(list_of_polygons[current_interior_polygon]):
                    current_point_counter = 0 # wrap if we hit the end of the list
                current_point = list_of_polygons[current_interior_polygon][current_point_counter]
            new_polygon.append(splice_point_inner)
            new_polygon.append(splice_point_outer)
            
            #print "New polygon after inner walk:", new_polygon
            
            #print "Copying polygon over and ending loop iteration"
            polygon = list(new_polygon)
            prv_splice_inner = splice_point_inner
            prv_splice_outer = splice_point_outer
            current_interior_polygon += 1
            
        
        #print "LOOP BROKEN"
        return polygon
    
    '''
    Function: createVisibilityGraph
    
    Description: Creates a visibility graph from a polygon
    
    Inputs: list of points representing a closed polygon
    Output: A triple, comprising a list of points (vertices), a list of linked lists (adj list),
    and a dictionary (weight function)
    '''
    def createVisibilityGraph(self, polygon):
        
        vertices = []
        adjList = []
        weights = {}
        polygon_edges = []
        
        # Create list of polygon edges
        current = 0
        while current < (len(polygon)-1):
            polygon_edges.append((polygon[current],polygon[current+1]))
            current += 1
        
        # Instantiate adj list and vertices list
        pointCount = 0
        while pointCount < (len(polygon) - 1):
            vertices.append(polygon[pointCount])
            newLL = LinkedList()
            adjList.append(newLL)
            pointCount += 1
        
        pointCount = 0
        while pointCount < (len(polygon) - 1):
            point1 = polygon[pointCount]
            for point2 in polygon:
                if point2 != point1:
                    
                    # Check if this is an internal edge
                    count = 0
                    
                    for edge in polygon_edges:
                        if ((point1,point2) != edge) and ((point2, point1) != edge):
                            if self.line_seg_intersect(point1, point2, edge[1], edge[2]) != 0:
                                count += 1
                        
                        # If intersections are odd, we have an internal edge    
                        if count % 2 != 0:
                            adjList[pointCount].add(point2) # add to adajcency list
                            straight_line_distance = math.sqrt(math.pow(math.fabs(point1[0]-point2[0]),2)+ math.pow(math.fabs(point1[1]-point2[1]),2))
                            weights[(point1,point2)] = straight_line_distance # add weight
                        
                pointCount += 1
                
    
    def convexPartition(self, polygon, number_of_splits):
        print "Call made to convex Partition:", number_of_splits
        
        # Base case: stop partitioning after a number of iterations initially specified
        if number_of_splits == 0:
            return [polygon]
        
        line_extension = 10000 # amount of extend line by for inside polygon check
        
        smallest_metric = sys.maxint # metric to minimize, (straight line distance) / (perimeter distance)
        splice_point1 = None
        splice_point2 = None
        point1 = 0
        while point1 < len(polygon):
            point2 = 0
            while point2 < len(polygon):
                # Look for non-identical points that do not exist on the same dimension
                if (not (polygon[point2][0] == polygon[point1][0] and polygon[point2][1] == polygon[point1][1])) and (polygon[point2][0] != polygon[point1][0] or polygon[point2][1] != polygon[point1][1]):
                    midpoint = [((polygon[point1][0]+polygon[point2][0])/2),((polygon[point1][1]+polygon[point2][1])/2)]
                    
                    # Determine if midpoint of this line segment is within the polygon (i.e. if line is within polygon
                    vertex = 0
                    intersection_count = 0
                    while vertex < (len(polygon) - 1):
                        if self.line_seg_intersect(midpoint, [midpoint[0],(midpoint[1]+line_extension)], polygon[vertex], polygon[vertex+1]) != 0:
                            intersection_count += 1
                        vertex += 1
                        
                    #print "Number of intersections:", intersection_count
                    
                    # If line segment is within the polygon, calculate metric
                    if intersection_count % 2 != 0:
                        straight_line_distance = math.sqrt(math.pow(math.fabs(polygon[point1][0]-polygon[point2][0]),2)+math.pow(math.fabs(polygon[point1][1]-polygon[point2][1]),2))
                        
                        # Calculate perimeter of segment
                        current_point = point1
                        perimeter = 0
                        while current_point != point2:
                            perimeter += 1
                            if (current_point + 1) >= len(polygon):
                                current_point = 0
                            else:
                                current_point += 1
                                
                        metric = float(straight_line_distance) / float(perimeter)
                        #print "Metric:", metric
                        if metric < smallest_metric:
                            smallest_metric = metric
                            splice_point1 = point1
                            splice_point2 = point2
                        
                point2 += 1
            point1 += 1
        
        print "Point 1: " + str(splice_point1) + " " + str(polygon[splice_point1])
        print "Point 2: " + str(splice_point2) + " " + str(polygon[splice_point2])
        
        splice_point1 = 30
        splice_point2 = 75
        
        # Split polygon into two
        polygon1 = []
        curr_point = splice_point1
        while curr_point != splice_point2:
            polygon1.append(list(polygon[curr_point]))
            if (curr_point + 1) >= len(polygon):
                curr_point = 0
            else:
                curr_point += 1
        polygon1.append(list(polygon[splice_point2]))
        polygon1.append(list(polygon[splice_point1]))
        
        print "Polygon 1:", polygon1
        
        polygon2 = []
        curr_point = splice_point1
        while curr_point != splice_point2:
            polygon2.append(list(polygon[curr_point]))
            if (curr_point - 1) < 0:
                curr_point = len(polygon) - 1
            else:
                curr_point -= 1
        polygon2.append(list(polygon[splice_point2]))
        polygon2.append(list(polygon[splice_point1]))
        
        print "Polygon 2:", polygon2
        
        # Recursive calls
        split_polygons1 = self.convexPartition(polygon1, (number_of_splits - 1))
        split_polygons2 = self.convexPartition(polygon2, (number_of_splits - 1))
        
        polygon_list = []
        for polygon in split_polygons1:
            polygon_list.append(polygon)
        for polygon in split_polygons2:
            polygon_list.append(polygon)
            
        return polygon_list
                    

    
    
    '''
    Function: tilesAreAdjacent
    
    Description: Determines if two tiles are adjacent
    
    Inputs: The top-left x,y coordinates of two tiles (as arrays), tile dimension
    Output: 1-4 if the two tiles are adjacent NESW, 5-8 if two tiles are adjacent diagonally, 0 otherwise
    '''
    def _tilesAreAdjacent_(self, tile1, tile2, tile_size):
        
        # Tile 1 is W of Tile 2
        if (tile1[0] + tile_size == tile2[0] and tile1[1] == tile2[1]):
            return 4
        # Tile 1 is N of Tile 2
        elif (tile1[0] == tile2[0] and tile1[1] + tile_size == tile2[1]):
            return 1
        # Tile 1 is E of Tile 2
        elif (tile1[0] - tile_size == tile2[0] and tile2[1] == tile1[1]):
            return 2
        # Tile 1 is S of Tile 2
        elif (tile2[0] == tile1[0] and tile1[1] - tile_size == tile2[1]):
            return 3
        # Tile 1 is NW of Tile 2
        elif (tile1[0] + tile_size == tile2[0] and tile1[1] + tile_size == tile2[1]):
            return 5
        # Tile 1 is NE of Tile 2
        elif (tile1[0] - tile_size == tile2[0] and tile1[1] + tile_size == tile2[1]):
            return 6
        # Tile 1 is SW of Tile 2
        elif (tile1[0] + tile_size == tile2[0] and tile1[1] - tile_size == tile2[1]):
            return 8
        # Tile 1 is SE of Tile 2
        elif (tile1[0] - tile_size == tile2[0] and tile1[1] - tile_size == tile2[1]):
            return 7
        else:
            return 0
        
        
    
    ########################################
    # HELPER METHODS FOR LINE INTERSECTION #
    ########################################
    
    def have_same_signs(self, a, b):
        return ((a ^ b) >= 0)
    
    
    
    def line_seg_intersect(self, line1point1, line1point2, line2point1, line2point2):
        # Constants for line-segment tests
        DONT_INTERSECT = 0
        COLINEAR = 0
        
        x1 = line1point1[0]
        y1 = line1point1[1]
        x2 = line1point2[0]
        y2 = line1point2[1]
        x3 = line2point1[0]
        y3 = line2point1[1]
        x4 = line2point2[0]
        y4 = line2point2[1]
    
        a1 = y2 - y1  
        b1 = x1 - x2  
        c1 = (x2 * y1) - (x1 * y2)
    
        r3 = (a1 * x3) + (b1 * y3) + c1  
        r4 = (a1 * x4) + (b1 * y4) + c1
    
        if ((r3 != 0) and (r4 != 0) and self.have_same_signs(r3, r4)):
            return(DONT_INTERSECT)
    
        a2 = y4 - y3  
        b2 = x3 - x4  
        c2 = x4 * y3 - x3 * y4
    
        r1 = a2 * x1 + b2 * y1 + c2  
        r2 = a2 * x2 + b2 * y2 + c2
    
        if ((r1 != 0) and (r2 != 0) and self.have_same_signs(r1, r2)):
            return(DONT_INTERSECT)
    
        denom = (a1 * b2) - (a2 * b1)  
        if denom == 0:  
            return(COLINEAR)
        elif denom < 0:
            offset = (-1 * denom / 2)
        else:
            offset = denom / 2
        
        num = (b1 * c2) - (b2 * c1)
        if num < 0:
            x = (num - offset) / denom
        else:
            x = (num + offset) / denom
    
        num = (a2 * c1) - (a1 * c2)  
        if num <0:
            y = (num - offset) / denom
        else:
            y = (num - offset) / denom
    
        return (x, y)