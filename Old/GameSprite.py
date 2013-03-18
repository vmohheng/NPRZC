'''
Created on Aug 12, 2012

GameSprite is a general class which holds methods and values that the a sprite in the game should have
All Sprites should extend from this

@author: Ant
'''

import pygame

class GameSprite(pygame.sprite.Sprite):
    
    image = None
    realPos = [0, 0] #The real position in terms of in game coordinates
    screenSize = [0, 0] #The dimensions of the screen
    rect = None #The rectangle. rect.topleft gets the coordinates on the screen
    next_update_time = 0 #If we want to update only at a certain time
    update_interval = 10 #Milliseconds between updates. Note, only updates between frames, so might stutter.
    
    #Takes in real game coordinates, screen dimension, and top-left coordinate of camera, and image path
    def __init__(self, initial_position, screen_size, screen_position, image_in = None):
        pygame.sprite.Sprite.__init__(self)
        if image_in != None:
            self.image = pygame.image.load(image_in).convert()
            self.rect = self.image.get_rect()
            self.rect.topleft = (initial_position[0] - screen_position[0], initial_position[1] - screen_position[1])
        self.realPos = initial_position
        self.screenSize = screen_size
        
    #Checks if even a portion of the Sprite is on the screen, after x and y offset
    def onScreen(self, x=0, y=0):
        if self.rect.topleft[0]+x + self.rect.width < 0:
            return False
        if self.rect.topleft[1]+y + self.rect.height < 0:
            return False
        if self.rect.topleft[0]+x > self.screenSize[0]:
            return False
        if self.rect.topleft[1]+y > self.screenSize[1]:
            return False
        return True
    
    #Checks if the entire Sprite is on the screen, after x and y offset
    def withinScreen(self, x=0, y=0):
        if self.rect.topleft[0]+x - self.rect.width < 0:
            return False
        if self.rect.topleft[1]+y - self.rect.height< 0:
            return False
        if self.rect.topleft[0]+x + self.rect.width > self.screenSize[0]:
            return False
        if self.rect.topleft[1]+y + self.rect.height > self.screenSize[1]:
            return False
        return True
    
    #Moves the sprite by x and y, both in game and on screen
    def move(self, x, y):
        self.rect = self.rect.move(x, y)
        self.realPos = (self.realPos[0] + x, self.realPos[1] + y)
        
    #Moves the sprite only on the screen, without changing in-game position
    def moveScreen(self, x, y):
        self.rect = self.rect.move((x, y))
        
    #The default update simply moves by the given parameter 
    def update(self, current_time, dx = 0, dy = 0):
        self.moveScreen(dx, dy)
        if self.next_update_time < current_time:
            self.next_update_time = current_time + self.update_interval
