'''
Created on Aug 12, 2012

Contains classes for Weapons and Bullets. A Weapon fires a bullet. A bullet is an actual sprite.

@author: Ant
'''

import pygame, sys, math, GameSprite, random

#This is a weapon holder sprite. It represents a weapon to be picked up.
class WeaponHolder(GameSprite.GameSprite):
    weapongroup = None
    # Sets image and mask
    def __init__(self, initial_position, screen_position, weapon):
        super(WeaponHolder, self).__init__(initial_position, screen_position, weapon.groundimage)
        self.image.set_colorkey((255, 255, 255))
        self.mask = pygame.mask.from_surface(self.image)
        self.weapon = weapon
        
        
        
# This is a basic weapon. Meant to be abstracted to provide for a larger weapon class
class Weapon(GameSprite.GameSprite):
    weaponimage = None
    weaponmask = None

    def __init__(self, owner, graphic):
        screenSource = (owner.realPos[0]-owner.rect.topleft[0], owner.realPos[1]-owner.rect.topleft[1])
        super(Weapon, self).__init__(owner.realPos, screenSource, graphic)
        self.offset = 0
        self.angleoffset = 0
        self.bulletoffset = 0
        
        self.groundimage = 'Images\\heroold.png'
        self.burstCounter = []
        self.screenPos = None
        self.bulletgroup = None
        self.mask = None
        self.owner = None # object that the weapon belongs to
        self.nextFireTime = 0 # save the time for when the weapon can be fired again
        self.radius = 1
        self.enemygroup = None
        self.owner = owner
        self.enemygroup = owner.enemies
        self.reloading = False
        self.reloadtime = 100
        self.ammo = 5
        self.maxammo = 5
        self.classnum = 0 #0 for pistols. 1 for shotguns. 2 for SMGs. 3 for rifles. 4 for Heavy.
        # Set instance
        if Weapon.weaponimage is None:
            Weapon.weaponimage = pygame.image.load('Images\\bullety.png').convert()
            Weapon.weaponimage.set_colorkey((255, 255, 255))
            Weapon.weaponmask = pygame.mask.from_surface(Weapon.weaponimage)
        self.weaponimage = Weapon.weaponimage
        self.mask = Weapon.weaponmask

    # Note that angle is IN RADIANS
    # By default, the angle is calculated from the x axis, not north
    def makebullet(self, angle):
        if self.owner.__class__.__name__ is 'Hero':
            self.owner.feats.modifyBullet()
            
        screenSource = (self.owner.realPos[0]-self.owner.rect.topleft[0], self.owner.realPos[1]-self.owner.rect.topleft[1])
        #Fine tune screenSource to have position relative to hero
        newbullet = Bullet(self.owner.realPos, screenSource)
        newbullet.image = self.weaponimage
        newbullet.originalImage = self.weaponimage
        newbullet.mask = self.weaponmask
        newbullet.rect = newbullet.image.get_rect()
        
        newbullet.rect.topleft = self.rect.topleft
        #Shifts the new bullet's CENTER into the CENTER of the owner's weapon
        newbullet.rect.topleft = ((newbullet.rect.topleft[0] - newbullet.rect.width/2 + self.rect.width/2, newbullet.rect.topleft[1] - newbullet.rect.height/2 + self.rect.height/2))
        #Shifts new bullet's position into an offset (from counterclockwise degrees to clockwise radians)
        newbullet.rect.topleft = ((newbullet.rect.topleft[0] + self.bulletoffset*math.cos(math.radians(-self.facing-90))),(newbullet.rect.topleft[1] + self.bulletoffset*math.sin(math.radians(-self.facing+-90))))
        
        newbullet.maxSpeed = self.maxSpeed*self.owner.maxbulletspeedmultiplier
        newbullet.HP = self.deathTime
        newbullet.enemycoll = self.enemygroup
        newbullet.dmg = self.dmg*self.owner.dmgmultiplier
        newbullet.owner = self.owner
        #Add in recoil
        angle = angle + math.radians(random.random()*self.recoil-self.recoil/2)*self.owner.accuracymultiplier
        
        newbullet.dx = self.bulletSpeed*self.owner.bulletspeedmultiplier * math.cos(angle)
        newbullet.xaccel = self.accel * math.cos(angle)
        newbullet.dy = self.bulletSpeed*self.owner.bulletspeedmultiplier * math.sin(angle)
        newbullet.yaccel = self.accel * math.sin(angle)
        newbullet.rotateSprite(angle)

        GameSprite.bullets.add(newbullet)
        GameSprite.allSprites.add(newbullet)
        
        if self.owner.__class__.__name__ is 'Hero':
            self.owner.feats.unmodifyBullet()

    def reload(self, currentTime):
        self.nextFireTime = currentTime + self.reloadtime
        self.reloading = True
        
    def update(self, angle, currentTime, fireCommandReceived):
        
        if fireCommandReceived is True:
            # If weapon hasn't been fired before or has cooled down, fire it
            if self.nextFireTime < currentTime and self.reloading is False:
                if self.ammo > 0:
                    self.ammo = self.ammo - 1
                    if self.owner.__class__.__name__ is 'Hero':
                        self.owner.feats.modifyBurst()
                    self.nextFireTime = currentTime + self.fireRate*self.owner.rofmultiplier
                    for i in range(len(self.burstCounter)):
                        self.burstCounter.pop(0)
                    for i in range(int(self.burstNum*self.owner.burstmultiplier)):
                        self.burstCounter.append(currentTime + i*self.burstRate)
                    if self.owner.__class__.__name__ is 'Hero':
                        self.owner.feats.unmodifyBurst()
                else:
                    self.reload(currentTime)
            elif self.nextFireTime < currentTime and self.reloading is True:
                self.ammo = self.maxammo
                self.reloading = False

        while len(self.burstCounter) > 0 and self.burstCounter[0] < currentTime:
            self.makebullet(angle)
            self.burstCounter.pop(0)
            #Feat for double up, power tree
            if self.owner.__class__.__name__ is 'Hero' and len(self.burstCounter) is 0:
                self.owner.feats.secondbursttime = currentTime + self.owner.feats.po5[0]*20
        
        #Sets the weapon's position on the screen
        self.rect.topleft = ((self.owner.rect.topleft[0] - self.rect.width/2 + self.owner.rect.width/2, self.owner.rect.topleft[1] - self.rect.height/2 + self.owner.rect.height/2))
        self.rect.topleft = ((self.rect.topleft[0] + self.offset*math.cos(math.radians(-self.owner.facing+self.angleoffset-90))),(self.rect.topleft[1] + self.offset*math.sin(math.radians(-self.owner.facing+self.angleoffset-90))))
        self.rotateSprite(angle)
   
    # This method is just to place a visual marker on a place
    def createMarker(self):
        screenSource = (self.owner.realPos[0]-self.owner.rect.topleft[0]-self.owner.rect.width, self.owner.realPos[1]-self.owner.rect.topleft[1]-self.owner.rect.height)
        newbullet = Bullet(self.owner.realPos, self.screenSize, screenSource)
        newbullet.image = Weapon.weaponimage
        newbullet.rect = self.image.get_rect()
        newbullet.rect.topleft = ((self.owner.realPos[0] - screenSource[0], self.owner.realPos[1] - screenSource[1]))
        newbullet.rect.topleft = ((newbullet.rect.topleft[0] - newbullet.rect.width, newbullet.rect.topleft[1] - newbullet.rect.height))
        newbullet.maxSpeed = 0
        newbullet.deathTime = self.deathTime
        GameSprite.bullets.add(newbullet)
        GameSprite.allSprites.add(newbullet)
        
