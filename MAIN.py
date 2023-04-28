############################################################
# GAME NAME: NOT UTOPIA 
# CREATER: RONG YUAN
############################################################
# Code Structure: 
# Animation Defaults + (Animation Defaults Helper Group): Connects User to the Game  
# The ACTIVE Part: Enable the moving of the character 
# MAZE GENERATION ALGORITHM: Takes in 2d maze, returns 3d Maze, with lifting, ladder, blocks sorted 
# DRAWING the DELIVERABLE: Puts Everything Together  

from cmu_graphics import *   #credit: MODULE FROM https://academy.cs.cmu.edu/desktop 
from pyamazeEdited import maze  #credit: MODULE FROM https://github.com/MAN1986/pyamaze/blob/main/pyamaze/pyamaze.py MAN1986
import copy
import math
import random
from PIL import Image, ImageDraw
import os, pathlib


############################################################
#Animation Defaults 
############################################################
def onAppStart(app):
    getSound(app)
    restart(app)

def restart(app):
    app.index = 1 #color theme
    loadColor(app, app.index) 
    app.width = 1200 #canvas default 
    app.height = 800
    app.dimension = None #maze settings
    app.sunnyMode = None
    app.fogMode = None
    app.startPage = True #page status
    app.win = False

def redrawAll(app):
    if app.startPage:
        drawStartInterface(app) #draw the start interface 
        drawSelected(app) #draw mode selected
        if app.dimension != None and app.fogMode!= None: #draw start button
            drawRect(1020, 470, 240, 100, fill = app.color.sWordsC, align='center')
            drawLabel('START', 1020, 470, fill = app.color.sBackgroundC, size = 45, font='Kefa', bold = True)
    else:
        if app.fogMode:
            drawMapFog(app) 
            app.char.drawChar(app)
            app.char.drawMoreL(app, getMapFog(app))
            drawFogModeInstructions(app)
        if app.sunnyMode:
            drawMap(app)
            app.char.drawChar(app)
            app.char.drawMoreL(app, app.map.theL)
            drawSunnyModeInstructions(app)
        drawMiniMap(app)
        drawKeyInstruction(app)
        if app.win:
            drawWinMap(app)
        drawBackButton(app)

def onStep(app): #this is for the sprites
    if app.startPage == False:
        app.steps += 1
        app.spriteCounter = app.steps // (6-app.dimension//2) % 6 

def onMousePress(app, mouseX, mouseY):
    app.buttonSound.play()
    if app.startPage:  #maze settings selection
        if 420<mouseX<620 and 330<mouseY<390:
            app.index = 1
            loadColor(app, app.index)
        elif 660<mouseX<860 and 330<mouseY<390:
            app.index = 2
            loadColor(app, app.index)
        elif 900<mouseX<1100 and 330<mouseY<390:
            app.index = 3
            loadColor(app, app.index)
        if 420<mouseX<620 and 440<mouseY<500:
            app.sunnyMode = True
            app.fogMode = False
        elif 660<mouseX<860 and 440<mouseY<500:
            app.fogMode = True
            app.sunnyMode = False
        if 420<mouseX<620 and 550<mouseY<610:
            app.dimension = 6
        elif 660<mouseX<860 and 550<mouseY<610:
            app.dimension = 8
        elif 900<mouseX<1100 and 550<mouseY<610:
            app.dimension = 10
        if app.fogMode != None and app.dimension != None:
            if 900<mouseX<1140 and 420<mouseY<520:
                app.startPage = False
        if app.startPage == False:
            gameStarts(app) #call main game starts
    else:  #back button
        if 50<mouseX<250 and 30<mouseY<110: 
            restart(app)

def onKeyHold(app, keys):
    if app.win == False:
    #SunnyMode 
        if app.sunnyMode:
            L = app.char.movable(app) #Vertical 
            verticalMove(app, keys)
            if app.char.zBlock % 1 == 0: #Horizontal 
                sunnyHorizontalMove(app, keys, L)
            if (app.char.xBlock, app.char.yBlock) in app.coins: #Coins check
                if ((app.char.xBlock, app.char.yBlock)) not in app.gotCoins:
                    app.sunSound.play()
                    app.gotCoins.append((app.char.xBlock, app.char.yBlock))
    #FoggyMode
        elif app.fogMode: 
            L = app.char.movable(app) #Vertical 
            verticalMove(app, keys)
            if app.char.zBlock % 1 == 0: #Horizontal 
                foggyHorizontalMove(app, keys, L)
    #win check
        if app.dimension*app.blockSize-4/5*app.blockSize<app.char.xBoard<app.dimension*app.blockSize-1/5*app.blockSize and 1/5*app.blockSize<app.char.yBoard<4/5*app.blockSize: 
            if app.sunnyMode == True:
                if len(app.gotCoins) == app.dimension-3:
                    app.win = True
                    app.winSound.play()
            else:
                app.win = True
                app.mazeLFDX = 555 
                app.mazeLFDY = 633 
                app.winSound.play()

def onKeyRelease(app, key): #Sound, Status Reset
    app.charStatus = None
    app.footSound.pause()


############################################################
#Animation Defaults Helper Function Group 
############################################################

##############################
#credit: Sound Import Helper Functions #AlGORITHEM FROM TA SHAWN https://piazza.com/class/lcnu63g1yps41j/post/1665
def getSound(app):
    #credit: Sound Effect from <a href="https://pixabay.com/sound-effects/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=music&amp;utm_content=6752">Pixabay</a>
    app.footSound = loadSound("Concrete.mp3")
    #credit: Sound Effect from https://themushroomkingdom.net/media/smb/wav
    app.sunSound = loadSound('coin.mp3')
    app.buttonSound = loadSound('press.mp3')
    #credit: Sound Effect from https://pixabay.com/sound-effects/search/cash/
    app.winSound = loadSound('cash.mp3')

def loadSound(relativePath):
    absolutePath = os.path.abspath(relativePath)
    url = pathlib.Path(absolutePath).as_uri()
    return Sound(url)

##############################
#Class Color. Color theme indexing 
class color:

    def __init__(self, index):
        if index == 1: #Shcheneley
            self.index = 1
            self.sBackgroundC = rgb(242, 227, 219)
            self.sCubeFC = rgb(65, 100, 74)
            self.sCubeTC = rgb(53, 94, 64)
            self.sCubeLC = rgb(50, 75, 57)
            self.sLineC = rgb(38, 58, 41)
            self.sWordsC = rgb(232, 106, 51)
        elif index == 2: #Allegheny 
            self.index = 2
            self.sBackgroundC = rgb(203, 228, 222)
            self.sCubeFC = rgb(14, 131, 136)
            self.sCubeTC = rgb(5, 118, 122)
            self.sCubeLC = rgb(14, 105, 108)
            self.sLineC = rgb(46, 79, 79)
            self.sWordsC = rgb(44, 51, 51)
        elif index == 3: #Squirrel Hill
            self.index = 3
            self.sBackgroundC = rgb(147, 199, 163)
            self.sCubeFC = rgb(243, 233, 159)
            self.sCubeTC = rgb(240, 230, 132)
            self.sCubeLC = rgb(228, 220, 148)
            self.sLineC = rgb(247, 208, 96)
            self.sWordsC = rgb(255, 109, 96)

    def __repr__(self):
        if self.index == 1:
            return 'Scheneley'
        elif self.index == 2:
            return 'Allegheny'
        elif self.index == 3:
            return 'Squirrel Hill'

def loadColor(app, index):
    app.color = color(index)

##############################
#Main Game Start Default Helper Funtion
def gameStarts(app): #Called when main game starts
    mapInitials(app)
    app.steps = 0
    app.mazeMap = loadNew2dMap(app)
    loadNewMap(app)
    app.char = Char(app)
    getTheMapDone(app)
    app.coins = getCoins(app)
    app.gotCoins = []

