'''
Created on Aug 12, 2012

The player. The player sprite also handles input and collision

@author: Ant
'''

import pygame, GameSprite, math, random, Weapon

# Constants
DX = 3
DY = 3
SCALE = 0.9

class Hero(GameSprite.GameSprite, pygame.sprite.Sprite):
    
    Backgroundcoll = None
    weapon = None
    mask = None
    fireX = 0
    fireY = 0
    fireCommandGiven = False
    animationPlayed = False
    weapons = [None, None, None, None, None] #List of weapons
    enemies = None
    
    # Sets image and mask
    def __init__(self, initial_position, screen_position):
        
        # Load animations
        animationList = []
        animationList.append(self.loadAnimation('Images\\newsquarea0.png', 3))
        super(Hero, self).__init__(initial_position, screen_position, 'Images\\newsquare.png', animationList)
        
        self.image.set_colorkey((255, 255, 255))
        self.mask = pygame.mask.from_surface(self.image)
        self.currentWeapon = 0
        self.currenttime = 0
        self.bloodlustend = 0
        self.bloodlusted = False
        self.bloodlustbonus = 0
        self.lastshottime = 0
        self.secondbursttime = 0
        #Now for a LONG LIST OF STATS
        self.HP = 100
        self.maxHP = 100
        self.shields = 10
        self.maxshields = 10
        self.XP = 0
        self.dmgmultiplier = 1.0
        self.accuracymultiplier = 1.0
        self.shieldregenrate = 100
        self.shieldregendelay = 3000
        self.shieldregentime = 0
        self.takeDMG = False
        self.rofmultiplier = 1.0
        self.bulletspeedmultiplier = 1.0
        self.maxbulletspeedmultiplier = 1.0
        self.burstmultiplier = 1.0
        self.clipmultiplier = 1.0
        self.distfromcenter = 0
        self.lastdmgtime = 0
        
        #STAMINA AND ROLLING AND FEATS
        self.speedmultiplier = 2.0
        self.stamina = 100
        self.maxstamina = 1000
        self.staminaregenrate = 2 #Per frame
        self.staminatime = 0
        self.rollmultiplier = 4.0
        self.rolltime = 7 #NUMBER OF FRAMES, NOT MILLISECONDS
        self.canroll = True
        self.rollcooldown = 1500
        self.nextrolltime = 0 
        self.rolltimeleft = 0
        self.sprintstamina = 10
        self.rollstamina = 250
        #Stuff for feats!
        self.feats = feats(self)
        
    def switchWeapon(self):
        startpoint = self.currentWeapon+1
        GameSprite.weapons.remove(self.weapon)
        while(startpoint != self.currentWeapon):
            if startpoint is 5:
                startpoint = 0
            if self.weapons[startpoint] != None:
                self.weapon = self.weapons[startpoint]
                self.currentWeapon = startpoint
                break
            startpoint = startpoint + 1
        GameSprite.weapons.add(self.weapon)
    
    #Pick up weapon
    def pickupWeapon(self, weapongroup):
        for b in weapongroup:
            if pygame.sprite.collide_mask(b, self) is not None:
                self.dropWeapon(weapongroup, b.weapon.classnum)
                self.takeWeapon(b.weapon)
                weapongroup.remove(b)
                GameSprite.allSprites.remove(b)
                break
                
    def takeWeapon(self, weapon):
        self.weapons[weapon.classnum] = weapon
        weapon.owner = self
        
    def numWeapons(self):
        numweaps = 0
        for i in range(len(self.weapons)-1):
            if self.weapons[i] != None:
                numweaps = numweaps + 1
        return numweaps
            
    def dropWeapon(self, weapongroup, dropped = None):
        if dropped is None:
            dropped = self.currentWeapon
        if self.weapons[dropped] is not None:    
            newweap = Weapon.WeaponHolder(self.realPos, self.getScreenPos(), self.weapons[dropped])
            weapongroup.add(newweap)
            GameSprite.allSprites.add(newweap)
            if dropped is self.currentWeapon:
                GameSprite.weapons.remove(self.weapon)
                self.switchWeapon()
            self.weapons[dropped] = None
        
        
    # Takes in keyboard input, outputs initial_position tuple for change in real position
    def keysIn(self, keysdown):
        
        #Handle rolling
        dx = 0
        dy = 0
        if keysdown[0]:
            dy -= DY
        if keysdown[1]:
            dy += DY
        if keysdown[2]:
            dx -= DX
        if keysdown[3]:
            dx += DX
        #For diagonals. Not proper
        if dx != 0 and dy != 0:
            dx = dx*0.707
            dy = dy*0.707
            
        #Handle Sprinting
        if keysdown[5]:
            if self.stamina >= 1:
                self.stamina = self.stamina - self.sprintstamina
                dx = dx * self.speedmultiplier
                dy = dy * self.speedmultiplier
                
        #Handle rolling
        if keysdown[4] and self.canroll is True:
            if self.stamina >= 25:
                self.stamina = self.stamina - self.rollstamina
                self.canroll = False
                self.rolltimeleft = self.rolltime
                
        if self.rolltimeleft > 0:    
            self.rolltimeleft = self.rolltimeleft - 1
            dx = dx * self.rollmultiplier
            dy = dy * self.rollmultiplier

            
        #Some collision detection should go on here
        self.move(dx, 0)
        for b in GameSprite.BG:
            if self.rect.colliderect(b):
                if pygame.sprite.collide_mask(self, b) != None:
                    self.move(-dx, 0)
                    dx = 0
        self.move(0, dy)
        for b in GameSprite.BG:
            if self.rect.colliderect(b):
                if pygame.sprite.collide_mask(self, b) != None:
                    self.move(0, -dy)
                    dy = 0
        self.move(-dx, -dy)

