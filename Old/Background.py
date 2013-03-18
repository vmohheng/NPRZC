'''
Created on Aug 12, 2012

Background sprite. Turns itself on and off

@author: Ant
'''
import pygame, GameSprite

class Background(GameSprite.GameSprite, pygame.sprite.Sprite):
    
    nullmage = pygame.image.load('Images\\hero.png') #Default singleton null image
    isOn = False #Whether this guy is on screen
    bgroup = None #The background group it belongs to
    imagename = None #Original image name
    
    def __init__(self, a, b, c, fname, mname, bgroup):
        super(Background, self).__init__(a, b, c, fname)
        self.imagename = fname
        self.image = self.nullmage
        self.bgroup = bgroup
        tempimg = pygame.image.load(mname).convert()
        tempimg.set_colorkey((255, 255, 255))
        self.mask = pygame.mask.from_surface(tempimg)
        
    def turnOn(self):
        if self.isOn is False:
            self.isOn = True
            self.image = pygame.image.load(self.imagename).convert()
            self.bgroup.add(self)
        
    def turnOff(self):
        if self.isOn is True:
            self.isOn = False
            self.image = Background.nullmage
            self.bgroup.remove(self)

    #Updates and turns on and off
    def update(self, current_time, dx = 0, dy = 0):
        self.moveScreen(dx, dy)
        if self.onScreen() and self.isOn is False:
            self.turnOn()
        elif self.onScreen() is False and self.isOn is True:
            self.turnOff()