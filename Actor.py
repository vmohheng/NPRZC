'''
Created on Aug 24, 2012

An actor is a sprite with a Weapon. It's for Hero, Enemies, and allies perhaps

@author: Ant
'''
import pygame, GameSprite, math

class Actor(GameSprite.GameSprite, pygame.sprite.Sprite):
    
    Backgroundcoll = None
    screen_size = None
    
    # Sets image and mask
    def __init__(self, initial_position, screen_position):
        self.weapon = None
        self.mask = None
        self.enemies = None
        # Load animations
        animationList = []
        animationList.append(self.loadAnimation('Images\\herodie0.png', 3))
        
        super(Actor, self).__init__(initial_position, self.screen_size, screen_position, 'Images\\hero.png', animationList)
        self.image.set_colorkey((255, 255, 255))
        self.mask = pygame.mask.from_surface(self.image)
        
        #Now for a LONG LIST OF STATS
        self.HP = 100
        self.maxHP = 100
        self.shields = 3
        self.maxshields = 3
        self.XP = 0
        self.dmgmodifier = 1.0
        self.accuracymodifier = 1.0
