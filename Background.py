'''
Created on Aug 12, 2012

Background sprite. Turns itself on and off

@author: Ant
'''
import pygame, GameSprite

class Background(GameSprite.GameSprite, pygame.sprite.Sprite):
    
    nullimage = pygame.image.load('Images\\hero.png') #Default singleton null image
    isOn = False #Whether this guy is on screen
    bgroup = None #The background group it belongs to
    imagename = None #Original image name
    mask = None #Mask for background
    
    def __init__(self, initial_position, screen_position, fname, mname):
        super(Background, self).__init__(initial_position, screen_position, fname)
        self.imagename = fname
        self.image = self.nullimage
        tempimg = pygame.image.load(mname).convert()
        tempimg.set_colorkey((255, 255, 255))
        self.mask = pygame.mask.from_surface(tempimg)
        self.HP = 3000000
        
    def turnOn(self):
        if self.isOn is False:
            self.isOn = True
            self.image = pygame.image.load(self.imagename).convert()
            GameSprite.BG.add(self)
        
    def turnOff(self):
        if self.isOn is True:
            self.isOn = False
            self.image = Background.nullimage
            GameSprite.BG.remove(self)

    #Updates and turns on and off
    def update(self, current_time, dx = 0, dy = 0):
        super(Background, self).update(current_time, dx,dy)
        self.HP = 30000000
        if self.onScreen() and self.isOn is False:
            self.turnOn()
        elif self.onScreen() is False and self.isOn is True:
            self.turnOff()