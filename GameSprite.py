'''
Created on Aug 12, 2012

GameSprite is a general class which holds methods and values that the a sprite in the game should have
All Sprites should extend from this

@author: Ant
'''

import pygame, math

class GameSprite(pygame.sprite.Sprite):
    
    image = None # current displayed image
    originalImage = None # original image that is unrotated
    savedImage = None # image saved for animations 
    realPos = [0, 0] #The real position in terms of in game coordinates
    rect = None # The rectangle. rect.topleft gets the coordinates on the screen
    next_update_time = 0 # If we want to update only at a certain time
    update_interval = 10 # Milliseconds between updates. Note, only updates between frames, so might stutter.
    facing = 0.0 # Direction the sprite is facing
    animationList = [] # List of animation lists
    isAnimating = False # Flag for whether animation is playing
    currentAnimation = None # Index of animation currently being played
    currentAnimationFrame = None # Index of current animation frame being played
    nextAnimationTime = None # time when next frame in animation will be played
    animationInterval = None # Flag for interval between animation frames
    revertToOriginalImage = False # Flag for whether to revert to original image after animation
    animationLoop = False # Flag for whether animation should be looped
    animationLoopFromStart = False # Flag for whether animation should be looped from the start (front-to-back-to-front etc.)
    animationFrameForward = True # Flag for whether or not animation frames should be cycled forward or backward
    HP = 0
    XP = 0
    
    screenSize = (800,600)
    allSprites = None #Holds all sprites
    BG = None #Holds the background
    bullets = None #Holds bullets
    weapons = None #Holds weapons
    
    # Takes in real game coordinates, screen dimension, and top-left coordinate of camera, image path and list of animations lists
    def __init__(self, initial_position, screen_position, image_in = None, animList = None):
        pygame.sprite.Sprite.__init__(self)
        # Load image
        if image_in != None:
            try:
                self.originalImage = pygame.image.load(image_in).convert()
                self.originalImage.set_colorkey((255, 255, 255))
            except pygame.error as message:
                print ('Cannot load image', image_in)
                raise (SystemExit, message)
            self.image = pygame.transform.rotate(self.originalImage, self.facing) # assign an unrotated image as the displayed image
            self.rect = self.image.get_rect()
            self.rect.topleft = (initial_position[0] - screen_position[0], initial_position[1] - screen_position[1])
            
        self.animationList = animList
        self.realPos = initial_position
    
    def loadAnimation(self, firstFramePath, frames):
        animation = []
        
        # String parsing to find base file name and extension
        i = len(firstFramePath) - 1
        while i >= 0:
            if firstFramePath[i] == '.':
                extension = firstFramePath[i:]
                while i >= 0:
                    if firstFramePath[i].isalpha() is True:
                        baseFileName = firstFramePath[:i+1]
                        break
                    i -= 1
                break   
            i -= 1
        
        #print "Base filename is", baseFileName
        #print "Extension is", extension
        
        # Load the sequence of frames for this animation
        for frame in range(frames):
            filename = baseFileName + str(frame) + extension
            #print "Filename is", filename
            
            try:
                frame = pygame.image.load(filename).convert()
                frame.set_colorkey((255, 255, 255))
            except pygame.error as message:
                print ('Cannot load image', filename)
                raise (SystemExit, message)            
            animation.append(frame)
            
        return animation
    
    # Rotates the sprite by a given angle in radians
    # Retains the original image's center after rotation, but not necessarily its original shape
    # Check coll denies the rotation if it collides with the background
    def rotateSprite(self, angle, checkcoll = False): 