class Bullet(GameSprite.GameSprite, pygame.sprite.Sprite):
    
    dx = 0.0
    dy = 0.0
    xaccel = 0.0
    yaccel = 0.0 
    maxSpeed = 0.0
    reachedmax = False
    Tick = 0
    xcap = 0.0 #Capacitators. Stores the remainder.
    ycap = 0.0
    enemycoll = None
    dmg = 0
    owner = None
    # Sets image and mask
    def __init__(self, initial_position, screen_position):
        super(Bullet, self).__init__(initial_position, screen_position)
    
    # Updates the weapon, firing it if necessary
    def update(self, current_time, dx = 0, dy = 0):
        super(Bullet, self).update(current_time, dx, dy) #Move for the screen
        
        # Account for lack of rounding
        if self.dx > 0:
            self.xcap = (self.xcap + self.dx)%1
        else:
            self.xcap = (self.xcap + self.dx)%-1
        if self.dy > 0:
            self.ycap = (self.ycap + self.dy)%1
        else:
            self.ycap = (self.ycap + self.dy)%-1
            
        self.move(self.dx+self.xcap, self.dy+self.ycap) #Move real position due to velocity

        if self.reachedmax is False and self.maxSpeed > self.magnitude(self.dx, self.dy):
            self.dx = self.dx + self.xaccel
            self.dy = self.dy + self.yaccel
        else:
            self.reachedmax = True
        self.doDmg(1)

        for b in GameSprite.BG:
            if self.rect.colliderect(b):
                if pygame.sprite.collide_mask(self, b) != None:
                    self.die()
                
        for b in self.enemycoll:
            if self.rect.colliderect(b):
                if pygame.sprite.collide_mask(self, b) != None:
                    b.doDmg(self.dmg)
                    if b.HP <= 0:
                        self.owner.giveXP(b.XP)
                    self.die()
        
    def magnitude(self, x, y):
        return math.sqrt(x*x + y*y)