##############################
#Game Play Key Event Helper Functions
def verticalMove(app, keys):
    if app.char.upable(app) != False:
        a, b, c = app.char.upable(app)
        if 'space' in keys and 'up' in keys: #move up
            app.char.charMoveUp(app)
            if app.char.zBlock-c>0: #set to the right spot
                app.char.xBoard, app.char.yBoard, app.char.zBlock = app.char.xBoard+(a*app.blockSize+0.5*app.blockSize-app.char.xBoard)/3, app.char.yBoard+(b*app.blockSize+0.5*app.blockSize-app.char.yBoard)/3, c
                app.eastLadder = app.northLadder = False
        if 'space' in keys and 'down' in keys: #move down
            app.char.charMoveDown(app)
            if app.char.zBlock < app.map.heightChart[(app.char.xBlock, app.char.yBlock)]: #set to the right spot
                app.char.zBlock = app.map.heightChart[(app.char.xBlock, app.char.yBlock)]
                app.eastLadder = app.northLadder = False
    if app.char.downable(app) != False: #Switch the player to the right place to enable 'upable'
        a, b, c = app.char.downable(app)
        if 'space' in keys and 'down' in keys:
            app.char.xBoard, app.char.yBoard= app.char.xBoard+(a*app.blockSize+0.5*app.blockSize-app.char.xBoard)/3, app.char.yBoard+(b*app.blockSize+0.5*app.blockSize-app.char.yBoard)/3
            app.char.charMoveDown(app)
    if app.char.downable(app) == False == app.char.upable(app): #for instruction drawing 
        app.eastLadder = app.northLadder = False

def sunnyHorizontalMove(app, keys, L):
    if 'up' in keys:
        app.char.charMoveN(app)
        if (app.char.xBlock, app.char.yBlock, app.char.zBlock) not in L:
            app.char.charMoveS(app)
            app.charStatus = None
    elif 'down' in keys:
        app.char.charMoveS(app)
        if (app.char.xBlock, app.char.yBlock, app.char.zBlock) not in L:
            app.char.charMoveN(app)
            app.charStatus = None
    elif 'right' in keys:
        app.char.charMoveE(app)
        if (app.char.xBlock, app.char.yBlock, app.char.zBlock) not in L:
            app.char.charMoveW(app)
            app.charStatus = None
    elif 'left' in keys:
        app.char.charMoveW(app)
        if (app.char.xBlock, app.char.yBlock, app.char.zBlock) not in L:
            app.char.charMoveE(app)
            app.charStatus = None

def foggyHorizontalMove(app, keys, L):
    if 'up' in keys:
        mazeMoveS(app)
        if (app.char.xBlock, app.char.yBlock, app.char.zBlock) not in L:
            mazeMoveN(app)
            app.charStatus = None
    elif 'down' in keys:
        mazeMoveN(app)
        if (app.char.xBlock, app.char.yBlock, app.char.zBlock) not in L:
            mazeMoveS(app)
            app.charStatus = None
    elif 'right' in keys:
        mazeMoveW(app)
        if (app.char.xBlock, app.char.yBlock, app.char.zBlock) not in L:
            mazeMoveE(app)
            app.charStatus = None
    elif 'left' in keys:
        mazeMoveE(app)
        if (app.char.xBlock, app.char.yBlock, app.char.zBlock) not in L:
            mazeMoveW(app)
            app.charStatus = None
############################################################


############################################################
#The ACTIVE PART: Moving around 
############################################################

