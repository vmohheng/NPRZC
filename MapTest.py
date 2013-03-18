'''
TEST HARNESS FOR MAP.PY

@author: Sam
'''

import pygame, sys, time, Map
from pygame.locals import *
from GameSprite import *
from Hero import *
from Background import *
from Weapon import *
from random import randint
from time import sleep

#Define initial stuff
BgColor = (128, 128, 128) #Background color
screenSize = 650, 650 #Size of screen, obviously
screenPos = 0, 0 #Top-left corner of our screen in real coordinates
FPS = 60 #Frames per second


#Run initial processes
fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode(screenSize)
screen.fill((255,255,255))
pygame.init()

IMAGE = 'Images//maptest2.bmp'
tile_size = 10

image = pygame.image.load(IMAGE).convert()
image.set_colorkey((255, 255, 255))
test = Map.Map(image, tile_size)

vertices = test._makeGrid_(image, tile_size)



'''
pixels = test._fitToGrid_(image, tile_size) # NOT BEING RETURNED. WHY????
list_of_edge_lists = test._extractEdges_(pixels, tile_size)
#pixels2 = test._extractEdges_(pixels, tile_size)
#polygon = test._createPolygon_(list_of_edge_lists)
#split_polygons = test.convexPartition(polygon, 1)
#print "DONE!!!"

#for edge_list in list_of_edge_lists:
    #print edge_list
    #pygame.draw.lines(screen, (0,0,0), False, edge_list)

'''

#pygame.draw.polygon(screen, (0,0,0), polygon, 1)
#for pixel in pixels:
#    pygame.draw.rect(screen, (0,0,0), (pixel[0], pixel[1], tile_size, tile_size), 1)

pixel_list_counter = 0
COLOR = (0,0,0)
clicked_once = False
first_click = (0,0)
while True:
    # Control handling
    for e in pygame.event.get():
        if e.type == QUIT:
            pygame.quit()
            sys.exit()
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if clicked_once == False:
                clicked_once = True
                first_click = pygame.mouse.get_pos()
            else:
                path = test._findPath_(vertices, tile_size, first_click, pygame.mouse.get_pos())
                if path != False:
                    pygame.draw.lines(screen, (255,0,0), False, path, 5)
                clicked_once = False
            
    for vertex_list in vertices:
        for vertex in vertex_list:
            if vertex != None:
                pygame.draw.rect(screen, (0,0,0), pygame.Rect(vertex.center[0] - (tile_size/2), vertex.center[1] - (tile_size/2), tile_size, tile_size), 1)
    


    '''
    sleep(0.5)
    start_point = (randint(1,649), randint(1,649))
    end_point = (randint(1,649), randint(1,649))
    print "Start:", start_point
    print "End:", end_point
    path = test._findPath_(vertices, tile_size, start_point, end_point)
    if path != False:
        pygame.draw.lines(screen, (randint(0,255),randint(0,255),randint(0,255)), False, path, 5)
    '''
    pygame.display.update()
    fpsClock.tick(FPS)
'''
    for pixel in pixels:
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(pixel[0], pixel[1], tile_size, tile_size), 1)
''' 