#        for b in GameSprite.BG:
#            if self.rect.colliderect(b):
#                print pygame.sprite.collide_mask(b, self)

        return (dx, dy)   
    
    # Returns the difference between where player is and where player should be based on mouse position (Camera)
    def mouseMove(self, mx, my):
        # Rotate sprite
        angle = self.findAngle((mx, my),(GameSprite.screenSize[0]/2, GameSprite.screenSize[1]/2))
        self.rotateSprite(angle, True)
        supposedx = GameSprite.screenSize[0]/2 + (GameSprite.screenSize[0]/2 - mx - self.rect.width/2)*SCALE
        supposedy = GameSprite.screenSize[1]/2 + (GameSprite.screenSize[1]/2 - my - self.rect.height/2)*SCALE
        changex = supposedx - self.rect.topleft[0]
        changey = supposedy - self.rect.topleft[1]
        self.distfromcenter = math.sqrt((GameSprite.screenSize[0]/2 - mx)*(GameSprite.screenSize[0]/2 - mx) + (GameSprite.screenSize[1]/2 - my)*(GameSprite.screenSize[1]/2 - my))
        self.setFirePoint(mx, my)
        return (changex, changey)
    
    # Passes the location of the mouse, modifies the position of the weapon's fire point
    def setFirePoint(self, x, y):
        self.fireX = x
        self.fireY = y
    
    def updateWeapon(self, mouseX, mouseY, current_time):
        #Weaponpos determines the position of the weapon on the screen (with offset)
        weaponpos = self.weapon.rect.topleft 
        weaponpos = (weaponpos[0]+self.weapon.rect.width/2, weaponpos[1]+self.weapon.rect.height/2)
        #Now position for offset
        #weaponpos = ((weaponpos[0] + self.weapon.bulletoffset*math.cos(math.radians(-self.weapon.facing-90))),(weaponpos[1] + self.weapon.bulletoffset*math.sin(math.radians(-self.weapon.facing-90))))
        angle = self.findAngle((mouseX+2, mouseY+2),(weaponpos))
        # Update the weapon state
        self.weapon.update(angle, current_time, self.fireCommandGiven)
        if self.fireCommandGiven is True:
            self.lastshottime = current_time
    
    def doDmg(self, damage):
        #Invulnerability roll
        if self.feats.su5[0] > 0 and self.rolltimeleft >= (self.rolltime - 30*self.feats.su5[0]):
            return
        
        if self.shields <= 0:
            super(Hero, self).doDmg(damage)        
        if self.shields >= 0:
            self.shields = self.shields - damage
            self.takeDMG = True
        if self.shields < 0:
            self.shields = 0
    
    def giveXP(self, XP):
        super(Hero, self).giveXP(XP)
        #Survival tree
        x = random.random() * 100
        if x <= self.feats.su1[2]*4 and self.shields <= self.maxshields:
            self.shields = self.shields + 1
        x = random.random() * 100
        if x <= self.feats.su4[0]*7 and self.HP < self.maxHP:
            self.HP = self.HP + 1
        #Power tree
        if self.bloodlusted is False:
            self.rofmultiplier = self.rofmultiplier - 0.05 * self.feats.po2[2]
        self.bloodlusted = True
        self.bloodlustend = self.currenttime + 1500
        
    #Update shield info
    def updateShields(self, current_time):
        if self.takeDMG is True:
            self.shieldregentime = current_time + self.shieldregendelay
            self.lastdmgtime = current_time
            self.takeDMG = False
        if current_time > self.shieldregentime:
            if self.shields < self.maxshields:
                self.shieldregentime = current_time+self.shieldregenrate
                self.shields = self.shields + 1
    
    #Update stamina and rolling
    def updateStamina(self, current_time):
        if current_time > self.staminatime:
            self.stamina = self.stamina + self.staminaregenrate
        #Rolling updating
        if current_time > self.nextrolltime:        
            if self.canroll is False:
                self.nextrolltime = current_time + self.rollcooldown
                self.canroll = True
                
    #Note: Update is not changed. Game engine should handle moving the hero back into place
    def update(self, current_time, dx = 0, dy = 0):
        currenttime = current_time
        if current_time > 2000 and self.animationPlayed is False:
            self.playAnimation(0,1000, False, True, False)
            self.animationPlayed = True
        super(Hero, self).update(current_time, dx,dy)
        if self.weapon is not None:
            self.updateWeapon(self.fireX, self.fireY, current_time)
        #Shield updating
        self.updateShields(current_time)
        #Stamina updating
        self.updateStamina(current_time)
        #Feat updating
        self.feats.update(current_time)
        