##############################
#Character Class
class Char:

    def __init__(self, app):
        for a, b, c in app.map.theL:
            if a == 0 and b == app.map.dimension-1:
                self.zBlock = c
        self.xBoard = app.blockSize/2
        self.yBoard = (app.map.dimension-1)*app.blockSize + app.blockSize/2
        self.xBlock = self.xBoard//app.blockSize
        self.yBlock = self.yBoard//app.blockSize
        self.x = self.xBoard/app.blockSize
        self.y = self.yBoard/app.blockSize
        self.z = self.zBlock+1.5
        self.xCoo, self.yCoo = getBlockLFD(app, self.x, self.y, self.z)
    #Mario Sprites  #credit: Graphics from Super Mario Oddyssey #credit: AlGORITHEM FROM MIKE: https://piazza.com/class/lcnu63g1yps41j/post/1519
        app.charN1 = Image.open('MN1.png') #Mario facing North
        app.charN1 = app.charN1.convert('RGBA')
        app.charN1 = CMUImage(app.charN1)
        app.charN2 = Image.open('MN2.png')
        app.charN2 = app.charN2.convert('RGBA')
        app.charN2 = CMUImage(app.charN2)
        app.charN3 = Image.open('MN3.png')
        app.charN3 = app.charN3.convert('RGBA')
        app.charN3 = CMUImage(app.charN3)
        app.charN4 = Image.open('MN4.png')
        app.charN4 = app.charN4.convert('RGBA')
        app.charN4 = CMUImage(app.charN4)
        app.charN5 = Image.open('MN5.png')
        app.charN5 = app.charN5.convert('RGBA')
        app.charN5 = CMUImage(app.charN5)
        app.charN6 = Image.open('MN6.png')
        app.charN6 = app.charN6.convert('RGBA')
        app.charN6 = CMUImage(app.charN6)
        app.charNSprites = [app.charN1, app.charN2, app.charN3, app.charN4, app.charN5, app.charN6]
        app.charE1 = Image.open('ME1.png') #Mario Facing East
        app.charE1 = app.charE1.convert('RGBA')
        app.charE1 = CMUImage(app.charE1)
        app.charE2 = Image.open('ME2.png')
        app.charE2 = app.charE2.convert('RGBA')
        app.charE2 = CMUImage(app.charE2)
        app.charE3 = Image.open('ME3.png')
        app.charE3 = app.charE3.convert('RGBA')
        app.charE3 = CMUImage(app.charE3)
        app.charE4 = Image.open('ME4.png')
        app.charE4 = app.charE4.convert('RGBA')
        app.charE4 = CMUImage(app.charE4)
        app.charE5 = Image.open('ME5.png')
        app.charE5 = app.charE5.convert('RGBA')
        app.charE5 = CMUImage(app.charE5)
        app.charE6 = Image.open('ME6.png')
        app.charE6 = app.charE6.convert('RGBA')
        app.charE6 = CMUImage(app.charE6)
        app.charESprites = [app.charE1, app.charE2, app.charE3, app.charE4, app.charE5, app.charE6]
        app.charW1 = Image.open('MW1.png') #Mario facing West
        app.charW1 = app.charW1.convert('RGBA')
        app.charW1 = CMUImage(app.charW1)
        app.charW2 = Image.open('MW2.png')
        app.charW2 = app.charW2.convert('RGBA')
        app.charW2 = CMUImage(app.charW2)
        app.charW3 = Image.open('MW3.png')
        app.charW3 = app.charW3.convert('RGBA')
        app.charW3 = CMUImage(app.charW3)
        app.charW4 = Image.open('MW4.png')
        app.charW4 = app.charW4.convert('RGBA')
        app.charW4 = CMUImage(app.charW4)
        app.charW5 = Image.open('MW5.png')
        app.charW5 = app.charW5.convert('RGBA')
        app.charW5 = CMUImage(app.charW5)
        app.charW6 = Image.open('MW6.png')
        app.charW6 = app.charW6.convert('RGBA')
        app.charW6 = CMUImage(app.charW6)
        app.charWSprites = [app.charW1, app.charW2, app.charW3, app.charW4, app.charW5, app.charW6]
        app.charS1 = Image.open('MS1.png') #Mario facing South
        app.charS1 = app.charS1.convert('RGBA')
        app.charS1 = CMUImage(app.charS1)
        app.charS2 = Image.open('MS2.png')
        app.charS2 = app.charS2.convert('RGBA')
        app.charS2 = CMUImage(app.charS2)
        app.charS3 = Image.open('MS3.png')
        app.charS3 = app.charS3.convert('RGBA')
        app.charS3 = CMUImage(app.charS3)
        app.charS4 = Image.open('MS4.png')
        app.charS4 = app.charS4.convert('RGBA')
        app.charS4 = CMUImage(app.charS4)
        app.charS5 = Image.open('MS5.png')
        app.charS5 = app.charS5.convert('RGBA')
        app.charS5 = CMUImage(app.charS5)
        app.charS6 = Image.open('MS6.png')
        app.charS6 = app.charS6.convert('RGBA')
        app.charS6 = CMUImage(app.charS6)
        app.charSSprites = [app.charS1, app.charS2, app.charS3, app.charS4, app.charS5, app.charS6]
        app.charWin1 = Image.open('MWin1.png') #Winning Jumping Mario
        app.charWin1 = app.charWin1.convert('RGBA')
        app.charWin1 = CMUImage(app.charWin1)
        app.charWin2 = Image.open('MWin2.png')
        app.charWin2 = app.charWin2.convert('RGBA')
        app.charWin2 = CMUImage(app.charWin2)
        app.charWin3 = Image.open('MWin3.png')
        app.charWin3 = app.charWin3.convert('RGBA')
        app.charWin3 = CMUImage(app.charWin3)
        app.charWin4 = Image.open('MWin4.png')
        app.charWin4 = app.charWin4.convert('RGBA')
        app.charWin4 = CMUImage(app.charWin4)
        app.charWin5 = Image.open('MWin5.png')
        app.charWin5 = app.charWin5.convert('RGBA')
        app.charWin5 = CMUImage(app.charWin5)
        app.charWin6 = Image.open('MWin6.png')
        app.charWin6 = app.charWin6.convert('RGBA')
        app.charWin6 = CMUImage(app.charWin6)
        app.charWinSprites = [app.charWin1, app.charWin2, app.charWin3, app.charWin4, app.charWin5, app.charWin6]  
        app.ML = Image.open('ML.png') #Ladder Climbing Mario
        app.ML = app.ML.convert('RGBA') 
        app.ML = CMUImage(app.ML)

    def charMoveE(self, app):
        app.footSound.play(loop=True)
        app.charStatus = 'E'
        self.xBoard += app.dimension/1.5
        app.char.valueUpdate(app)
        self.xCoo, self.yCoo = getBlockLFD(app, self.x, self.y, self.z)

    def charMoveW(self, app):
        app.footSound.play(loop=True)
        app.charStatus = 'W'
        self.xBoard -= app.dimension/1.5
        app.char.valueUpdate(app)
        self.xCoo, self.yCoo = getBlockLFD(app, self.x, self.y, self.z)

    def charMoveN(self, app):
        app.footSound.play(loop=True)
        app.charStatus = 'N'
        self.yBoard += app.dimension/1.5
        app.char.valueUpdate(app)
        self.xCoo, self.yCoo = getBlockLFD(app, self.x, self.y, self.z)

    def charMoveS(self, app):
        app.footSound.play(loop=True)
        app.charStatus = 'S'
        self.yBoard -= app.dimension/1.5
        app.char.valueUpdate(app)
        self.xCoo, self.yCoo = getBlockLFD(app, self.x, self.y, self.z)
    
    def valueUpdate(self, app):
        self.xBlock = self.xBoard//app.blockSize
        self.yBlock = self.yBoard//app.blockSize
        self.x = self.xBoard/app.blockSize
        self.y = self.yBoard/app.blockSize
        self.z = self.zBlock+1.5

    def drawChar(self, app): #drawing the char
        if app.charStatus == 'N':
            sprite = app.charNSprites[app.spriteCounter]
            drawImage(sprite, self.xCoo, self.yCoo, align = 'center', width=100, height=100)
        elif app.charStatus == 'E':
            sprite = app.charESprites[app.spriteCounter]
            drawImage(sprite, self.xCoo, self.yCoo, align = 'center', width=100, height=100)
        elif app.charStatus == 'W':
            sprite = app.charWSprites[app.spriteCounter]
            drawImage(sprite, self.xCoo, self.yCoo, align = 'center', width=100, height=100)
        elif app.charStatus == 'S':
            sprite = app.charSSprites[app.spriteCounter]
            drawImage(sprite, self.xCoo, self.yCoo, align = 'center', width=100, height=100)
        elif app.charStatus == None:
            sprite = Image.open('MSS.png')
            sprite = sprite.convert('RGBA')
            sprite = CMUImage(sprite)
            drawImage(sprite, self.xCoo, self.yCoo, align = 'center', width=100, height=100)
        elif app.charStatus == 'up' or app.charStatus=='down':
            drawImage(app.ML, self.xCoo, self.yCoo, align = 'center', width=90, height=90)
        else:
            drawCircle(self.xCoo, self.yCoo, app.blockSize/2, fill='cyan', opacity = 70)

    def movable(self, app):
        E = [(self.xBlock, self.yBlock, self.zBlock)]
        ex, ey = self.xBlock + 1, self.yBlock
        wx, wy = self.xBlock - 1, self.yBlock
        nx, ny = self.xBlock, self.yBlock + 1
        sx, sy = self.xBlock, self.yBlock - 1
        ez = wz = nz = sz = None
        for (a, b) in app.map.heightChart:
            if (a, b) == (ex, ey):
                ez = app.map.heightChart[(a, b)]
            elif (a, b) == (wx, wy):
                wz = app.map.heightChart[(a, b)]
            elif (a, b) == (nx, ny):
                nz = app.map.heightChart[(a, b)]
            elif (a, b) == (sx, sy):
                sz = app.map.heightChart[(a, b)]
        if ez != None:
            if abs(ez - self.zBlock)<0.005:
                E.append((ex, ey, ez))
        if wz != None:
            if abs(wz - self.zBlock)<0.005:
                E.append((wx, wy, wz))
        if sz != None:
            if abs(sz - self.zBlock)<0.005:
                E.append((sx, sy, sz))
        if nz != None:
            if abs(nz - self.zBlock)<0.005:
                E.append((nx, ny, nz))
        return E
    
    def downable(self, app):
        ex, ey = self.xBlock + 1, self.yBlock
        wx, wy = self.xBlock - 1, self.yBlock
        nx, ny = self.xBlock, self.yBlock + 1
        sx, sy = self.xBlock, self.yBlock - 1
        ez = wz = nz = sz = None
        for (a, b) in app.map.heightChart:
            if (a, b) == (ex, ey):
                ez = app.map.heightChart[(a, b)]
            elif (a, b) == (wx, wy):
                wz = app.map.heightChart[(a, b)]
            elif (a, b) == (nx, ny):
                nz = app.map.heightChart[(a, b)]
            elif (a, b) == (sx, sy):
                sz = app.map.heightChart[(a, b)]
        for a, b, c in app.ladderE:
            if self.xBlock == a and self.yBlock == b:
                if ez!= None:
                    if self.xBoard-self.xBlock*app.blockSize > app.blockSize-10:
                        app.eastLadder = True
                        return (ex, ey, ez)
        for a, b, c in app.ladderW:
            if self.xBlock == a and self.yBlock == b:
                if wz != None:
                    if self.xBoard-self.xBlock*app.blockSize < 10:
                        app.eastLadder = app.northLadder = False
                        return (wx, wy, wz)
        for a, b, c in app.ladderS:
            if self.xBlock == a and self.yBlock == b:
                if sz != None:
                    if self.yBoard -self.yBlock*app.blockSize < 10:
                        app.eastLadder = app.northLadder = False
                        return (sx, sy, sz)
        for a, b, c in app.ladderN:
            if self.xBlock == a and self.yBlock == b:
                if nz != None:
                    if self.yBoard-app.blockSize*self.yBlock > app.blockSize-10:
                        app.northLadder = True
                        return (nx, ny, nz)
        return False

    def upable(self, app):
        ex, ey = self.xBlock + 1, self.yBlock
        wx, wy = self.xBlock - 1, self.yBlock
        nx, ny = self.xBlock, self.yBlock + 1
        sx, sy = self.xBlock, self.yBlock - 1
        ez = wz = nz = sz = None
        for (a, b) in app.map.heightChart:
            if (a, b) == (ex, ey):
                ez = app.map.heightChart[(a, b)]
            elif (a, b) == (wx, wy):
                wz = app.map.heightChart[(a, b)]
            elif (a, b) == (nx, ny):
                nz = app.map.heightChart[(a, b)]
            elif (a, b) == (sx, sy):
                sz = app.map.heightChart[(a, b)]
        if ez != None:
            if (ex, ey, ez) in app.ladderW: 
                if self.xBoard-self.xBlock*app.blockSize > app.blockSize-10:
                    app.eastLadder = app.northLadder = False
                    return (ex, ey, ez)
        if wz != None:
            if (wx, wy, wz) in app.ladderE:
                if self.xBoard-self.xBlock*app.blockSize < 10:
                    app.eastLadder = True
                    return (wx, wy, wz)
        if sz != None:
            if (sx, sy, sz) in app.ladderN:
                if self.yBoard-self.yBlock*app.blockSize < 10:
                    app.northLadder = True
                    return (sx, sy, sz)
        if nz != None:
            if (nx, ny, nz) in app.ladderS:
                if self.yBoard - self.yBlock*app.blockSize>app.blockSize-10:
                    app.eastLadder = app.northLadder = False
                    return (nx, ny, nz)
        return False
        
    def charMoveUp(self, app):
        app.footSound.play(loop=True)
        app.charStatus = 'up'
        self.zBlock += 0.015*app.dimension
        app.char.valueUpdate(app)
        self.xCoo, self.yCoo = getBlockLFD(app, self.x, self.y, self.z)

    def charMoveDown(self, app):
        app.footSound.play(loop=True)
        app.charStatus = 'down'
        self.zBlock -= 0.015*app.dimension
        app.char.valueUpdate(app)
        self.xCoo, self.yCoo = getBlockLFD(app, self.x, self.y, self.z)
    
    def getMoreL(self, app, T):
        L = []
        T = deepsort(T)
        for a, b, c in T:
            if self.xBlock >= a and self.yBlock >= b and c > self.zBlock:
                    L.append((a, b, c))
        return L

    def drawMoreL(self, app, T):
        C = app.char.getMoreL(app, T)
        if C != None:
            for a, b, c in C:
                drawBlock(app, a, b, c, app.blockSize)
                if (a, b) == (app.dimension-1, 0) or (a, b) == (0, app.dimension-1):
                    drawStarterBlockTop(app, a, b, c, app.blockSize)
                if (a, b, c) in app.ladderW:
                    drawLadder(app, a, b, c, app.blockSize, 'L')
                if (a, b, c) in app.ladderS:
                    drawLadder(app, a, b, c, app.blockSize, 'R')

