'''
Created on Aug 12, 2012

Where the main game runs. Input processing also done here

@author: Ant
'''

import pygame, sys
from pygame.locals import *
from GameSprite import *
from Actor import *
from Hero import *
from Background import *
from Weapon import *
from Enemy import *

#Define initial stuff
BgColor = (128, 128, 128) #Background color
screenSize = 800, 600 #Size of screen, obviously
screenPos = 0, 0 #Top-left corner of our screen in real coordinates
FPS = 60 #Frames per second


#Run initial processes
fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode(screenSize)
pygame.init()
pygame.mouse.set_cursor(*pygame.cursors.broken_x)

# Declare spritegroups
allSprites = pygame.sprite.Group() #All sprites
BG = pygame.sprite.Group() #The background
herogroup = pygame.sprite.Group() #Just for the hero
enemygroup = pygame.sprite.Group() #Just for enemies
bulletgroup = pygame.sprite.Group() #All the projectiles
weapongroup = pygame.sprite.Group() #All the weapons on the ground
weapondisplaygroup = pygame.sprite.Group() #The weapons BEING HELD

#Declare globals
GameSprite.BG = BG
GameSprite.allSprites = allSprites
GameSprite.screenSize = screenSize
GameSprite.bullets = bulletgroup
GameSprite.weapons = weapondisplaygroup

#Initiate hero
hero = Hero((screenSize[0]/2, screenSize[1]/2), screenPos)
hero.enemies = enemygroup
hero.takeWeapon(TestWeapon(hero, 0, 5))
hero.switchWeapon()


#Test enemy
enemy = Enemy((5, 5), screenPos)
enemy.enemies = herogroup
enemy.weapon = Pistol(enemy, 0, 1)
enemy2 = Enemy((130, 5), screenPos)
enemy2.enemies = herogroup
enemy2.weapon = Pistol(enemy2, 0, 1)
allSprites.add(enemy)
enemygroup.add(enemy)
allSprites.add(enemy2)
enemygroup.add(enemy2)
weapondisplaygroup.add(enemy2.weapon)
weapondisplaygroup.add(enemy.weapon)

#Test weapongroup
weap1 = WeaponHolder((100, 400), screenPos, Pistol(hero, 0, 30))
weap2 = WeaponHolder ((100, 450), screenPos, Shotgun(hero, 0, 30))
allSprites.add(weap1)
allSprites.add(weap2)
weapongroup.add(weap1)
weapongroup.add(weap2)

# Instantiate sprite groups
allSprites.add(hero)
herogroup.add(hero)


nr = 2
mr = 2
stepsize = 650

for n in range(nr):
    for m in range(mr):
        ns = Background((n*stepsize, m*stepsize), screenPos, 'Images\\davinci3.png', 'Images\\colltest5.bmp')
        k = int((n*mr+m)*100/(nr*mr))
        print('Loading: ' + str(k) +'%')
        allSprites.add(ns)

# The ingame loop
keysDown = [False, False, False, False, False, False]
mouseChange = [0, 0]
autoFire = False # flag for weapon auto fire
autoFireCounter = 0 # counter for auto fire speed

while True:
    mouseX, mouseY = pygame.mouse.get_pos()
    time = pygame.time.get_ticks()
    # Control handling
    for e in pygame.event.get():
        if e.type == QUIT:
            pygame.quit()
            sys.exit()
        elif e.type == KEYUP:
            if e.key == K_a:
                keysDown[2] = False
            if e.key == K_w:
                keysDown[0] = False
            if e.key == K_d:
                keysDown[3] = False
            if e.key == K_s:
                keysDown[1] = False
            if e.key == K_SPACE:
                keysDown[4] = False
            if e.key == K_LSHIFT:
                keysDown[5] = False
            
        elif e.type == KEYDOWN:
            if e.key == K_a:
                keysDown[2] = True
            if e.key == K_w:
                keysDown[0] = True
            if e.key == K_d:
                keysDown[3] = True
            if e.key == K_s:
                keysDown[1] = True
            if e.key == K_SPACE:
                keysDown[4] = True
            if e.key == K_LSHIFT:
                keysDown[5] = True
            
            #Test x to switch weapon
            if e.key == K_x:
                hero.switchWeapon()
            if e.key == K_q:
                hero.feats.use()
            if e.key == K_e:
                hero.pickupWeapon(weapongroup)
            if e.key == K_r:
                hero.weapon.reload(time)
        
        elif e.type == MOUSEBUTTONDOWN:
            hero.fireCommandGiven = True
            hero.feats.checkSecondBurst()
        
        elif e.type == MOUSEBUTTONUP:
            if hero.fireCommandGiven is True:
                hero.fireCommandGiven = False
        
    # Get offsets from control
    kbx, kby = hero.keysIn(keysDown)
    
    mx, my = hero.mouseMove(mouseX, mouseY)
    
    # Move all the sprites
    allSprites.update(time, (-kbx+mx), (-kby+my)) #Everything moves on the screen
    hero.move(kbx, kby) #Hero's actual movement

    # Draw shit
    screen.fill(BgColor)
    BG.draw(screen)
    weapongroup.draw(screen)
    weapondisplaygroup.draw(screen)
    enemygroup.draw(screen)
    herogroup.draw(screen)
    bulletgroup.draw(screen)

    pygame.display.update()
        
    fpsClock.tick(FPS)


