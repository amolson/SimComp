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
        
command = ['RUN', 'RNS', 'NEW', 'RST', 'LOD', 'LOA', 'END']

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
    if '=' == larray[0][2]:
        larray[0] = larray[0][3:]
    elif '=' == larray[0][1]:
        larray[0] = larray[0][2:]
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
            print 'checking for number only'
            print larray[0][:-1], 'larray[0]'
            try:
                number = int(larray[0][:-1])
                numflag = True
                print '', number
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
    ML.append(i*12)
    
CPU = []
for i in range(6):
    CPU.append(444*i)
    
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
        elif 0 < nbr < 30:
            runtypeflag = 'Free'
            fps = nbr
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
        
#Mnemonic handling

if cmd == 'LDA' and evalm:
    CPU[1] = ML[nbr]
    evalm = False
    
if cinst == "ADD" and evalm: #Op Code 3
    cpu[1] = ML[nbr] + int(cpu[1])
    evalm = False
    
#Run handling
        if runflag:
#            bc += 1        
#            if bc >= 30 and run == "free":
#                counter += 1
#                if counter == 1:
#                    cpu['PC'] = 0
#                    cpu['FETCH'] = 0
#                    cpu['EXEC'] = ''
#                    step = False
#                if counter == 2:
#                    cpu['FETCH'] = cpu['PC']
#                    cpu['IR'] = mem[cpu['FETCH']]
#                    cpu['INC'] = 'PC'
#                    step = False
#                if counter == 3:
#                    cpu['EXEC'] = cpu['IR'][:3]
#                    if cpu['INC'] == 'PC':
#                        cpu['PC'] += 1
#                        cpu['INC'] = ''
#                    trigger = True
#                    step = False
#                    counter = 1
#                bc = 0
            if step == True and runtypeflag == "Step":
                counter += 1
                if counter == 1:
                    cpu['PC'] = 0
                    cpu['FETCH'] = 0
                    cpu['EXEC'] = ''
                    step = False
                if counter == 2:
                    cpu['FETCH'] = cpu['PC']
                    cpu['IR'] = mem[cpu['FETCH']]
                    cpu['INC'] = 'PC'
                    step = False
                if counter == 3:
                    cpu['EXEC'] = cpu['IR'][:3]
                    if cpu['INC'] == 'PC':
                        cpu['PC'] += 1
                        cpu['INC'] = ''
                    evalm = True
                    step = False
                    counter = 1
            cmem = cpu['IR']
            cinst = cmem[:3]
            cnum = cmem[3:]

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
                    runflag = False
                else:
                    Lines[0] =  Lines[0][:-1] + (chr(event.key)).upper() + "?"
            if event.key == pygame.K_SPACE and runflag == True:
                    step = True
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                print 'check backspace'
                Lines[0] = Lines[0][:-2] + "?"
            elif event.key == pygame.K_RETURN:
                cmd, nbr = checkLoad(Lines)
                print cmd, nbr
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
                            Lines[0] = str(memloc) + cmd
                        else:
                            ML[memloc] = cmd + str(nbr)
                            Lines[0] = str(memloc) + '=' + cmd + str(nbr)
                        memloc += 1
                        Lines.insert(0, str(memloc) + '=?')
                        Lines = Lines[:5]
                if inputflag:
                    CPU[1] = nbr
                    inputflag = False
            elif runflag == False and event.key != pygame.K_ESCAPE:
                try:
                    Lines[0] =  Lines[0][:-1] + (chr(event.key)).upper() + "?"
                except ValueError:
                    Lines[0]
                           
    pygame.display.update()
    fpsClock.tick(fps)