##############################
#Fog Mode: MAZE MOVE
def mazeMoveN(app):
    app.charStatus = 'S'
    app.footSound.play(loop=True)
    app.mazeLFDX, app.mazeLFDY = getBlockLFD(app, 0, 1/10, 0)
    app.char.yBoard -= 4.5
    app.char.valueUpdate(app)
    
def mazeMoveS(app):
    app.charStatus = 'N'
    app.footSound.play(loop=True)
    app.mazeLFDX, app.mazeLFDY = getBlockLFD(app, 0, -4/30, 0)
    app.char.yBoard += 4.5
    app.char.valueUpdate(app)

def mazeMoveE(app):
    app.charStatus = 'W'
    app.footSound.play(loop=True)
    app.mazeLFDX, app.mazeLFDY = getBlockLFD(app, 1/10, -1/30, 0)
    app.char.xBoard -= 4
    app.char.valueUpdate(app)

def mazeMoveW(app):
    app.charStatus = 'E'
    app.footSound.play(loop=True)
    app.mazeLFDX, app.mazeLFDY = getBlockLFD(app, -1/10, 0, 0)
    app.char.xBoard += 4
    app.char.valueUpdate(app)
############################################################


############################################################
#the MAZE GENERATION ALGORITHM 
############################################################

##############################
#WRAPPER
def loadNew2dMap(app): #credit: This Algorithm of 2d maze generating is from PYAMAZE https://github.com/MAN1986/pyamaze/blob/main/pyamaze/pyamaze.py MAN1986
    m=maze(app.dimension, app.dimension)
    m.CreateMaze()
    mazeMap = m.maze_map
    return mazeMap

def loadNewMap(app):
    app.map = Maze(app.mazeMap, app.dimension)

class Maze:
    def __init__(self, mazeMap, dimension):
        self.mazeMap = mazeMap
        self.heightChart = moduleToMap(self.mazeMap, dimension)
        self.theL = pushAllUp(self.mazeMap, dimension)
        self.mazeMapO = systemConvert(self.mazeMap, dimension)
        self.dimension = dimension

##############################
#MAIN PART (Back Tracking) + Helper 
def systemConvert(mazeMap, dimension):
    newMap = dict()
    for cell in mazeMap:
        x = cell[1]
        y = cell[0]
        newMap[(x-1, dimension-y)] = mazeMap[cell]
    return newMap

def moduleToMap(mazeMap, dimension):
    newMap = systemConvert(mazeMap, dimension)
    return moduleToMapHelper(newMap, dict(), dimension)

def moduleToMapHelper(newMap, heightChart, dimension):
    if len(newMap) == 0:
        return heightChart
    else:
        for i in range (0, dimension):
            for t in range(0, dimension):
                cell = (i, t)
                if cell not in newMap:
                    continue
                code = newMap[cell]
                height = getHeight(cell, code, heightChart, dimension)
                if height != None:
                    if isLegalMove(cell, code, heightChart, height):
                        heightChart[cell] = height 
                        newMap.pop(cell)
                        solution = moduleToMapHelper(newMap, heightChart, dimension)
                        if solution != None:
                            return solution 
                        else:
                            newMap[cell] = code
                            heightChart.pop(cell)
    return None

def isLegalMove(cell, code, heightChart, height):
    count = 0
    x = cell[0]
    y = cell[1]
    for direction in code:
        if code[direction] == 0:
            if direction == 'E':
                checkY = y
                checkX = x + 1
            elif direction == 'W':
                checkY = y
                checkX = x - 1
            elif direction == 'N':
                checkY = y + 1
                checkX = x
            elif direction == 'S':
                checkY = y - 1
                checkX = x
            heightCheck = heightChart.get((checkX, checkY))
            if heightCheck != None:
                if heightCheck == height:
                    count += 1
        if code[direction] == 1:
            if direction == 'E':
                checkY = y
                checkX = x + 1
            elif direction == 'W':
                checkY = y
                checkX = x - 1
            elif direction == 'N':
                checkY = y + 1
                checkX = x
            elif direction == 'S':
                checkY = y - 1
                checkX = x
            heightCheck = heightChart.get((checkX, checkY))
            if heightCheck != None:
                if heightCheck != height + 1 or heightCheck != height - 1 or heightCheck != height:
                    count += 1
    if count > 2:
        return False
    return True

def getHeight(cell, code, heightChart, dimension):
    if cell == (0, 0):
        return 0
    x = cell[0]
    y = cell[1]
    checkX = None
    checkY = None
    for direction in code:
        if code[direction] == 0:
            if direction == 'E':
                checkY = y
                checkX = x + 1
            elif direction == 'W':
                checkY = y
                checkX = x - 1
            elif direction == 'N':
                checkY = y + 1
                checkX = x
            elif direction == 'S':
                checkY = y - 1
                checkX = x
            heightCheck = heightChart.get((checkX, checkY))
            if heightCheck != None:
                if heightCheck >= dimension//2:
                    return heightCheck - 1
                else:
                    return heightCheck + 1
    for direction in code:
        if code[direction] == 1:
            if direction == 'E':
                checkY = y
                checkX = x + 1
            elif direction == 'W':
                checkY = y
                checkX = x - 1
            elif direction == 'N':
                checkY = y + 1
                checkX = x
            elif direction == 'S':
                checkY = y - 1
                checkX = x
            heightCheck = heightChart.get((checkX, checkY))
            if heightCheck != None:
                return heightCheck
    return None

def finalConvertion(heightChart):
    L = []
    for t in heightChart:
        c = heightChart[t]
        a = t[0]
        b = t[1]
        L.append((a, b, c))
    return L

def pushAllUp(mazeMap, dimension):
    return finalConvertion(moduleToMap(mazeMap, dimension))