#            self.facing = math.degrees(-angle) - 90
#            center = self.rect.center
#            rotate = pygame.transform.rotate
#            self.image = rotate(self.originalImage, self.facing)
#            self.rect = self.image.get_rect(center=center)
        if checkcoll is False:
            self.facing = math.degrees(-angle) - 90
            center = self.rect.center
            rotate = pygame.transform.rotate
            self.image = rotate(self.originalImage, self.facing)
            self.rect = self.image.get_rect(center=center)
        #Rotate back if collide
        elif checkcoll is True:
            originalfacing = self.facing
            self.facing = math.degrees(-angle) - 90
            center = self.rect.center
            rotate = pygame.transform.rotate
            self.image = rotate(self.originalImage, self.facing)
            self.rect = self.image.get_rect(center=center)
            for b in BG:
                if self.rect.colliderect(b):
                    if pygame.sprite.collide_mask(self, b) != None:
                        self.facing = originalfacing
                        self.image = rotate(self.originalImage, originalfacing)
                        self.rect = self.image.get_rect(center=center)      

        
        # self.image = pygame.transform.rotate(self.originalImage, self.facing)
    
    # Checks if even a portion of the Sprite is on the screen, after x and y offset
    def onScreen(self, x=0, y=0):
        if self.rect.topleft[0]+x + self.rect.width < 0:
            return False
        if self.rect.topleft[1]+y + self.rect.height < 0:
            return False
        if self.rect.topleft[0]+x > self.screenSize[0]:
            return False
        if self.rect.topleft[1]+y > self.screenSize[1]:
            return False
        return True
    
    # Checks if the entire Sprite is on the screen, after x and y offset
    def withinScreen(self, x=0, y=0):
        if self.rect.topleft[0]+x - self.rect.width < 0:
            return False
        if self.rect.topleft[1]+y - self.rect.height< 0:
            return False
        if self.rect.topleft[0]+x + self.rect.width > self.screenSize[0]:
            return False
        if self.rect.topleft[1]+y + self.rect.height > self.screenSize[1]:
            return False
        return True
    
    # Moves the sprite by x and y, both in game and on screen
    def move(self, x, y):
        self.rect = self.rect.move(x, y)
        self.realPos = (self.realPos[0] + x, self.realPos[1] + y)
        
    # Moves the sprite only on the screen, without changing in-game position
    def moveScreen(self, x, y):
        self.rect = self.rect.move((x, y))
        
    # Sets flag to play an indexed animation
    def playAnimation(self, index, interval, revert=False, loop=False, loopFromStart=False):
        
        # Input validation
        if self.animationList[index] == None:
            print "Error: Animation " + str(index) + " does not exist"
        
        else:
            self.isAnimating = True
            self.currentAnimation = index
            self.currentAnimationFrame = 0
            self.animationInterval = interval 
            self.nextAnimationTime = 0
            
            if revert is True:
                self.revertToOriginalImage = True
                self.savedImage = self.originalImage.copy()
                
            if loop is True:
                self.animationLoop = True
                self.animationLoopFromStart = loopFromStart
                
        
    # The default update simply moves by the given parameter 
    def update(self, current_time, dx = 0, dy = 0):
        
        # Handle animation
        if self.isAnimating is True:
            
            if self.nextAnimationTime <= current_time:
                
                # Check if animation is complete
                if self.currentAnimationFrame >= len(self.animationList[self.currentAnimation]) or self.currentAnimationFrame < 0:
                    
                    # End animation if it is not looping
                    if self.animationLoop is False:
                        self.isAnimating = False
                        if self.revertToOriginalImage is True:
                            self.originalImage = self.savedImage.copy()
                            self.revertToOriginalImage = False
                    
                    else:
                        # Loop frames from start if flag is set
                        if self.animationLoopFromStart is True:
                            self.currentAnimationFrame = 0
                        # Otherwise, reverse the direction of looping
                        else:
                            if self.animationFrameForward is True:
                                self.currentAnimationFrame -= 2
                            else:
                                self.currentAnimationFrame += 2
                            self.animationFrameForward = not self.animationFrameForward
                    
                    
                
                else:
                    self.originalImage = self.animationList[self.currentAnimation][self.currentAnimationFrame]
                    self.nextAnimationTime = current_time + self.animationInterval
                    
                    if self.animationFrameForward is True:
                        self.currentAnimationFrame += 1
                    else:
                        self.currentAnimationFrame -= 1
            
        self.moveScreen(dx, dy)
            
        if self.next_update_time < current_time:
            self.next_update_time = current_time + self.update_interval
            
    def die(self):
        self.kill()
    
    def giveXP(self, XP):
        self.XP = self.XP + XP
    
    def doDmg(self, dmg):
        self.HP = self.HP - dmg
        if self.HP < 0:
            self.die()
            
    # Finds the angle between 2 points
    def findAngle(self, (x1,y1), (x2,y2)):
        # Calculate angle of weapon update
        XDiff = float(x1-x2)
        YDiff = float(y1-y2)

        if XDiff != 0 and YDiff != 0:
            angle = math.atan(YDiff/XDiff)
        # Accounting for 90 degrees where Tan is undefined
        elif YDiff == 0:
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
        return angle

    def getScreenPos(self):
        return (self.realPos[0] - self.rect.topleft[0], self.realPos[1] - self.rect.topleft[1])