#Holds the feat tree. For XP and stuff.                
class feats():
    def __init__(self, hero):
        self.user = hero
        self.isOn = False
        self.featcooldown = 5000
        self.nextfeattime = 0
        self.featexpires = 0
        self.usable = True
        self.currentfeat = 0
        self.featstart = False
        self.featduration = 1500
        self.invulroll = False
        self.invultill = 0
        #Survival tree, Power tree, Accuracy tree, Ammo tree
        self.su1 = [0, 0, 0]
        self.su2 = [0, 0, 0]
        self.su3 = [0, 0, 0]
        self.su4 = [0, 0]
        self.su5 = [0]
        self.po1 = [0, 0, 0]
        self.po2 = [0, 0, 0]
        self.po3 = [0, 0, 0]
        self.po4 = [0, 0]
        self.po5 = [0]
        self.ac1 = [0, 0, 0]
        self.ac2 = [0, 0, 0]
        self.ac3 = [0, 0, 0]
        self.ac4 = [0, 0]
        self.ac5 = [0]
        self.am1 = [0, 0, 0]
        self.am2 = [0, 0, 0]
        self.am3 = [0, 0, 0]
        self.am4 = [0, 0]
        self.am5 = [0]
        self.originalimage = None
        self.originalburst = 1.0
        self.changedmg = 0
        self.changeburst = 0
        self.timebetweenshots = 0
        self.crittime = 0
        self.cancrit = False
        self.secondbursttime = 0
        self.clicked = False
        self.changeaccuracy = 0
        self.canlaser = False
        self.lasertime = 0
        self.recoilmodifier = 0
        self.lasering = False
        self.lastlaser = 0
        
    #Modifies stats for feats
    def modifyStats(self):
        #Survival tree
        self.user.sprintstamina = self.user.sprintstamina - self.su1[0]*2
        self.DY = self.DY + self.su1[1]/2
        self.DX = self.DX + self.su1[1]/2
        self.user.maxshields = self.user.maxshields + self.su2[0]
        self.user.rollcooldown = self.user.rollcooldown - 150*self.su2[1]
        self.user.rollstamina = self.user.rollstamina - 30*self.su2[1]
        self.user.staminaregenrate = self.user.staminaregenrate + 2*self.su2[2]
        self.user.shieldregenrate = self.user.shieldregenrate - 5*self.su3[0]
        self.user.maxHP = self.user.maxHP + self.su3[1]
        self.user.maxstamina = self.user.maxstamina + 150*self.su3[2]
        #Power tree
        self.user.dmgmultiplier = self.user.dmgmultiplier + 0.03*self.po1[1]
        #Accuracy tree
        self.user.accuracymultiplier = self.user.accuracymultiplier - 0.03*self.ac1[0]
        self.user.maxbulletspeedmultiplier = self.user.maxbulletspeedmultiplier + 0.1*self.ac1[1]
        
        
    #Reverts stats
    def unmodifyStats(self):
        #Survival tree
        self.user.sprintstamina = self.user.sprintstamina + self.su1[0]*2
        self.DY = self.DY - self.su1[1]/2
        self.DX = self.DX - self.su1[1]/2
        self.user.maxshields = self.user.maxshields - self.su2[0]
        self.user.rollcooldown = self.user.rollcooldown + 150*self.su2[1]
        self.user.rollstamina = self.user.rollstamina + 30*self.su2[1]
        self.user.staminaregenrate = self.user.staminaregenrate - 2*self.su2[2]
        self.user.shieldregenrate = self.user.shieldregenrate + 5*self.su3[0]
        self.user.maxHP = self.user.maxHP - self.su3[1]
        self.user.maxstamina = self.user.maxstamina - 150*self.su3[2]
        #Power tree
        self.user.dmgmultiplier = self.user.dmgmultiplier - 0.03*self.po1[1]
        #Accuracy tree
        self.user.accuracymultiplier = self.user.accuracymultiplier + 0.03*self.ac1[0]
        self.user.maxbulletspeedmultiplier = self.user.maxbulletspeedmultiplier - 0.1*self.ac1[1]
            
    #Modifies Bullet
    def modifyBullet(self):
        #Survival tree
        self.user.dmgmultiplier = self.user.dmgmultiplier + 0.15*self.su4[1]*(self.user.maxHP - self.user.HP)
        #Power tree
        if self.user.shields <= 0:
            self.changedmg = self.changedmg + 0.5*self.po1[2]
            self.user.dmgmultiplier = self.user.dmgmultiplier + self.changedmg
        x = random.random()*100
        if x <= self.po3[0]*5:
            self.changedmg = self.changedmg + 1.0
            self.user.dmgmultiplier = self.user.dmgmultiplier + self.changedmg
        if self.timebetweenshots >= 6000:
            self.changedmg = self.changedmg + 0.2*self.po3[1]
            self.user.dmgmultiplier = self.user.dmgmultiplier + self.changedmg
        if self.user.shields < self.user.maxshields/2:
            self.changedmg = self.changedmg + 0.1*self.po3[1]
            self.user.dmgmultiplier = self.user.dmgmultiplier + self.changedmg
        if self.cancrit is True and self.po4[0] > 0:
            self.changedmg = self.changedmg + 1.0
            self.user.dmgmultiplier = self.user.dmgmultiplier + self.changedmg
            self.cancrit = False
        #Accuracy tree
        if self.user.weapon.burstNum is 1:
            self.user.accuracymultiplier = self.user.accuracymultiplier - 0.04*self.ac1[2]
        self.user.bulletspeedmultiplier = self.user.bulletspeedmultiplier + 0.1*self.ac2[1]
        if self.user.weapon.fireRate >= 1500:
            self.user.dmgmultiplier = self.user.dmgmultiplier + 0.1*self.ac2[2]
        self.changedaccuracy = self.user.accuracymultiplier * 0.0001*(500-self.user.distfromcenter)*1
        if self.user.lastdmgtime < self.user.currenttime - 3000:
            self.changedaccuracy = self.changedaccuracy + (self.user.accuracymultiplier-self.changedaccuracy)*0.08*self.ac3[0]
        if self.user.shields == self.user.maxshields:
            self.changedaccuracy = self.changedaccuracy + (self.user.accuracymultiplier-self.changedaccuracy)*0.05*self.ac3[2]
        self.user.weapon.dmg = self.user.weapon.dmg + 0.5*self.ac3[1]*self.user.weapon.bulletSpeed*self.user.bulletspeedmultiplier
        if self.canlaser is True and self.lasertime > self.user.currenttime and self.ac4[0] > 0:
            self.changedaccuracy = self.user.accuracymultiplier
            self.canlaser = False
            self.lasering = True
            self.lastlaser = self.user.currenttime + self.user.weapon.burstCounter[len(self.user.weapon.burstCounter)-1]
        if self.lasering is True:
            self.changedaccuracy = self.user.accuracymultiplier
            
        self.user.accuracymultiplier = self.user.accuracymultiplier - self.changedaccuracy

    #Reverts Bullet
    def unmodifyBullet(self):
        #Survival tree and others
        self.user.dmgmultiplier = self.user.dmgmultiplier - 0.15*self.su4[1]
        self.user.dmgmultiplier = self.user.dmgmultiplier - self.changedmg
        self.changedmg = 0
        #Accuracy tree
        if self.user.weapon.burstNum is 1:
            self.user.accuracymultiplier = self.user.accuracymultiplier + 0.04*self.ac1[2]
        self.user.bulletspeedmultiplier = self.user.bulletspeedmultiplier - 0.1*self.ac2[1]
        if self.user.weapon.fireRate >= 1500:
            self.user.dmgmultiplier = self.user.dmgmultiplier - 0.1*self.ac2[2]
        self.user.weapon.dmg = self.user.weapon.dmg - 0.5*self.ac3[1]*self.user.weapon.bulletSpeed*self.user.bulletspeedmultiplier     
        self.user.accuracymultiplier = self.user.accuracymultiplier + self.changedaccuracy
        self.changedaccuracy = 0
        
    
    #Modifies burst
    def modifyBurst(self):
        #Power tree
        x = random.random() * 100
        if x <= self.po1[0]*2:
            self.originalburst = self.user.burstmultiplier
            self.user.burstmultiplier = self.user.burstmultiplier*2
        x = random.random() * 100
        if x <= self.po2[0]*5:
            self.changeburst = 1.0
            self.user.dmgmultiplier = self.user.dmgmultiplier + self.changeburst
        self.user.dmgmultiplier = self.user.dmgmultiplier + 0.0001*(500-self.user.distfromcenter)*self.po2[1]
        #TO BE CODED: LUCKY SHOT. PO4[2]
        #Accuracy tree

        
    #Reverts burst
    def unmodifyBurst(self):
        self.user.burstmultiplier = self.originalburst
        self.user.dmgmultiplier = self.user.dmgmultiplier - self.changeburst
        self.changeburst = 0
        #Accuracy tree
         
    #For clicking a second time, special feats        
    def checkSecondBurst(self):
        self.clicked = True

    #Switching weapon, changes feats
    def switchweapon(self, category):
        None
        
    def update(self, current_time):
        if self.featstart is True:
            self.featstart = False
            self.featexpires = current_time + self.featduration
            self.nextfeattime = current_time + self.featcooldown
        if current_time > self.nextfeattime:
            self.usable = True
        if current_time > self.featexpires and self.isOn is True:
            self.turnoff()
            
        #Power Tree
        if self.user.bloodlusted is True and current_time > self.user.bloodlustend:
            self.user.rofmultiplier = self.user.rofmultiplier + 0.05 * self.po2[2]
            self.user.bloodlusted = False
        
        self.timebetweenshots = current_time - self.user.lastshottime
        if self.cancrit is False and current_time > self.crittime:
            self.cancrit = True
            self.crittime = current_time + 6000 - 500*self.po4[0]
        if self.clicked is True:
            if current_time < self.secondbursttime:
                print ('double')
                self.secondbursttime = current_time
                self.user.weapon.nextFireTime = current_time
            self.clicked = False
            
        #Accuracy tree
        if self.canlaser is False and current_time > self.lasertime:
            self.canlaser = True
            self.lasertime = current_time + 6000 - 500*self.ac4[1]
        if self.lastlaser < current_time:
            self.lasering = False
    
    def turnoff(self):
        self.isOn = False
        self.user.weapon.weaponimage = self.originalimage
        
    def use(self):
        if self.usable is True:
            self.isOn = True
            if self.currentfeat == 0:
                self.usable = False
                self.featstart = True
                self.originalimage = self.user.weapon.weaponimage
                self.user.weapon.weaponimage = pygame.image.load('images\\testx.png').convert()
                
            