##############################
#Maze Gen Helper = following + Maze Generation SECTION
def blocksAddIn(theL, mazeMap, heightChart, ladderE, ladderW, ladderN, ladderS, dimension): #add in additional blocks
    newMap = systemConvert(mazeMap, dimension)
    for coordinate in newMap:
        x = coordinate[0]
        y = coordinate[1]
        height = heightChart[coordinate]
        code = newMap[coordinate]
        for direction in code:
            if code[direction] == 1:
                if direction == 'E':
                    checkY = y
                    checkX = x + 1
                    direction = 1
                elif direction == 'W':
                    checkY = y
                    checkX = x - 1
                    direction = 2
                elif direction == 'N':
                    checkY = y + 1
                    checkX = x
                    direction = 3
                elif direction == 'S':
                    checkY = y - 1
                    checkX = x
                    direction = 4
                heightCheck = heightChart.get((checkX, checkY))
                if heightCheck != None:
                    if heightCheck - height > 1:
                        if direction == 1:
                            ladderW.add((checkX, checkY, heightCheck))
                            for i in range(1, heightCheck-height):
                                theL.append((checkX, checkY, heightCheck-i))
                                ladderW.add((checkX, checkY, heightCheck-i))
                        elif direction == 2:
                            ladderE.add((checkX, checkY, heightCheck))
                            for i in range(1, heightCheck-height):
                                theL.append((checkX, checkY, heightCheck-i))
                                ladderE.add((checkX, checkY, heightCheck-i))
                        elif direction == 3:
                            ladderS.add((checkX, checkY, heightCheck))
                            for i in range(1, heightCheck-height):
                                theL.append((checkX, checkY, heightCheck-i))
                                ladderS.add((checkX, checkY, heightCheck-i))
                        elif direction == 4:
                            ladderN.add((checkX, checkY, heightCheck))
                            for i in range(1, heightCheck-height):
                                theL.append((checkX, checkY, heightCheck-i))
                                ladderN.add((checkX, checkY, heightCheck-i))
                    elif heightCheck - height < -1:
                        if direction == 1:
                            ladderE.add((x, y, height))
                            for i in range(1, height-heightCheck):
                                theL.append((x, y, height-i))
                                ladderE.add((x, y, height-i))
                        elif direction == 2:
                            ladderW.add((x, y, height))
                            for i in range(1, height-heightCheck):
                                theL.append((x, y, height-i))
                                ladderW.add((x, y, height-i))
                        elif direction == 3:
                            ladderN.add((x, y, height))
                            for i in range(1, height-heightCheck):
                                theL.append((x, y, height-i))
                                ladderN.add((x, y, height-i))
                        elif direction == 4:
                            ladderS.add((x, y, height))
                            for i in range(1, height-heightCheck):
                                theL.append((x, y, height-i))
                                ladderS.add((x, y, height-i))
    return theL, ladderE, ladderW, ladderN, ladderS

def deepsort(L):  #sort the block list to draw correctly
    X = copy.deepcopy(L)
    X.sort(key=lambda tuple: tuple[2])
    z1 = X[0][2]
    z2 = X[-1][2]
    R = []
    for zValue in range(z1, z2+1):
        T = []
        for x, y, z in X:
            if z == zValue: 
                T.append((x, y, z))
        T.sort(key=lambda tuple:tuple[0], reverse=True)
        T.sort(key=lambda tuple:tuple[1], reverse=True)
        R.extend(T)
    return R

def getLadder(mazeMap, heightChart, dimension): #get where the ladders are based on the map 
    ladderW = set()
    ladderS = set()
    ladderE = set()
    ladderN = set()
    newMap = systemConvert(mazeMap, dimension)
    for coordinate in newMap:
        x = coordinate[0]
        y = coordinate[1]
        height = heightChart[coordinate]
        code = newMap[coordinate]
        for direction in code:
            if code[direction] == 1:
                if direction == 'E':
                    checkY = y
                    checkX = x + 1
                    direction = 1
                elif direction == 'W':
                    checkY = y
                    checkX = x - 1
                    direction = 2
                elif direction == 'N':
                    checkY = y + 1
                    checkX = x
                    direction = 3
                elif direction == 'S':
                    checkY = y - 1
                    checkX = x
                    direction = 4
                heightCheck = heightChart.get((checkX, checkY))
                if heightCheck != None:
                    if heightCheck - height == 1:
                        if direction == 1:
                            ladderW.add((checkX, checkY, heightCheck))
                        elif direction == 2:
                            ladderE.add((checkX, checkY, heightCheck))
                        elif direction == 3:
                            ladderS.add((checkX, checkY, heightCheck))
                        elif direction == 4:
                            ladderN.add((checkX, checkY, heightCheck))
                    elif heightCheck - height == -1:
                        if direction == 1:
                            ladderE.add((coordinate[0], coordinate[1], height))
                        elif direction == 2:
                            ladderW.add((coordinate[0], coordinate[1], height))
                        elif direction == 3:
                            ladderN.add((coordinate[0], coordinate[1], height))
                        elif direction == 4:
                            ladderS.add((coordinate[0], coordinate[1], height))
    return ladderE, ladderW, ladderN, ladderS
############################################################


############################################################
#The 'DELIVERABLE': Drawing it Out 
############################################################

##############################
#Start Interface
def drawStartInterface(app):
    drawBackground(app)  
    drawLabel('Creator: Archi.Axolotl.Rong', 600, 60, font='Rockwell', fill = app.color.sCubeFC, size = 15)
    drawLabel('Dedicated to the MOST SPECIAL TIME, NOW', 600, 90, font='Rockwell', fill = app.color.sCubeFC, size = 15)
    drawLabel("Special Credit: Jia.Rong'sXiGouFriend.bothFailedtoBecomeVinay",  600, 120, font='Rockwell', fill = app.color.sCubeFC, size = 15)
    drawLabel('not UTOPIA', 600, 210, fill = app.color.sWordsC, font='Kefa', size = 120, bold = True)
    drawColorSelection(app)
    drawModeSelection(app)
    drawDimensionSelection(app)
    drawRect(1020, 470, 240, 100, fill = app.color.sWordsC, align='center', opacity = 30)
    drawLabel('START', 1020, 470, fill = app.color.sBackgroundC, size = 45, font='Kefa', bold = True, opacity = 30)

def drawColorSelection(app): 
    drawLabel('Select Color', 250, 360, fill = app.color.sWordsC, font='Kefa', size = 35, bold = True)
    drawRect(760, 360, 200, 60, fill = rgb(14, 131, 136), align = 'center')
    drawLabel('ALLEGHENY', 760, 360, fill = rgb(44, 51, 51), font='Kefa', size = 30, bold = True)
    drawRect(520, 360, 200, 60, fill = rgb(65, 100, 74), align = 'center')
    drawLabel('SCHENLEY', 520, 360, fill = rgb(232, 106, 51), font='Kefa', size = 30, bold = True)
    drawRect(1000, 360, 200, 60, fill = rgb(243, 233, 159), align = 'center')
    drawLabel('Squirrel HILL', 1000, 360, fill = rgb(255, 109, 96), font='Kefa', size = 30, bold = True)

def drawModeSelection(app):
    drawLabel('Select Mode', 248, 470, fill = app.color.sWordsC, font='Kefa', size = 35, bold = True)
    drawRect(520, 470, 200, 60, fill = app.color.sCubeTC, align = 'center')
    drawLabel('SUNNY', 520, 470, fill = app.color.sBackgroundC, font='Kefa', size = 30, bold = True)
    drawRect(760, 470, 200, 60, fill = app.color.sCubeTC, align = 'center')
    drawLabel('FOGGY', 760, 470, fill = app.color.sBackgroundC, font='Kefa', size = 30, bold = True)

def drawDimensionSelection(app):
    drawLabel('Select Difficulty', 250, 580, fill = app.color.sWordsC, font='Kefa', size = 35, bold = True)
    drawRect(520, 580, 200, 60, fill = app.color.sCubeLC, align = 'center')
    drawLabel('6 x 6', 520, 580, fill = app.color.sBackgroundC, font='Kefa', size = 30, bold = True)
    drawRect(760, 580, 200, 60, fill = app.color.sCubeLC, align = 'center')
    drawLabel('8 x 8', 760, 580, fill = app.color.sBackgroundC, font = 'Kefa', size = 30, bold = True)
    drawRect(1000, 580, 200, 60, fill = app.color.sCubeLC, align = 'center')
    drawLabel('10 x 10', 1000, 580, fill = app.color.sBackgroundC, font='Kefa', size = 30, bold = True)