class TestWeapon(Weapon):
    weaponimage = None
    def __init__(self, owner, config = 0, level = 1):
        super(TestWeapon, self).__init__(owner, 'Images\\Weapons\\pistolheld1.png')
        if config == 0:
            self.groundimage = 'Images\\Weapons\\pistol1.png'
            self.offset = 15
            self.angleoffset = 22
            self.bulletoffset = 6
            
            self.bulletSpeed = 10
            self.recoil = 0
            self.fireRate = 100
            self.burstRate = 50
            self.burstNum = 1 + int((random.random()*100)/90)*int(level/10)
            self.source = 0, 0
            self.accel = 0.01
            self.maxSpeed = 10
            self.deathTime = 450
            self.radius = 2
            self.dmg = 2 + (random.random()*3*level) + level/2
            self.reloadtime = 100
            self.ammo = 15 + int((random.random()*100)/90)*int(level/10)
            self.maxammo = self.ammo
            self.classnum = 0
            if Pistol.weaponimage is None:
                Pistol.weaponimage = pygame.image.load('Images\\Projectiles\\Bullet1.png').convert()
                Pistol.weaponimage.set_colorkey((255, 255, 255))
                Pistol.weaponmask = pygame.mask.from_surface(Pistol.weaponimage)
            self.weaponimage = Pistol.weaponimage
            self.mask = Pistol.weaponmask
            
class Pistol(Weapon):
    weaponimage = None
    def __init__(self, owner, config = 0, level = 1):
        super(Pistol, self).__init__(owner, 'Images\\Weapons\\pistolheld1.png')
        if config == 0:
            self.groundimage = 'Images\\Weapons\\pistol1.png'
            self.offset = 15
            self.angleoffset = 22
            self.bulletoffset = 6
            
            self.bulletSpeed = 7.0
            self.recoil = 2.0 - int((random.random()*100)/49)*0.5
            self.fireRate = 500 - (random.random()*3*level)
            self.burstRate = 50
            self.burstNum = 1 + int((random.random()*100)/90)*int(level/10)
            self.source = 0, 0
            self.accel = 0.01
            self.maxSpeed = self.bulletSpeed
            self.deathTime = 50
            self.radius = 2
            self.dmg = 2 + (random.random()*3*level) + level/2
            self.reloadtime = 700
            self.ammo = 5 + int((random.random()*100)/90)*int(level/10)
            self.maxammo = self.ammo
            self.classnum = 0
            if Pistol.weaponimage is None:
                Pistol.weaponimage = pygame.image.load('Images\\Projectiles\\Bullet1.png').convert()
                Pistol.weaponimage.set_colorkey((255, 255, 255))
                Pistol.weaponmask = pygame.mask.from_surface(Pistol.weaponimage)
            self.weaponimage = Pistol.weaponimage
            self.mask = Pistol.weaponmask

class Shotgun(Weapon):
    weaponimage = None
    def __init__(self, owner, config = 0, level = 1):
        super(Shotgun, self).__init__(owner, 'Images\\Weapons\\shotgunheld1.png')
        if config == 0:
            self.groundimage = 'Images\\Weapons\\shotgun1.png'
            self.offset = 20
            self.angleoffset = -20
            self.bulletoffset = 10
            
            self.bulletSpeed = 10.0
            self.recoil = 10 - int((random.random()*100)/49)*2
            self.fireRate = 1200 - int((random.random()*100)/30)*10*level
            self.burstRate = 5
            self.burstNum = 10 + int((random.random()*100)/45)*int(level/5)
            self.source = 0, 0
            self.accel = 0.1
            self.maxSpeed = self.bulletSpeed
            self.deathTime = 100
            self.radius = 2
            self.dmg = 1 + (random.random()*level) + level/4
            self.reloadtime = 1700 - int((random.random()*100)/90)*level*10
            self.ammo = 3 + int((random.random()*100)/90)*int(level/10)
            self.maxammo = self.ammo
            self.classnum = 1
            if Shotgun.weaponimage is None:
                Shotgun.weaponimage = pygame.image.load('Images\\Projectiles\\Pellet1.png').convert()
                Shotgun.weaponimage.set_colorkey((255, 255, 255))
                Shotgun.weaponmask = pygame.mask.from_surface(Shotgun.weaponimage)
            self.weaponimage = Shotgun.weaponimage
            self.mask = Shotgun.weaponmask