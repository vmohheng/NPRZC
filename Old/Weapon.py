'''
Created on Aug 12, 2012

Contains classes for Weapons and Bullets. A Weapon fires a bullet. A bullet is an actual sprite.

@author: Ant
'''

import pygame, sys, math, GameSprite

class Bullet(GameSprite.GameSprite, pygame.sprite.Sprite):
    
    dx = 0.0
    dy = 0.0
    xaccel = 0.0
    yaccel = 0.0 
    maxspeed = 0.0
    reachedmax = False
    DeathTime = 100
    Tick = 0
    xcap = 0.0 #Capacitators. Stores the remainder.
    ycap = 0.0
    bulletgroup = None
    bgcoll = None
    #Sets image and mask
    def __init__(self, a, b, c):
        super(Bullet, self).__init__(a, b, c)
        
    def update(self, current_time, dx = 0, dy = 0):
        super(Bullet, self).update(current_time, dx, dy) #Move for the screen
        
        #Account for lack of rounding
        if self.dx > 0:
            self.xcap = (self.xcap + self.dx)%1
        else:
            self.xcap = (self.xcap + self.dx)%-1
        if self.dy > 0:
            self.ycap = (self.ycap + self.dy)%1
        else:
            self.ycap = (self.ycap + self.dy)%-1
            
        self.move(self.dx+self.xcap, self.dy+self.ycap) #Move real position due to velocity

        if self.reachedmax is False and self.maxspeed > self.magnitude(self.dx, self.dy):
            self.dx = self.dx + self.xaccel
            self.dy = self.dy + self.yaccel
        else:
            self.reachedmax = True
        self.Tick = self.Tick + 1
        #print(self.Tick)
        if self.Tick >= self.DeathTime:
            self.kill()

        for b in self.bgcoll:
            if pygame.sprite.collide_mask(self, b) != None:
                self.kill()
    
    def magnitude(self, x, y):
        return math.sqrt(x*x + y*y)
        
#This is a basic weapon. Meant to be abstracted to provide for a larger weapon class
class BasicWeapon:
    weaponimage = None
    screenSize = None
    screenPos = None
    bulletgroup = None
    allgroup = None
    bgcoll = None
    radius = 1
    def __init__(self):
        if self.weaponimage is None:
            BasicWeapon.weaponimage = pygame.image.load('Images\\bullety.png').convert()
            BasicWeapon.weaponimage.set_colorkey((255, 255, 255))
        else:
            self.weaponimage = BasicWeapon.weaponimage
        self.image = self.weaponimage
        
        self.speed = 6.5
        self.recoil = 5.0
        self.refire = 500
        self.burstrate = 10
        self.burstnum = 3
        self.source = 0, 0
        self.accel = 0.01
        self.maxspeed = 10.0
        self.DeathTime = 150
        self.radius = 2
    
    #Note that angle is IN RADIANS
    #By default, the angle is calculated from the x axis, not north
    def makebullet(self, angle):
        newbullet = Bullet(self.source, self.screenSize, self.screenPos)
        newbullet.image = BasicWeapon.weaponimage
        #newbullet.image = pygame.image.load('Images\\testx.png').convert()
        newbullet.rect = self.image.get_rect()
        newbullet.rect.topleft = ((self.source[0] - self.screenPos[0], self.source[1] - self.screenPos[1]))
        newbullet.rect.topleft = ((newbullet.rect.topleft[0] - newbullet.rect.width, newbullet.rect.topleft[1] - newbullet.rect.height))
        newbullet.maxspeed = self.maxspeed
        newbullet.DeathTime = self.DeathTime
        
        newbullet.dx = self.speed * math.cos(angle)
        newbullet.xaccel = self.accel * math.cos(angle)
        newbullet.dy = self.speed * math.sin(angle)
        newbullet.yaccel = self.accel * math.sin(angle)

        newbullet.bgcoll = self.bgcoll
        self.bulletgroup.add(newbullet)
        self.allgroup.add(newbullet)
        
        #Calculate nearest wall to collide into
#        a = newbullet.dy / newbullet.dx
#        print(newbullet.realPos)
#        c = -a*newbullet.realPos[0] - newbullet.realPos[1]
#        print(' y = ', a, 'x + ',c)
#        root = math.sqrt(a*a + 1)
#        listy = []
#        for p in self.bgcoll:
#            absval = (a*p[0] - p[1] + c)
#            if absval < 0: 
#                absval = 0-absval
#            d = absval/root
#            if d <= self.radius:
#                if newbullet.dx*p[0] >= 0 and newbullet.dy*p[1] >= 0:
#                    listy.append(p)
#                    self.createMarker(p)
        
    def fire(self, angle):
        self.makebullet(angle)  
    
    #This method is just to place a visual marker on a place
    def createMarker(self, source):
        newbullet = Bullet(source, self.screenSize, self.screenPos)
        newbullet.image = BasicWeapon.weaponimage
        #newbullet.image = pygame.image.load('Images\\testx.png').convert()
        newbullet.rect = self.image.get_rect()
        newbullet.rect.topleft = ((source[0] - self.screenPos[0], source[1] - self.screenPos[1]))
        newbullet.rect.topleft = ((newbullet.rect.topleft[0] - newbullet.rect.width, newbullet.rect.topleft[1] - newbullet.rect.height))

        newbullet.maxspeed = 0
        newbullet.DeathTime = self.DeathTime
        self.bulletgroup.add(newbullet)
        self.allgroup.add(newbullet)