def drawSelected(app):
    if app.index == 1:
        drawRect(520, 360, 200, 60, border = app.color.sWordsC, align = 'center', fill = None, borderWidth=6)
    elif app.index == 2:
        drawRect(760, 360, 200, 60, border = app.color.sWordsC, align = 'center', fill = None, borderWidth=6)
    elif app.index == 3:
        drawRect(1000, 360, 200, 60, border = app.color.sWordsC, align = 'center', fill = None, borderWidth=6)
    if app.fogMode:
        drawRect(760, 470, 200, 60, border = app.color.sWordsC, align = 'center', fill = None, borderWidth=6)
    elif app.sunnyMode:
        drawRect(520, 470, 200, 60, border = app.color.sWordsC, align = 'center', fill = None, borderWidth=6)
    if app.dimension == 6:
        drawRect(520, 580, 200, 60, border = app.color.sWordsC, align = 'center', fill = None, borderWidth=6)
    elif app.dimension == 8:
        drawRect(760, 580, 200, 60, border = app.color.sWordsC, align = 'center', fill = None, borderWidth=6)
    elif app.dimension == 10:
        drawRect(1000, 580, 200, 60, border = app.color.sWordsC, align = 'center', fill = None, borderWidth=6)

############################################################
#Draw Maze 
#START: Call MAZE GENERATION
def mapInitials(app):
    app.xCoo = 0
    app.yCoo = 0
    app.zCoo = 0
    app.blockSize = 40
    app.charStatus = None
    app.spriteCounter = 0
    app.northLadder = False
    app.eastLadder = False
    if app.fogMode:
        app.mazeLFDX = 800 #LeftFrontDownXCoordinate
        app.mazeLFDY = 633 #LeftFrontDownYCoordinate
    if app.sunnyMode:
        app.mazeLFDX = 555 #LeftFrontDownXCoordinate
        app.mazeLFDY = 633 #LeftFrontDownYCoordinate

def getTheMapDone(app): #Call Maze class, which calls maze generating function, and get the lists
    theL = app.map.theL
    theL = deepsort(theL)
    ladderE, ladderW, ladderN, ladderS = getLadder(app.map.mazeMap, app.map.heightChart, app.dimension)
    theL, app.ladderE, app.ladderW, app.ladderN, app.ladderS = blocksAddIn(theL, app.map.mazeMap, app.map.heightChart, ladderE, ladderW, ladderN, ladderS, app.dimension)
    app.map.theL = deepsort(theL)

##############################
#Drawing WRAPPER
def drawMap(app):
    drawBackground(app)
    theL = app.map.theL
    theL = deepsort(theL)
    mazeMapO = app.map.mazeMapO
    mazeMap = app.map.mazeMap
    heightChart = app.map.heightChart
    for a, b, c in theL:
        drawBlock(app, a, b, c, app.blockSize)
        if (a, b) == (app.dimension-1, 0) or (a, b) == (0, app.dimension-1):
            drawStarterBlockTop(app, a, b, c, app.blockSize)
        if (a, b, c) in app.ladderW:
            drawLadder(app, a, b, c, app.blockSize, 'L')
        if (a, b, c) in app.ladderS:
            drawLadder(app, a, b, c, app.blockSize, 'R')

def drawMapFog(app):
    drawBackground(app)
    L = getMapFog(app)
    for a, b, c in L:
        drawBlock(app, a, b, c, app.blockSize)
        if (a, b) == (app.dimension-1, 0) or (a, b) == (0, app.dimension-1):
            drawStarterBlockTop(app, a, b, c, app.blockSize)
        if (a, b, c) in app.ladderW:
            drawLadder(app, a, b, c, app.blockSize, 'L')
        if (a, b, c) in app.ladderS:
            drawLadder(app, a, b, c, app.blockSize, 'R')

def getMapFog(app):
    x = app.char.xBlock
    y = app.char.yBlock
    L = []
    for a, b, c in deepsort(app.map.theL):
        if (abs(a-x)<=1) and(abs(b-y)<=1):
            L.append((a, b, c))
    return L

def drawBackground(app):
    drawRect(0, 0, 1200, 800, fill = app.color.sBackgroundC, opacity = 60)

##############################
#Sunny Mode Get Coins Feature 
def getCoins(app):
    L = []
    while len(L) < app.dimension-3:
        x = random.randint(0, app.dimension-1)
        y = random.randint(0, app.dimension-1)
        if x == 0 and y == app.dimension-1:
            continue
        elif x == app.dimension-1 and y == 0:
            continue
        else:
            if (x, y) not in L:
                L.append((x, y))
    return L

def get2dCoodinate(app):
    x = 1000 + app.char.xBlock*(120/app.dimension) + (120/app.dimension/2)
    y = 620 - app.char.yBlock*(120/app.dimension) - (120/app.dimension/2)
    return x, y

def drawCoins(app):
    for a, b in app.coins:
        drawLabel('R', 1000+120/app.dimension*(a+1/2), 620-120/app.dimension*(b+1/2), fill = app.color.sWordsC, font = 'Wingdings', size = 20, bold = True)
    for i in range(len(app.coins)):
        drawLabel('R', 1110-i*40, 645, fill = app.color.sCubeFC, font = 'Wingdings', size = 45, bold = True, opacity = 50)
    for a, b in app.gotCoins:
        drawLabel('R', 1000+120/app.dimension*(a+1/2), 620-120/app.dimension*(b+1/2), fill = app.color.sCubeFC, font = 'Wingdings', size = 20, bold = True)
    for i in range(len(app.gotCoins)):
        drawLabel('R', 1110-i*40, 645, fill = app.color.sWordsC, font = 'Wingdings', size = 45, bold = True)

##############################
#DrawLadder
def drawLadder(app, xCoo, yCoo, zCoo, size, direction): #draw individual Ladder given the ladder coo. 
    if direction == 'L':
        blockLFDX, blockLFDY = getBlockLFD(app, xCoo, yCoo, zCoo)
        blockLFUX, blockLFUY = getBlockLFD(app, xCoo, yCoo, zCoo+1)
        blockLBDX, blockLBDY = getBlockLFD(app, xCoo, yCoo+1, zCoo)
        blockLBUX, blockLBUY = getBlockLFD(app, xCoo, yCoo+1, zCoo+1)
        ladderLFDX, ladderLFDY = blockLFDX-(blockLFDX - blockLBDX)/4, blockLFDY-(blockLFDY-blockLBDY)/4
        ladderLBDX, ladderLBDY = blockLBDX+(blockLFDX - blockLBDX)/4, blockLBDY+(blockLFDY-blockLBDY)/4
        ladderLFUX, ladderLFUY = ladderLFDX, ladderLFDY - size
        ladderLBUX, ladderLBUY = ladderLBDX, ladderLBDY - size
        drawLine(ladderLFDX, ladderLFDY, ladderLFUX, ladderLFUY, fill = app.color.sWordsC, lineWidth = 4)
        drawLine(ladderLBDX, ladderLBDY, ladderLBUX, ladderLBUY, fill = app.color.sWordsC, lineWidth = 4)
        for i in range(1, 5):
            drawLine(ladderLFDX, ladderLFDY-i*0.25*size, ladderLBDX, ladderLBDY-i*0.25*size, fill = app.color.sWordsC, lineWidth = 3)
    elif direction == 'R':
        blockRFDX, blockRFDY = getBlockLFD(app, xCoo+1, yCoo, zCoo)
        blockRFUX, blockRFUY = getBlockLFD(app, xCoo+1, yCoo, zCoo+1)
        blockLFDX, blockLFDY = getBlockLFD(app, xCoo, yCoo, zCoo)
        blockLFUX, blockLFUY = getBlockLFD(app, xCoo, yCoo, zCoo+1)
        ladderRFDX, ladderRFDY = blockLFDX+(blockRFDX - blockLFDX)/4, blockLFDY-(blockLFDY-blockRFDY)/4
        ladderRBDX, ladderRBDY = blockRFDX-(blockRFDX - blockLFDX)/4, blockRFDY+(blockLFDY-blockRFDY)/4
        ladderRFUX, ladderRFUY = ladderRFDX, ladderRFDY - size
        ladderRBUX, ladderRBUY = ladderRBDX, ladderRBDY - size
        drawLine(ladderRFDX, ladderRFDY, ladderRFUX, ladderRFUY, fill = app.color.sWordsC, lineWidth = 4)
        drawLine(ladderRBDX, ladderRBDY, ladderRBUX, ladderRBUY, fill = app.color.sWordsC, lineWidth = 4)
        for i in range(1, 5):
            drawLine(ladderRFDX, ladderRFDY-i*0.25*size, ladderRBDX, ladderRBDY-i*0.25*size, fill = app.color.sWordsC, lineWidth = 3)

