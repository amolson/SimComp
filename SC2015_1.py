# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 08:34:05 2015

@author: amolson
"""

import pygame, sys
from pygame.locals import *

#Initialize code
pygame.init()
fpsClock = pygame.time.Clock()
pygame.key.set_mods(KMOD_CAPS)

size = (1000, 480)

screen=pygame.display.set_mode(size)

pygame.display.set_caption('Simulated Computer')

red = pygame.Color(255, 0, 0)
green = pygame.Color(64, 255, 0)
blue = pygame.Color(0, 0, 255)
white = pygame.Color(255, 255, 255)
black = pygame.Color(0, 0, 0)

#Starting Information
mousex, mousey = 0, 0
memArray = ['']*32
fps = 30

mnem = [['STP', 'LDA', 'STA', 'ADD', 'SUB', 'MUL', 'DIV', 'INP', 'OUT',
        'JMP', 'MOD', 'NEG', 'RND'], 
        ['SKZ', 'SNZ', 'SLZ', 'SGZ', 'SPS', 'SNG'],
        ['JPZ', 'JNZ', 'JLZ', 'JGZ', 'JPS', 'JNG'],
        ['AND', 'NOR', 'ORL', 'XOR', 'INV', 'SHL'
        'SHR', 'ROL', 'ROR']]

#pull from tuple
X = 0
Y = 1
width = 2
height = 3

scale = (100, 100)

#Base locations for modules, out of 100
memoryBaseLocation = (50, 15)
CPUBaseLocation = (2, 76)
screenBaseLocation = (2, 2)
runBaseLocation = (80, 5)
baseBaseLocation = (54, 5)

#Fonts
memAddressFont = pygame.font.Font(None, 25)
memValFont = pygame.font.Font(None, 45)

CPULabelFont = pygame.font.Font(None, 30)
CPUValFont = pygame.font.Font(None, 50)

screenFont = pygame.font.Font(None, 70)

controlFont = pygame.font.Font(None, 40)

#Print functions
def buildMemLabels(numType, addressType):
    arr = []
    if numType == 'Dec' and addressType == 'Direct':
        for i in range(32):
            arr.append(str(i))
    if numType == 'Hex':
        for i in range(32):
            arr.append(str(hex(i))[2:])
    return arr
    
def memAddPrint(s, location):
    output = memAddressFont.render(s, 1, black)
    screen.blit(output, (location[X], 
                        location[Y]))
                        
def memValPrint(s, location):
    output = CPUValFont.render(s, 1, white)
    soutput = output.get_size()
    screen.blit(output, (location[X]-soutput[X] + location[width], 
                        location[Y]-soutput[Y] + location[height]))
                        
def drawMemory(memArray, location):
    for i in range(32):
        memLocation = (location[X] + ((i/8) * 100*scale[X]/100),
                       location[Y] + ((i % 8) * 50*scale[Y]/100), 
                        90*scale[X]/100, 45*scale[Y]/100)
        pygame.draw.rect(screen, red, memLocation)
                                                 
        memAddPrint(str(memLabels[i]), memLocation)
        
        memValPrint(str(memArray[i]), memLocation)
    return memArray
    
def CPULabels(CPUType):
    arr = ['EXEC', 'ACC', 'INC', 'PC', 'FETCH', 'IR' ]
    return arr
    
def CPULabelPrint(s, location):
    output = CPULabelFont.render(s, 1, black)
    screen.blit(output, (location[X], 
                        location[Y]))
    
def CPUValPrint(s, location):
    output = CPUValFont.render(s, 1, white)
    soutput = output.get_size()
    screen.blit(output, ((location[X]-soutput[X] + location[width], 
                        location[Y]-soutput[Y] + location[height])))
    
def drawCPU(s, location):
    tempFont = pygame.font.Font(None, 70) 
    output = tempFont.render('CPU', 1, black)
    soutput = output.get_size()
    tempOutL = (location[X] + ((150+soutput[0]/4)*scale[X]/100),
                       location[Y] - (50*scale[Y]/100))
    screen.blit(output, tempOutL)
    for i in range(6):
        CPULocation = (location[X] + ((i/2) * 150*scale[X]/100),
                       location[Y] + ((i%2) * 50*scale[Y]/100),
                        140*scale[X]/100, 45*scale[Y]/100)
                        
        pygame.draw.rect(screen, blue, CPULocation)
        
        CPULabelPrint(str(CPULabels[i]), CPULocation)
        
        CPUValPrint(str(s[i]), CPULocation)
    return CPULocation
    
def screenValPrint(s, location):
    output = screenFont.render(s, 1, black)
    soutput = output.get_size()
    screen.blit(output, (location[X] + location[width], 
                        location[Y]-soutput[1] + location[height]))
    
def drawScreen(s, location):
    screenLocation = (location[X], location[Y], 
                      450*scale[X]/100, 300*scale[Y]/100)
                      
    pygame.draw.rect(screen, green, screenLocation)
    
    for i in range(5):
        screenLocation = (location[X],
                       location[Y] - i*60*scale[Y]/100,
                        10*scale[X]/100, 300*scale[Y]/100)
                        
        screenValPrint(str(s[i]), screenLocation)
        
def drawRun(run, location):
    output = controlFont.render(run, 1, white, black)
    runr = pygame.Rect(output.get_rect())
    runrect = runr.move(location)
    screen.blit(output, location)
    
    return runrect
    
def drawBase(base, location):
    output = controlFont.render(base, 1, white, black)
    baser = pygame.Rect(output.get_rect())
    baserect = baser.move(location)
    screen.blit(output, location)
    
    return baserect

#flags

runflag = False #False, paused: True, running
baseflag = 'Hex' #Hex or Dec
runtypeflag = 'Step' #Step or Free
addressflag = 'Direct' #Direct addressing or xy, bank/location addressing
CPUflag = 'Normal' #Place holder for possible future variations
loadflag = False #False, not loading: True, loading
inputflag = False #False, not taking in put: True, taking input
flags = {'run':runflag, 'base':baseflag, 'runtype':runtypeflag,
         'address':addressflag, 'CPU':CPUflag, 'load':loadflag}

#initialize labels
memLabels = buildMemLabels(baseflag, addressflag)
CPULabels = CPULabels(CPUflag)

#initialize locations
memoryLocation = (size[X] * scale[X]/100 * memoryBaseLocation[X]/100, 
                size[Y] * scale[Y]/100 * memoryBaseLocation[Y]/100)
                
CPULocation = (size[X] * scale[X]/100 * CPUBaseLocation[X]/100, 
                size[Y] * scale[Y]/100 * CPUBaseLocation[Y]/100) 
                
screenLocation = (size[X] * scale[X]/100 * screenBaseLocation[X]/100, 
                size[Y] * scale[Y]/100 * screenBaseLocation[Y]/100)
                
runLocation = (size[X] * scale[X]/100 * runBaseLocation[X]/100, 
                size[Y] * scale[Y]/100 * runBaseLocation[Y]/100)
                
baseLocation = (size[X] * scale[X]/100 * baseBaseLocation[X]/100, 
                size[Y] * scale[Y]/100 * baseBaseLocation[Y]/100)

#Test data arrays
ML = []
for i in range(32):
    ML.append(i*12)
    
CPU = []
for i in range(6):
    CPU.append(444*i)
    
Lines = []
for i in range(1,6,1):
    Lines.append(str(i * 2345))

while True:
    screen.fill(white)
      
    drawMemory(ML, memoryLocation)    
    drawCPU(CPU, CPULocation)                    
    drawScreen(Lines, screenLocation)
    
    runrect = drawRun(runtypeflag, runLocation)
    
    baserect = drawBase(baseflag, baseLocation)
    
    #Draw Buttons
    drawRun(runtypeflag, runLocation)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if runrect.collidepoint(x, y):
                    if runtypeflag == 'Step':
                        runtypeflag = 'Free'
                    elif runtypeflag == 'Free':
                        runtypeflag = 'Step'
                if baserect.collidepoint(x, y):
                    if baseflag == 'Hex':
                        baseflag = 'Dec'
                    elif baseflag == 'Dec':
                        baseflag = 'Hex'
                    memLabels = buildMemLabels(baseflag, addressflag)
            
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE and runflag == False:
                pygame.event.post(pygame.event.Event(QUIT))
            if event.key == pygame.K_ESCAPE and runflag == True:
                    running = False
            if event.key == pygame.K_SPACE and runflag == True:
                    step = True
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                    Lines[0] = Lines[0][:-2] + "?"
            elif event.key == pygame.K_RETURN:
                if loadflag == False and inputflag == False:
                    if Lines[0] != "?":
                        Lines[0] = Lines[0][:-1]
                    Lines.insert(0, "?")
                    Lines = Lines[:5]
                if loadflag:
                    if Lines[0][-4:-1] == "END":
                        loadflag = False
                        Lines[0] = Lines[0][:-1]
                        Lines.insert(0, "?")
                        Lines = Lines[:5]
                    else:
                        mem[memloc] = Lines[0][3:-1]
                        Lines[0] = Lines[0][:-1]
                        memloc += 1
                        Lines.insert(0, mystr(memloc) + "=?")
                        Lines = Lines[:5]
                if inputflag:
                    Lines[0] =  Lines[0][:-1] + '?'#(chr(event.key)).upper() + "?"
                    cpu['ACC'] = Lines[0][:-1]
                    inputflag = False
                    runflag = True
                    trigger = False
            elif runflag == False and event.key != pygame.K_ESCAPE:
                Lines[0] =  Lines[0][:-1] + (chr(event.key)).upper() + "?"
            
                
    pygame.display.update()
    fpsClock.tick(fps)