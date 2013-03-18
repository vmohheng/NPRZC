'''
Created on Aug 12, 2012

The player. The player sprite also handles input and collision

@author: Ant
'''

import pygame, GameSprite

class Hero(GameSprite.GameSprite, pygame.sprite.Sprite):
    
    Backgroundcoll = None
    #Sets image and mask
    def __init__(self, a, b, c):
        super(Hero, self).__init__(a, b, c, 'Images\\hero.png')
        self.image.set_colorkey((255, 255, 255))
        self.mask = pygame.mask.from_surface(self.image)
        
    #Takes in keyboard input, outputs a tuple for change in real position
    def keysIn(self, keysdown):
        dx = 0
        dy = 0
        if keysdown[0]:
            dy-=3
        if keysdown[1]:
            dy+=3
        if keysdown[2]:
            dx-=3
        if keysdown[3]:
            dx+=3
        #For diagonals. Not proper
        if dx != 0 and dy != 0:
            dx = dx*0.707
            dy = dy*0.707
        #Some collision detection should go on here
        self.move(dx, dy)
        for b in self.Backgroundcoll:
            if pygame.sprite.collide_mask(self, b) != None:
                self.move(-dx, -dy)
                return (0, 0)
        self.move(-dx, -dy)
        return (dx, dy)   
        
    #Returns the difference between where player is and where player should be based on mouse position (Camera)
    def mouseMove(self, mx, my):
        scale = 0.9
        supposedx = self.screenSize[0]/2 + (self.screenSize[0]/2 - mx - self.rect.width/2)*scale
        supposedy = self.screenSize[1]/2 + (self.screenSize[1]/2 - my - self.rect.height/2)*scale
        changex = supposedx - self.rect.topleft[0]
        changey = supposedy - self.rect.topleft[1]
        return (changex, changey)
    
    #Note: Update is not changed. Game engine should handle moving the hero back into place