##############################
#DrawBlock
def drawBlock(app, xCoo, yCoo, zCoo, size):
    blockLFDX, blockLFDY = getBlockLFD(app, xCoo, yCoo, zCoo)
    blockLFUX, blockLFUY = getBlockLFD(app, xCoo, yCoo, zCoo+1)
    blockRFDX, blockRFDY = getBlockLFD(app, xCoo+1, yCoo, zCoo)
    blockRFUX, blockRFUY = getBlockLFD(app, xCoo+1, yCoo, zCoo+1)
    blockLBDX, blockLBDY = getBlockLFD(app, xCoo, yCoo+1, zCoo)
    blockLBUX, blockLBUY = getBlockLFD(app, xCoo, yCoo+1, zCoo+1)
    blockRBDX, blockRBDY = getBlockLFD(app, xCoo+1, yCoo+1, zCoo)
    blockRBUX, blockRBUY = getBlockLFD(app, xCoo+1, yCoo+1, zCoo+1)
    #Front
    drawPolygon(blockLFDX, blockLFDY, blockLFUX, blockLFUY, blockRFUX, blockRFUY, blockRFDX, blockRFDY, border=app.color.sLineC, fill=app.color.sCubeFC, borderWidth = 1.5)
    #Left
    drawPolygon(blockLFDX, blockLFDY, blockLFUX, blockLFUY, blockLBUX, blockLBUY, blockLBDX, blockLBDY, border=app.color.sLineC, fill=app.color.sCubeLC, borderWidth = 1.5)
    #Top
    drawPolygon(blockLFUX, blockLFUY, blockRFUX, blockRFUY, blockRBUX, blockRBUY, blockLBUX, blockLBUY, border=app.color.sLineC, fill=app.color.sCubeTC, borderWidth = 1.5)

def getBlockLFD(app, xCoo, yCoo, zCoo):
    blockLFDX = int(app.mazeLFDX + xCoo*(app.blockSize*math.cos(18/180*math.pi)) - yCoo*(app.blockSize*math.cos(45/180*math.pi)))
    blockLFDY = int(app.mazeLFDY-yCoo*(app.blockSize*math.sin(45/180*math.pi))*0.9-zCoo*app.blockSize-xCoo*(app.blockSize*math.sin(18/180*math.pi)))
    return (blockLFDX, blockLFDY)

##############################
#Draw Art, Draw Back Buttons, Draw Instructions, Draw MiniMap, Draw Win Map
def drawStarterBlockTop(app, xCoo, yCoo, zCoo, size): 
    blockLFUX, blockLFUY = getBlockLFD(app, xCoo, yCoo, zCoo+1)
    blockRFUX, blockRFUY = getBlockLFD(app, xCoo+1, yCoo, zCoo+1)
    blockLBUX, blockLBUY = getBlockLFD(app, xCoo, yCoo+1, zCoo+1)
    blockRBUX, blockRBUY = getBlockLFD(app, xCoo+1, yCoo+1, zCoo+1)
    drawPolygon(blockLFUX, blockLFUY, blockRFUX, blockRFUY, blockRBUX, blockRBUY, blockLBUX, blockLBUY, border=app.color.sLineC, fill=app.color.sWordsC, borderWidth = 1.5)
    drawPolygon(blockLFUX+(blockRFUX-blockLFUX)/5, blockLFUY-(blockLFUY-blockRFUY)/5, blockLFUX+(blockRFUX-blockLFUX)/5*2, blockLFUY-(blockLFUY-blockRFUY)/5*2, blockLBUX+(blockRFUX-blockLFUX)/5*2, blockLBUY-(blockLFUY-blockRFUY)/5*2, blockLBUX+(blockRFUX-blockLFUX)/5, blockLBUY-(blockLFUY-blockRFUY)/5, fill = app.color.sLineC, opacity = 80)
    drawPolygon(blockLFUX+(blockRFUX-blockLFUX)/5*3, blockLFUY-(blockLFUY-blockRFUY)/5*3, blockLFUX+(blockRFUX-blockLFUX)/5*4, blockLFUY-(blockLFUY-blockRFUY)/5*4, blockLBUX+(blockRFUX-blockLFUX)/5*4, blockLBUY-(blockLFUY-blockRFUY)/5*4, blockLBUX+(blockRFUX-blockLFUX)/5*3, blockLBUY-(blockLFUY-blockRFUY)/5*3, fill = app.color.sLineC, opacity = 80)
    drawPolygon(blockLBUX+(blockLFUX-blockLBUX)/5, blockLBUY+(blockLFUY-blockLBUY)/5, blockLBUX+(blockLFUX-blockLBUX)/5*2, blockLBUY+(blockLFUY-blockLBUY)/5*2, blockRBUX+(blockLFUX-blockLBUX)/5*2, blockRBUY+(blockLFUY-blockLBUY)/5*2, blockRBUX+(blockLFUX-blockLBUX)/5, blockRBUY+(blockLFUY-blockLBUY)/5, fill = app.color.sLineC, opacity = 80)
    drawPolygon(blockLBUX+(blockLFUX-blockLBUX)/5*3, blockLBUY+(blockLFUY-blockLBUY)/5*3, blockLBUX+(blockLFUX-blockLBUX)/5*4, blockLBUY+(blockLFUY-blockLBUY)/5*4, blockRBUX+(blockLFUX-blockLBUX)/5*4, blockRBUY+(blockLFUY-blockLBUY)/5*4, blockRBUX+(blockLFUX-blockLBUX)/5*3, blockRBUY+(blockLFUY-blockLBUY)/5*3, fill = app.color.sLineC, opacity = 80)

def drawBackButton(app):
    drawRect(50, 30, 200, 80, fill = app.color.sCubeFC, border = app.color.sLineC, borderWidth = 4, opacity = 80)
    drawLabel('ToMain', 150, 70, fill = app.color.sWordsC, size=40, font = 'Kefa', bold = True)

