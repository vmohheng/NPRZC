'''
Created on Aug 24, 2012

A Test enemy

@author: Ant
'''

import pygame, GameSprite, math


class Enemy(GameSprite.GameSprite, pygame.sprite.Sprite):
    
    weapon = None
    mask = None
    animationPlayed = False
    enemies = None
    fireX = 350
    fireY = 350
    DX = 3
    DY = 3
    
    # Sets image and mask
    def __init__(self, initial_position, screen_position):
        self.XP = 1
        # Load animations
        animationList = []
        animationList.append(self.loadAnimation('Images\\herodie0.png', 3))
        super(Enemy, self).__init__(initial_position, screen_position, 'Images\\hero.png', animationList)
        self.image.set_colorkey((255, 255, 255))
        self.mask = pygame.mask.from_surface(self.image)
        
        #Character attributes
        self.HP = 10
        self.dmgmultiplier = 1.0
        self.accuracymultiplier = 1.0
        self.shieldregenrate = 100
        self.shieldregendelay = 3000
        self.shieldregentime = 0
        self.shields = 10
        self.maxshields = 10
        self.rofmultiplier = 1.0
        self.bulletspeedmultiplier = 1.0
        self.maxbulletspeedmultiplier = 1.0
        self.burstmultiplier = 1.0
        self.clipmultiplier = 1.0
        self.takeDMG = False
    

    def updateWeapon(self, mouseX, mouseY, current_time):
        #Weaponpos determines the position of the weapon on the screen (with offset)
        weaponpos = self.weapon.rect.topleft 
        weaponpos = (weaponpos[0]+self.weapon.rect.width/2, weaponpos[1]+self.weapon.rect.height/2)
        #Now position for offset
        #weaponpos = ((weaponpos[0] + self.weapon.bulletoffset*math.cos(math.radians(-self.weapon.facing-90))),(weaponpos[1] + self.weapon.bulletoffset*math.sin(math.radians(-self.weapon.facing-90))))
        angle = self.findAngle((mouseX, mouseY),(weaponpos))
        # Update the weapon state
        self.weapon.update(angle, current_time, False)
        
    def doDmg(self, damage):
        if self.shields <= 0:
            super(Enemy, self).doDmg(damage)        
        if self.shields >= 0:
            self.shields = self.shields - damage
            self.takeDMG = True
        if self.shields < 0:
            self.shields = 0
    
    def die(self):
        GameSprite.weapons.remove(self.weapon)
        super(Enemy, self).die()

    #Note: Update is not changed. Game engine should handle moving the hero back into place
    def update(self, current_time, dx = 0, dy = 0):
        
        if current_time > 2000 and self.animationPlayed is False:
            self.playAnimation(0,1000, False, True, False)
            self.animationPlayed = True
        
        super(Enemy, self).update(current_time, dx,dy)
        self.updateWeapon(self.fireX, self.fireY, current_time)
        
        if self.takeDMG is True:
            self.shieldregentime = current_time + self.shieldregendelay
            self.takeDMG = False
        if current_time > self.shieldregentime:
            if self.shields < self.maxshields:
                self.shieldregentime = current_time+self.shieldregenrate
                self.shields = self.shields + 1