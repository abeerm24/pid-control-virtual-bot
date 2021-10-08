import pygame
import math
import os

pygame.init()

white = (255, 255, 255)
black = (0, 0, 0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
pi = math.pi

screen = pygame.display.set_mode((800, 600))

pygame.display.set_caption("Line Follower")
icon = pygame.image.load(os.path.join('imgs', 'icon.png'))
pygame.display.set_icon(icon)

backgroundImg = pygame.image.load(os.path.join('imgs', 'track.png'))

# bot
botImg = pygame.image.load(os.path.join('imgs', 'bot.jpg'))
# current position of bot should be chosen in the way that it should spawn correctly on the screen
botSize = 60  # diameter of bot
running = True
centreX = 400     #Original: 146
centreY = 500     #Original: 320
botCurrent_y = centreY
botx = centreX-botSize/2
boty = centreY - botSize/2


#Coordinates for sensor 1 of the bot
pos1 = [-9,-40]                       # Position vector of sensor wrt centre of botImg
x1 = centreX + pos1[0]
y1 = centreY + pos1[1]
    
#Coordinates for sensor 2 of the bot
pos2 = [9,-40]
x2 = centreX + pos2[0]
y2 = centreY + pos2[1]

#Coordinates for middle sensor of the bot
posm = [0,-40]
xm = centreX + posm[0]
ym = centreY + posm[1]

rad = 3 #Sensor radius

#Define the direction vector for motion of the bot
dx = 0
dy = -1
dvec = [dx,dy]

def translate(x,y,vec):
    '''
    This function returns the coordinates of a point after shifting by vec.
    '''
    x+= vec[0]
    y+= vec[1]
    return x,y

def rotateVec(vec, theta):
    '''
    This function rotates the given vector by theta (in radians). 
    '''
    X = vec[0]*math.cos(theta) - vec[1]*math.sin(theta)
    Y = vec[0]*math.sin(theta) + vec[1]*math.cos(theta)
    return [X,Y]

def colorSensor(x,y):
    '''
    This function returns whether the color at (x,y) is black or not.
    '''
    colorRGBA = tuple(screen.get_at((int(x),int(y))))
    colorRGB = colorRGBA[:3]
    if colorRGB==black:
        return True
    else:
        return False

def inScreen(x):
    if x<750 and x>50:
        return True
    else:
        return False

def errorCalculator():
    '''
    This function returns the error as:-
    i) 1 : if Sensor1 detects white
    ii) 0 : if none of the sensors detects white
    iii)-1: if Sensor2 detects white 
    '''
    if not colorSensor(x1,y1) and (colorSensor(x2,y2) or colorSensor(xm,ym)):
        error = 0.1
    elif not colorSensor(x2,y2) and (colorSensor(x1,y1) or colorSensor(xm,ym)):
        error = -0.1
    elif colorSensor(x1,y1) and colorSensor(x2,y2) and colorSensor(xm,ym):
        error = 0
    #elif colorSensor(x1,y1) and colorSensor(xm,ym) and colorSensor(xm,ym): 
    else:
        if inScreen(xm):
            if inScreen(ym):
                error = 0
            else:
                error = 10
        else:
            error = 10

    return error

def PIDControl(lasterr,interr,vec):
    '''
    This function implements PID control over our bot.
    :param lasterr: Stores the error recorded last time.
    '''
    #Define error variable 'e' i.e. the proportional part
    e = errorCalculator()
    if e==10:
        theta = 3*pi/4
    else:
        #Define another variable 'inte' to store accumulated error over time i.e. the integral part
       interr += e
       #Define another variable 'dere' to store the change in error over one loop i.e. the derivative part
       dere = e-lasterr

       #Define the pid constants
       kp=0.1
       kd=0.1
       ki=0.1
    
       #Theta will be a relation between the P,I,D and then dvec is rotated
       theta = kp*e + ki*interr + kd*dere
    vec = rotateVec(vec,theta)

    return lasterr, interr, vec, theta

count = 0 #This variable will act as the equivalent of time while the game loop runs

#Initialize lasterr and interr as zero
lasterr = 0
interr = 0

while running:
    screen.fill(black)
    screen.blit(backgroundImg, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    lasterr,interr,dvec,theta = PIDControl(lasterr,interr,dvec)
    #botImg = pygame.transform.rotate(botImg,theta*180/pi)
    botx,boty = translate(botx,boty,dvec)
    centreX,centreY = translate(centreX,centreY,dvec)
    screen.blit(botImg, (int(botx), int(boty)))
    #Update sensor1 position
    pos1 = rotateVec(pos1,theta)
    x1,y1 = translate(centreX,centreY,pos1)
    pygame.draw.circle(screen,red,(int(x1),int(y1)),rad,1)       #Thickness of circle is 1
    #Update sensor2 position
    pos2 = rotateVec(pos2,theta)
    x2,y2 = translate(centreX,centreY,pos2)
    pygame.draw.circle(screen,green,(int(x2),int(y2)),rad,1)
    #Update middle sensor position
    posm = rotateVec(posm,theta)
    xm,ym = translate(centreX,centreY,posm)
    pygame.draw.circle(screen,blue,(int(xm),int(ym)),rad,1)
    pygame.display.update()
