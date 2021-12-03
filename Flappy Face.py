import pygame
import random
from pygame.locals import *
import cv2

noseCoords = [0,0,0,0]

def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    features = classifier.detectMultiScale(gray_img, scaleFactor, minNeighbors)
    coords = []
    for(x,y,w,h) in features:
        cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
        cv2.putText(img, text, (x,y-4), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)
        coords = [x, y, w, h]
    return coords

    
def detect(img, faceCascade, eyesCascade, mouthCascade):
    global noseCoords
    
    color = {"blue":(255,0,0), "red":(0,0,255),"green":(0,255,0),"white":(255,255,255)}
    coords = draw_boundary(img, faceCascade, 1.1, 14, color['blue'], "Face")
    if not coords:
        coords = [0,0]
    noseCoords = coords
    if len(coords)==4:
        roi_img = img[coords[1]:coords[1]+coords[3], coords[0]:coords[0]+coords[2]]
        coords = draw_boundary(roi_img, eyesCascade, 1.1, 15, color['red'], "Eyes")
        coords = draw_boundary(roi_img, mouthCascade, 1.1, 70, color['white'], "Smile")
        
    return img

def getFaceCoords():
    global noseCoords
    return (noseCoords[0], noseCoords[1])

faceCascade = cv2.CascadeClassifier("/cascades/haarcascade_frontalface_default.xml")
eyesCascade = cv2.CascadeClassifier("/cascades/haarcascade_eye.xml")
mouthCascade = cv2.CascadeClassifier("/cascades/haarcascade_smile.xml")

video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)



#define display surface
W, H = 420, 420
HW, HH = W / 2, H / 2
AREA = W * H

#initialize display
pygame.init()
win = pygame.display.set_mode((W, H))
pygame.display.set_caption("flappy face")
clock = pygame.time.Clock()


# define some colors
BLACK = (0,0,0, 255)
WHITE = (255,255,255,255)
BLUE = (0,181,204,1)

#define sprites
bird = pygame.Surface((32,32))
bg = pygame.image.load("/sprites/bg.png").convert()
pipe = pygame.Surface((50,500))

#set up sprites
bgX = 0
bgX2 = bg.get_width()

class playerClass(object):

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width 
        self.height = height 
        self.hitbox = (self.x + 20, self.y+10, 23, 23)
    
    def set_position (self, x, y):
        self.x = x-30 
        self.y = y-30

    def draw(self, win):
        win.blit(bird, (self.x, self.y))
        self.hitbox = (self.x, self.y, 32, 32)
        pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        
class pipesClass (object):

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width 
        self.height = height 
        self.vel = 10
        self.hitboxTop = (self.x, self.y, 50, 500)
        self.hitboxBot = (self.x, self.y + 575, 50, 500)

    def draw (self,win):
        self.move()
        win.blit(pipe, (self.x, self.y))
        win.blit(pipe, (self.x, self.y + 575))
        self.hitboxTop = (self.x, self.y, 50, 500)
        self.hitboxBot = (self.x, self.y + 575, 50, 500)
        pygame.draw.rect(win, (255,0,0), self.hitboxTop, 2)
        pygame.draw.rect(win, (255,0,0), self.hitboxBot, 2)
    
    def move(self):
        self.x -= self.vel
        if self.x <= 0:
            self.x = 420
            self.y = random.randint(-450,-210) #change here for random y
 
    def update_vel(self, vel):
        self.vel = vel

    def hit(self):
        print('hit')
       

#####    Main Game Loop   #####

# Initialize score counter, font, and score XY positions
score = 0
font = pygame.font.Font('freesansbold.ttf', 24)
textX, textY = 1


# Update the game screen
def redrawWindow():
    # Draw shown bg and bg on queue for scrolling
    win.blit(bg, (bgX,0))
    win.blit(bg, (bgX2, 0))

    # Draw the bird and pipes
    flyer.draw(win)
    pipes.draw(win)
    
    # Update the score
    show_score(textX, textY)
    pygame.display.update()

# Initialize pipes and player character, set the timer, initialize speed to 60 and run to True
pipes = pipesClass(420,-300,50, 500)
flyer = playerClass(75,100,32,32)
pygame.time.set_timer(USEREVENT+1, 500)
speed = 60
run = True

# Display game over screen
def showGameOver():
    go_render = font.render("GAME OVER!", True, (255,165,0))
    win.blit(go_render, (210,210))
    pygame.display.update()

# 
def show_score(x,y):
    score_render = font.render("Score: " + str(score), True, (255,165,0))
    win.blit(score_render, (x,y))
    
isGameOver = False
while run:

    if (isGameOver == False):
        _, img = video_capture.read()
        img = cv2.flip(img, 1)
        img = detect(img, faceCascade, eyesCascade, mouthCascade)
        cv2.imshow("Video", img)
        if(cv2.waitKey(1) & 0xFF == ord("q")):
           break

        redrawWindow()
        bgX -= 1.4
        bgX2 -= 1.4
        if bgX < bg.get_width() * -1:  #showing background movement to the left
            bgX = bg.get_width()
        if bgX2 < bg.get_width() * -1:
            bgX2 = bg.get_width()
        birdx, birdy = getFaceCoords()
        flyer.set_position(birdx, birdy)
        for event in pygame.event.get(): #quit event
            if event.type == USEREVENT+1:
                speed += 0.5
  
            elif event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()            
            
            if flyer.y < pipes.hitboxTop[1] + pipes.hitboxTop[3] and flyer.y > pipes.hitboxTop[1]:
                if flyer.x + 32 > pipes.hitboxTop[0] and flyer.x + 32 < pipes.hitboxTop[0] + pipes.hitboxTop[2]:
                    pipes.hit()
                    isGameOver = True

            if flyer.y + 32 < pipes.hitboxBot[1] + pipes.hitboxBot[3] and flyer.y + 32 > pipes.hitboxBot[1]:
                if flyer.x + 32 > pipes.hitboxBot[0] and flyer.x + 32 < pipes.hitboxBot[0] + pipes.hitboxBot[2]:
                    pipes.hit()
                    isGameOver = True

        score+=1
        
    else:
        showGameOver()
        video_capture.release()
        cv2.destroyAllWindows()
        for event in pygame.event.get(): #quit event
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
   
    clock.tick(speed)
