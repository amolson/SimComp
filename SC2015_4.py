# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 08:34:05 2015

@author: amolson
"""

import pygame, sys
from pygame.locals import *
import random

#Initialize code
pygame.init()
fpsClock = pygame.time.Clock()
pygame.key.set_mods(KMOD_CAPS)

size = (1200, 480)

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
speed = 30

cmd = ''
nbr = ''

mnem = [['STP', 'LDA', 'STA', 'ADD', 'SUB', 'MUL', 'DIV', 'INP', 'OUT',
        'JMP', 'MOD', 'NEG', 'RND'], 
        ['SKZ', 'SNZ', 'SLZ', 'SGZ', 'SPS', 'SNG'],
        ['JPZ', 'JNZ', 'JLZ', 'JGZ', 'JPS', 'JNG'],
        ['AND', 'NOR', 'ORL', 'XOR', 'INV', 'SHL'
        'SHR', 'ROL', 'ROR']]
        
mnemflat = []
for i in mnem:
    for j in i:
        mnemflat.append(j)
        
command = ['RUN', 'RNS', 'NEW', 'RST', 'LOD', 'LOA', 'END', 'CPR']

#pull from tuple
X = 0
Y = 1
width = 2
height = 3

scale = (100, 100)

#flags

runflag = False #False, paused: True, running
baseflag = 'Dec' #Hex or Dec
runtypeflag = 'Step' #Step or Free
addressflag = 'Direct' #Direct addressing or xy, bank/location addressing
CPUflag = 'Normal' #Place holder for possible future variations
loadflag = False #False, not loading: True, loading
inputflag = False #False, not taking in put: True, taking input
opflag = 'Mnem' #Mnemonic, Mnem: or Opcode, Opco
flags = {'run':runflag, 'base':baseflag, 'runtype':runtypeflag,
         'address':addressflag, 'CPU':CPUflag, 'load':loadflag}
         
#activity flags

evalm = False

#Base locations for modules, out of 100
memoryBaseLocation = (50, 15)
CPUBaseLocation = (2, 76)
screenBaseLocation = (2, 2)
runBaseLocation = (80, 5)
opBaseLocation = (65, 5)
baseBaseLocation = (54, 5)

memloc = 0

counter = 0

bc = 0

step = False

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
        memLocation = (location[X] + ((i/8) * 150*scale[X]/100),
                       location[Y] + ((i % 8) * 50*scale[Y]/100), 
                        140*scale[X]/100, 45*scale[Y]/100)
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
    
def drawButton(string, location):
    output = controlFont.render(string, 1, white, black)
    runr = pygame.Rect(output.get_rect())
    runrect = runr.move(location)
    screen.blit(output, location)
    
    return runrect
    
def checkLoad(larray):
    """Verifies user input and standardizes format into 3 and Number, 
    if any. Input is the line array."""
    try:
        if '=' == larray[0][2]:
            larray[0] = larray[0][3:]
        elif '=' == larray[0][1]:
            larray[0] = larray[0][2:]
    except IndexError:
        return 'UDF', 'NAN'
    iscmd = larray[0][:3]
    numflag = True
    number = 0
    if iscmd in command:
        if iscmd == 'LOA':
            try:
                larray[0] = larray[0][:3] + larray[0][4:]
            except UnboundLocalError:
                iscmd = 'NVC'
    elif iscmd not in mnemflat:
        if baseflag == 'Dec':
            try:
                number = int(larray[0][:-1])
                numflag = True
                return '', number
            except ValueError:
                iscmd = 'NVC'
                isnum = ''
                number = 'NAN'
                numflag = False
        elif baseflag == 'Hex':
            print 'checking for hex'
            try:
                number = int(larray[0][:-1], 16)
                numflag = True
                return '', number
            except ValueError:
                iscmd = 'NVC'
                isnum = ''
                number = 'NAN'
                numflag = False
    if numflag:
        isnum = larray[0][3:-1]
    if type(isnum) == str and numflag:
        if isnum != ' ':
            numflag = True
        else:
            numflag = False
    elif isnum == '':
        numflag = False
    if baseflag == "Dec" and numflag:
        try: 
            number = int(isnum)
            numflag = True
        except ValueError:
            number = 'NAN'
            numflag = False
    elif baseflag == 'Hex' and numflag:
        try: 
            number = int(isnum, 16)
            numflag = True
        except ValueError:
            number = 'NAN'
            numflag = False
    else:
        iscmd = 'NVC'
    return iscmd, number

#initialize labels
memLabels = buildMemLabels(baseflag, addressflag)
CPULabels = CPULabels(CPUflag)

#initialize locations
def scaleLocation(BL, scale, size):
    return (size[0] * scale[0]/100 * BL[0]/100, 
                size[1] * scale[1]/100 * BL[1]/100)

memoryLocation = scaleLocation(memoryBaseLocation, scale, size)
                
CPULocation = scaleLocation(CPUBaseLocation, scale, size) 
                
screenLocation = scaleLocation(screenBaseLocation, scale, size)
                
runLocation = scaleLocation(runBaseLocation, scale, size)
                
opLocation = scaleLocation(opBaseLocation, scale, size)
                
baseLocation = scaleLocation(baseBaseLocation, scale, size)

#Test data arrays
ML = []
for i in range(32):
    ML.append('')
    
CPU = []
for i in range(6):
    CPU.append('')
    
Lines = ['?', '', '', '', '', '']

while True:
    screen.fill(white)

#draw everything
    drawMemory(ML, memoryLocation)    
    drawCPU(CPU, CPULocation)                    
    drawScreen(Lines, screenLocation)
    
    runrect = drawButton(runtypeflag, runLocation)
    
    oprect = drawButton(opflag, opLocation)    
    
    baserect = drawButton(baseflag, baseLocation)

#Command handling
    if cmd == 'LOA' or cmd == 'LOD':
        loadflag = True
        if nbr == 'NAN':
            memloc = 0
        else:
            memloc = nbr
        cmd = ''
        Lines[0] = str(memloc) + '=?'
    
    if cmd == "RUN":
        runflag = True
        if nbr == 'NAN':
            memloc = 0
        else:
            memloc = nbr
        cmd = ''
        
    if cmd == 'RNS':
        runflag = True
        if nbr == 'NAN':
            runtypeflag = 'Step'
        elif 0 < nbr < 101:
            runtypeflag = 'Free'
            speed = nbr
        else:
            runtypeflag = 'Free'
        cmd = ''
        
    if cmd == 'NEW':
        ML = []
        for i in range(32):
            ML.append('')
        cmd = ''
            
    if cmd == 'RST':
        ML = []
        for i in range(32):
            ML.append('')
        CPU = [0, '', '', '', '', '']
        cmd = ''
        
    if cmd == 'CPR':
        CPU = [0, '', '', '', '', '']
        counter = 0
        cmd = ''
        
#Mnemonic handling

    if cmd == 'STP' and evalm:  #Op code 000, not in manual
        Lines.insert(0, "?")
        Lines = Lines[:5]
        runflag = False
        evalm = False

    if cmd == 'LDA' and evalm:   #Op code 001, load accumulator
        CPU[1] = ML[int(nbr)]
        evalm = False
        
    if cmd == 'STA' and evalm:   #Op code 002, store accumulator
        ML[int(nbr)] = CPU[1]
        evalm = False
            
    if cmd == "ADD" and evalm: #Op Code 003
        CPU[1] = int(CPU[1]) + int(ML[int(nbr)])
        evalm = False
        
    if cmd == "SUB" and evalm: #Op Code 004
        CPU[1] = int(CPU[1]) - int(ML[int(nbr)])
        evalm = False
        
    if cmd == "MUL" and evalm: #Op Code 005
        CPU[1] = int(CPU[1]) * int(ML[int(nbr)])
        evalm = False
    
    if cmd == "DIV" and evalm: #Op Code 006
        try:
            CPU[1] = int(CPU[1]) / int(ML[int(nbr)])
        except ZeroDivisionError:
            Lines.insert(0, 'DVZ!')
        evalm = False
        
    if cmd == "INP" and evalm: #Op Code 007, input to location
        inputflag = True
        runflag = False
        evalm = False
        lines.insert(0, "?")
        lines = lines[:5]
        
    if cmd == 'OUT' and evalm: #Op code 008, output from accumulator
        Lines.insert(0, CPU[1])
        Lines = Lines[:5]
        evalm = False
        
    if cmd == 'JMP' and evalm: #Op code 009, jump to location
        counter = 1
        CPU[3] = int(nbr)
        CPU[2] = ''            
        evalm = False
        
    if cmd == 'MOD' and evalm: #Op code 00a, modulo
        CPU[1] = int(CPU[1]) % int(ML[int(nbr)])
        evalm = False
        
    if cmd == 'NEG' and evalm: #Op code 00b, negates value in accumulator
        CPU[1] = 0 - int(CPU[1])
        evalm = False
        
    if cmd == 'TRP' and evalm: #Op code 00c, stop and output value in accumulator
        Lines.insert(0, str(CPU[1]))
        Lines = Lines[:5]
        runflag = False
        evalm = False
        
    if cmd == 'RND' and evalm: #Op code 00d, random number between 0 and 100
        CPU[1] = random.randrange(0, 100)
        evalm = False
        
    if cmd == 'SKZ' and evalm:
        counter = 1
        if int(cpu[1]) == 0:
            CPU[3] += 1
            CPU[2] = ''
        else:
            CPU[2] = ''
        evalm = False

    if cmd == 'SNZ' and evalm:
        counter = 1
        if int(cpu[1]) != 0:
            CPU[3] += 1
            CPU[2] = ''
        else:
            CPU[2] = ''
        evalm = False

    if cmd == 'SLZ' and evalm:
        counter = 1
        if int(cpu[1]) < 0:
            CPU[3] += 1
            CPU[2] = ''
        else:
            CPU[2] = ''
        evalm = False
        
    if cmd == 'SGZ' and evalm:
        counter = 1
        if int(cpu[1]) > 0:
            CPU[3] += 1
            CPU[2] = ''
        else:
            CPU[2] = ''
        evalm = False
        
    if cmd == 'SPS' and evalm:
        counter = 1
        if int(cpu[1]) >= 0:
            CPU[3] += 1
            CPU[2] = ''
        else:
            CPU[2] = ''
        evalm = False
        
    if cmd == 'SNG' and evalm:
        counter = 1
        if int(cpu[1]) <= 0:
            CPU[3] += 1
            CPU[2] = ''
        else:
            CPU[2] = ''
        evalm = False
        
    if cmd == 'JPZ' and evalm:
        counter = 1
        if int(cpu[1]) == 0:
            CPU[3] = int(nbr)
            CPU[2] = ''
        else:
            CPU[2] = ''
        evalm = False

    if cmd == 'JNZ' and evalm:
        counter = 1
        if int(cpu[1]) != 0:
            CPU[3] = int(nbr)
            CPU[2] = ''
        else:
            CPU[2] = ''
        evalm = False

    if cmd == 'JLZ' and evalm:
        counter = 1
        if int(cpu[1]) < 0:
            CPU[3] = int(nbr)
            CPU[2] = ''
        else:
            CPU[2] = ''
        evalm = False
        
    if cmd == 'JGZ' and evalm:
        counter = 1
        if int(cpu[1]) > 0:
            CPU[3] = int(nbr)
            CPU[2] = ''
        else:
            CPU[2] = ''
        evalm = False
        
    if cmd == 'JPS' and evalm:
        counter = 1
        if int(cpu[1]) >= 0:
            CPU[3] = int(nbr)
            CPU[2] = ''
        else:
            CPU[2] = ''
        evalm = False
        
    if cmd == 'JNG' and evalm:
        counter = 1
        if int(cpu[1]) <= 0:
            CPU[3] = int(nbr)
            CPU[2] = ''
        else:
            CPU[2] = ''
        evalm = False
    
#Run handling
    if runflag:
        if runtypeflag == "Free":
            bc += 1
            if bc >= speed:
                bc = 0
                step = True
        if step == True: # and runtypeflag == "Step":
            counter += 1
            if counter == 1:
                CPU[3] = 0
                CPU[4] = 0
                CPU[0] = ''
                step = False
            if counter == 2:
                CPU[4] = CPU[3]
                CPU[5] = ML[CPU[4]]
                CPU[2] = 'PC'
                step = False
            if counter == 3:
                CPU[0] = CPU[5][:3]
                if CPU[2] == 'PC':
                    CPU[3] += 1
                    CPU[2] = ''
                evalm = True
                step = False
                counter = 1
        cmem = CPU[5]
        try:
            cmd = cmem[:3]
            nbr = cmem[3:]
        except:
            cmd = 'UDF'
            nbr = ''

#User event handling        
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
                if oprect.collidepoint(x, y):
                    if opflag == 'Mnem':
                        opflag = 'Opco'
                    elif opflag == 'Opco':
                        opflag = 'Mnem'
                if baserect.collidepoint(x, y):
                    if baseflag == 'Hex':
                        baseflag = 'Dec'
                    elif baseflag == 'Dec':
                        baseflag = 'Hex'
                    memLabels = buildMemLabels(baseflag, addressflag)
            
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE and runflag == False:
                pygame.event.post(pygame.event.Event(QUIT))
            if event.key == pygame.K_ESCAPE:
                if runflag == True:
                    Lines[0] = 'STP'
                    Lines.insert(0, '?')
                    runflag = False
                else:
                    Lines[0] =  Lines[0][:-1] + (chr(event.key)).upper() + "?"
            if event.key == pygame.K_SPACE and runflag == True:
                    step = True
            if event.key == pygame.K_RIGHT and runtypeflag == "Free":
                speed += 1
                print speed
            if event.key == pygame.K_LEFT and runtypeflag == "Free":
                speed -= 1
                print speed
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                Lines[0] = Lines[0][:-2] + "?"
            elif event.key == pygame.K_RETURN:
                cmd, nbr = checkLoad(Lines)
                if loadflag == False and inputflag == False:
                    if cmd in command or cmd in mnemflat:
                        if nbr != 'NAN':
                            Lines[0] = cmd + str(nbr)
                        else:
                            Lines[0] = cmd
                    elif cmd == 'NVC':
                        Lines[0] = cmd
                    Lines.insert(0, '?')
                if loadflag:
                    if cmd == 'END':
                        loadflag = False
                        Lines[0] = cmd
                        Lines.insert(0, "?")
                        Lines = Lines[:5]
                    else:
                        if nbr == 'NAN':
                            ML[memloc] = cmd
                            Lines[0] = str(memloc) + '=' + cmd
                        else:
                            ML[memloc] = cmd + str(nbr)
                            Lines[0] = str(memloc) + '=' + cmd + str(nbr)
                        memloc += 1
                        Lines.insert(0, str(memloc) + '=?')
                        Lines = Lines[:5]
                if inputflag:
                    CPU[1] = nbr
                    inputflag = False
                    runflag = True
                    evalm = False
            elif runflag == False and event.key != pygame.K_ESCAPE:
                try:
                    Lines[0] =  Lines[0][:-1] + (chr(event.key)).upper() + "?"
                except ValueError:
                    Lines[0]
                           
    pygame.display.update()
    fpsClock.tick(fps)