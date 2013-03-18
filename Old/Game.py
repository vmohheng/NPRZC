'''
Created on Aug 12, 2012

Where the main game runs. Input processing also done here

@author: Ant
'''

import pygame, sys
from pygame.locals import *
from GameSprite import *
from Hero import *
from Background import *
from Weapon import *

#Define initial stuff
BgColor = (128, 128, 128) #Background color
screenSize = 800, 600 #Size of screen, obviously
screenPos = 0, 0 #Top-left corner of our screen in real coordinates
FPS = 60 #Frames per second


#Run initial processes
fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode(screenSize)
pygame.init()

#Declare spritegroups
allSprites = pygame.sprite.Group()
BG = pygame.sprite.Group()
herogroup = pygame.sprite.Group()
bulletgroup = pygame.sprite.Group()

#TEST INITIATION FOR WEAPON
#backcoll = [] #Background collision pixels

weapon = BasicWeapon()
weapon.screenSize = screenSize
weapon.bulletgroup = bulletgroup
weapon.allgroup = allSprites
weapon.bgcoll = BG
#weapon.bgcoll = backcoll

#Instantiate sprites
hero = Hero((screenSize[0]/2, screenSize[1]/2), screenSize, screenPos)
allSprites.add(hero)
herogroup.add(hero)
hero.Backgroundcoll = BG


nr = 2
mr = 2
stepsize = 650

for n in range(0, nr):
    for m in range(0, mr):
        ns = Background((n*stepsize, m*stepsize), screenSize, screenPos, 'Images\\davince2.png', 'Images\\colltest3.bmp', BG)
        k = int((n*mr+m)/(nr*mr)*100)
        print('Loading: ' + str(k) +'%')
        allSprites.add(ns)
        
#        w, h = ns.mask.get_size()
#        for x in range(0, w):
#            for y in range (0, h):
#                if ns.mask.get_at((x, y)) != 0:
#                    backcoll.append((x+ns.realPos[0], y+ns.realPos[1]))

#The ingame loop
keysDown = [False, False, False, False]
mouseChange = [0, 0]

while True:
    
    mouseX, mouseY = pygame.mouse.get_pos()
    #Control handling
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
            
        elif e.type == KEYDOWN:
            if e.key == K_a:
                keysDown[2] = True
            if e.key == K_w:
                keysDown[0] = True
            if e.key == K_d:
                keysDown[3] = True
            if e.key == K_s:
                keysDown[1] = True
    
        elif e.type == MOUSEBUTTONDOWN:
            #FIRE ZE WEAPON
            XDiff = mouseX - screenSize[0]/2
            YDiff = mouseY - screenSize[1]/2

            if XDiff != 0 and YDiff != 0:
                angle = math.atan(YDiff/XDiff)
                
            #Accounting for 90 degrees where Tan is undefined
            elif YDiff is 0:
                if XDiff > 0:
                    angle = 0
                else:
                    angle = math.pi*2
            else:
                if YDiff > 0:
                    angle = math.pi/2
                else:
                    angle = math.pi*3/2
            if XDiff < 0:
                angle = angle + math.pi
            #print (angle)
            weapon.source = hero.realPos
            weapon.fire(angle)
        
    #Get offsets from control
    kbx, kby = hero.keysIn(keysDown)
    
    mx, my = hero.mouseMove(mouseX, mouseY)
    
    #Move all the sprites
    time = pygame.time.get_ticks()
    allSprites.update(time, (-kbx+mx), (-kby+my)) #Everything moves on the screen
    hero.move(kbx, kby) #Hero's actual movement
    screenPos = (hero.realPos[0]-hero.rect.topleft[0]-hero.rect.width, hero.realPos[1]-hero.rect.topleft[1]-hero.rect.height)

    weapon.screenPos = screenPos
    #Draw shit
    screen.fill(BgColor)
    BG.draw(screen)
    herogroup.draw(screen)
    bulletgroup.draw(screen)
    pygame.display.update()
        
    fpsClock.tick(FPS)