def drawInstructionBlock(app, x, y, size):
    x1, y1 = x-size*math.cos(45/180*math.pi), y-size*math.cos(45/180*math.pi)-size
    x2, y2 = x+size*math.cos(18/180*math.pi)-size*math.cos(45/180*math.pi), y-size*math.sin(18/180*math.pi)-size-size*math.cos(45/180*math.pi)
    x3, y3 = x+size*math.cos(18/180*math.pi), y-size*math.sin(18/180*math.pi)-size
    drawLine(x2, y2, x2, y2+size, fill = app.color.sLineC, lineWidth = 3)
    drawLine(x2, y2+size, x-size*math.cos(45/180*math.pi), y-size*math.cos(45/180*math.pi), fill = app.color.sLineC, lineWidth = 3)
    drawLine(x2, y2+size, x+size*math.cos(18/180*math.pi), y-size*math.sin(18/180*math.pi), fill = app.color.sLineC, lineWidth = 3)
    drawLine(x1+(x2-x1)/4, y2+(y1-y2)/4*3,  x1+(x2-x1)/4, y2+(y1-y2)/4*3+size, fill = app.color.sWordsC, lineWidth = 4)
    drawLine(x1+(x2-x1)/4*3, y2+(y1-y2)/4,  x1+(x2-x1)/4*3, y2+(y1-y2)/4+size, fill = app.color.sWordsC, lineWidth = 4)
    drawLine(x2+(x3-x2)/4, y2+(y3-y2)/4, x2+(x3-x2)/4, y2+(y3-y2)/4+size, fill = app.color.sWordsC, lineWidth = 4)
    drawLine(x2+(x3-x2)/4*3, y2+(y3-y2)/4*3, x2+(x3-x2)/4*3, y2+(y3-y2)/4*3+size, fill = app.color.sWordsC, lineWidth = 4)
    for i in range(3):
        drawLine(x1+(x2-x1)/4, y2+(y1-y2)/4*3+size/4*(i+1), x1+(x2-x1)/4*3, y2+(y1-y2)/4+size/4*(i+1), fill = app.color.sWordsC, lineWidth = 3)
        drawLine(x2+(x3-x2)/4, y2+(y3-y2)/4+size/4*(i+1), x2+(x3-x2)/4*3, y2+(y3-y2)/4*3+size/4*(i+1), fill = app.color.sWordsC, lineWidth = 3)
    drawPolygon(x, y, x, y-size, x-size*math.cos(45/180*math.pi), y-size*math.cos(45/180*math.pi)-size, x-size*math.cos(45/180*math.pi), y-size*math.cos(45/180*math.pi), border=app.color.sLineC, fill=app.color.sCubeLC, borderWidth = 2, opacity = 60)
    drawPolygon(x, y, x, y-size, x+size*math.cos(18/180*math.pi), y-size*math.sin(18/180*math.pi)-size, x+size*math.cos(18/180*math.pi), y-size*math.sin(18/180*math.pi), border=app.color.sLineC, fill=app.color.sCubeFC, borderWidth = 2, opacity = 60)
    drawPolygon(x, y-size, x+size*math.cos(18/180*math.pi), y-size*math.sin(18/180*math.pi)-size, x+size*math.cos(18/180*math.pi)-size*math.cos(45/180*math.pi), y-size*math.sin(18/180*math.pi)-size-size*math.cos(45/180*math.pi), x-size*math.cos(45/180*math.pi), y-size*math.cos(45/180*math.pi)-size, border=app.color.sLineC, fill=app.color.sCubeTC, borderWidth = 2, opacity = 60)
    if app.northLadder:
        drawLine(x1+(x2-x1)/4, y2+(y1-y2)/4*3,  x1+(x2-x1)/4, y2+(y1-y2)/4*3+size, fill = app.color.sWordsC, lineWidth = 4)
        drawLine(x1+(x2-x1)/4*3, y2+(y1-y2)/4,  x1+(x2-x1)/4*3, y2+(y1-y2)/4+size, fill = app.color.sWordsC, lineWidth = 4)
        for i in range(3):
            drawLine(x1+(x2-x1)/4, y2+(y1-y2)/4*3+size/4*(i+1), x1+(x2-x1)/4*3, y2+(y1-y2)/4+size/4*(i+1), fill = app.color.sWordsC, lineWidth = 3)
    if app.eastLadder:
        drawLine(x2+(x3-x2)/4, y2+(y3-y2)/4, x2+(x3-x2)/4, y2+(y3-y2)/4+size, fill = app.color.sWordsC, lineWidth = 4)
        drawLine(x2+(x3-x2)/4*3, y2+(y3-y2)/4*3, x2+(x3-x2)/4*3, y2+(y3-y2)/4*3+size, fill = app.color.sWordsC, lineWidth = 4)
        for i in range(3):
            drawLine(x2+(x3-x2)/4, y2+(y3-y2)/4+size/4*(i+1), x2+(x3-x2)/4*3, y2+(y3-y2)/4*3+size/4*(i+1), fill = app.color.sWordsC, lineWidth = 3)

def drawKeyInstruction(app):
    drawLabel('c', 240, 580, fill = app.color.sLineC, size = 80,font = 'Wingdings 3', rotateAngle = 45)
    drawLabel('UP DOWN RIGHT LEFT', 270, 620, fill = app.color.sWordsC, size=20, font = 'Kefa', bold = True, rotateAngle = -25)
    drawLabel('c', 183, 520, fill = app.color.sLineC, size = 80,font = 'Wingdings 3', rotateAngle = -135)
    drawLabel('e', 300, 540, fill = app.color.sLineC, size = 80,font = 'Wingdings 3', rotateAngle = -25)
    drawLabel('e', 160, 600, fill = app.color.sLineC, size = 80,font = 'Wingdings 3', rotateAngle = 155)
    drawLabel('Y', 60, 360, fill = app.color.sLineC, size = 80, font = 'Wingdings 3')
    drawLabel('SPACE+UP', 100, 360, fill = app.color.sWordsC, size = 20,font = 'Kefa', bold = True, align = 'left')
    drawLabel('Y', 60, 430, fill = app.color.sLineC, size = 80, font = 'Wingdings 3', rotateAngle = 180)
    drawLabel('SPACE+DOWN', 100, 430, fill = app.color.sWordsC, size = 20,font = 'Kefa', bold = True, align = 'left')

def drawFogModeInstructions(app):
    drawLabel('Goal: ', 800, 50, fill = app.color.sLineC, size = 25, align = 'left', bold = True, opacity = 90, font = 'Kefa')
    drawLabel('It is a foggy day today, ', 820, 90, fill = app.color.sLineC, size = 22, align = 'left', bold = True, opacity= 80, font = 'Kefa')
    drawLabel('But you still need to go to class', 847, 120, fill = app.color.sLineC, size = 22, align = 'left', bold = True, opacity= 80, font = 'Kefa')
    drawLabel('Go from TOP LEFT Corner', 874, 150, fill = app.color.sLineC, size = 22, align = 'left', bold = True, opacity = 100, font = 'Kefa')
    drawLabel('to DOWN RIGHT Corner', 901, 180, fill = app.color.sLineC, size = 22, align = 'left', bold = True, opacity = 100, font = 'Kefa')
    drawInstructionBlock(app, 1050, 400, 70)

def drawSunnyModeInstructions(app):
    drawLabel('Goal: ', 800, 50, fill = app.color.sLineC, size = 25, align = 'left', bold = True, opacity = 90, font = 'Kefa')
    drawLabel('It is a sunny day today, ', 820, 90, fill = app.color.sLineC, size = 22, align = 'left', bold = True, opacity= 80, font = 'Kefa')
    drawLabel('Collect ALL SUNS around', 847, 120, fill = app.color.sLineC, size = 22, align = 'left', bold = True, opacity= 80, font = 'Kefa')
    drawLabel('Go from TOP LEFT Corner', 874, 150, fill = app.color.sLineC, size = 22, align = 'left', bold = True, opacity = 100, font = 'Kefa')
    drawLabel('to DOWN RIGHT Corner', 901, 180, fill = app.color.sLineC, size = 22, align = 'left', bold = True, opacity = 100, font = 'Kefa')
    drawInstructionBlock(app, 1050, 400, 70)

def drawMiniMap(app):
    drawLabel('Mini Map', 1060, 480, fill = app.color.sWordsC, bold = True, size = 23, opacity = 80, font = 'Kefa')
    drawRect(1000, 500, 120, 120, border = app.color.sLineC, fill = app.color.sCubeFC, borderWidth = 3, opacity = 80)
    if app.sunnyMode:
        drawCoins(app)
    drawRect(1000, 500, 120/app.dimension, 120/app.dimension, fill = app.color.sCubeTC, border=app.color.sWordsC)
    drawRect(1120-120/app.dimension, 620-120/app.dimension, 120/app.dimension, 120/app.dimension, fill = app.color.sCubeTC, border=app.color.sWordsC)
    x, y = get2dCoodinate(app)
    drawCircle(x, y, 10, fill = app.color.sWordsC)
    drawCircle(x, y, 6, fill = app.color.sLineC)
    drawCircle(x, y, 3, fill = app.color.sWordsC)

def drawWinMap(app):
    drawMap(app) #redrawMap
    sprite = app.charWinSprites[app.spriteCounter] #draw jumping Mario
    drawImage(sprite, app.char.xCoo+20, app.char.yCoo-70, align = 'center', width=100, height=200)
    drawLabel('You Made It!', 600, 350, fill = app.color.sWordsC, size = 180, align = 'center', font = 'kefa', bold = True) #drawLabel
############################################################


def main():
    runApp()

main()