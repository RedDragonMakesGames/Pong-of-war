import pygame
from pygame.locals import *
import random
import math
import sys

#Defines
XSIZE = 700
YSIZE = 400
WALL_SIZE = 10
SPEED = 5
AI_SPEED = 3
PLAYER_SPEED = 3
CENTER_SPEED = 3

#Helper functions for tuples
def tupAdd(A, B):
    return (A[0] + B[0], A[1] + B[1])

def tupSub(A, B):
    return (A[0] - B[0], A[1] - B[1])

def tupDivInt(A, factor):
    return (math.floor(A[0]/factor), math.floor(A[1]/factor))

def CheckTounching(pos1, pos2, size):
    if ((pos1[0] >= pos2[0] and pos1[0] <= pos2[0] + size[0]) and (pos1[1] >= pos2[1] and pos1[1] <= pos2[1] + size[1])):
        return True
    else:
        return False

class BreakIn:
    def __init__(self):
        #Set up here
        pygame.init()
        self.screen = pygame.display.set_mode((XSIZE, YSIZE))
        pygame.display.set_caption("Pong of war")

        self.clock = pygame.time.Clock()

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((200,200,200))

        self.topLeft = (WALL_SIZE, WALL_SIZE)
        self.topRight = (XSIZE - WALL_SIZE, WALL_SIZE)
        self.bottomLeft = (WALL_SIZE, YSIZE - WALL_SIZE)
        self.bottomRight = (XSIZE - WALL_SIZE, YSIZE - WALL_SIZE)

        #Load assets
        self.ball = pygame.image.load('Assets/ball.png')
        self.paddle = pygame.image.load('Assets/paddle.png')
        if pygame.font:
            self.font = pygame.font.Font(None, 40)

        self.SpawnBall()

        self.playerScore = 0
        self.AIScore = 0

        self.paddlePos = (XSIZE - WALL_SIZE*2, YSIZE/2)
        self.AIpaddlePos = (WALL_SIZE*2, YSIZE/2)
        self.centerPaddlePos = (XSIZE/2, YSIZE/2)
        self.playerDirection = 0
        self.AIDirection = 0

        #Flag for ending, True is player wins, False is player loses
        self.ended = None

        #Start the main gameplay loop
        self.Run()

    def Run(self):
        self.finished = False

        while not self.finished:
            #Handle input
            if self.ended == None:
                self.HandleInput()

            #Control AI
            if self.ended == None:
                self.HandleAI()

            #Draw screen
            self.Draw()

            self.clock.tick(60)

    def HandleInput(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()

        #Movement for paddles
        moving = True
        if pygame.key.get_pressed()[K_UP]:
            if self.paddlePos[1] > WALL_SIZE:
                self.paddlePos = (self.paddlePos[0], self.paddlePos[1] - PLAYER_SPEED)
                self.playerDirection = -1
        elif pygame.key.get_pressed()[K_DOWN]:
            if self.paddlePos[1] < YSIZE - WALL_SIZE - self.paddle.get_size()[1]:
                self.paddlePos = (self.paddlePos[0], self.paddlePos[1] + PLAYER_SPEED)
                self.playerDirection = 1
        else:
            self.playerDirection = 0

#Moves the paddle in the x direction of the ball
    def HandleAI(self):
        if self.ballPos[1] > self.AIpaddlePos[1] + (self.paddle.get_size()[1] / 2):
            if self.AIpaddlePos[1] < YSIZE - WALL_SIZE - self.paddle.get_size()[1]:
                self.AIpaddlePos = (self.AIpaddlePos[0], self.AIpaddlePos[1] + AI_SPEED)
                self.AIDirection = 1
        else:
            if self.AIpaddlePos[1] > WALL_SIZE:
                self.AIpaddlePos = (self.AIpaddlePos[0], self.AIpaddlePos[1] - AI_SPEED)
                self.AIDirection = -1

    def Draw(self):
        #clear screen
        self.screen.blit(self.background, (0,0))

        #Draw walls
        pygame.draw.line(self.screen, (10,10,10), self.topLeft, self.topRight)
        pygame.draw.line(self.screen, (255,10,10), self.topLeft, self.bottomLeft)
        pygame.draw.line(self.screen, (255,10,10), self.topRight, self.bottomRight)
        pygame.draw.line(self.screen, (10,10,10), self.bottomLeft, self.bottomRight)

        #Perform ball movement
        if self.ended == None:
            self.ballPos = tupAdd(self.ballPos, self.ballSpeed)
            self.CheckAndCalculateCollision()
        
        #perform center paddle movement
        self.centerPaddlePos = (self.centerPaddlePos[0], self.centerPaddlePos[1] + CENTER_SPEED *(self.AIDirection + self.playerDirection))
        if self.centerPaddlePos[1] > YSIZE - WALL_SIZE - self.paddle.get_size()[1]:
            self.centerPaddlePos = (self.centerPaddlePos[0], YSIZE - WALL_SIZE - self.paddle.get_size()[1])
        elif self.centerPaddlePos[1] < WALL_SIZE:
            self.centerPaddlePos = (self.centerPaddlePos[0], WALL_SIZE)

        #Draw ball
        #Adjust by size of ball/2 to draw so the middle of the ball is ballPos
        self.screen.blit(self.ball, tupSub(self.ballPos, tupDivInt(self.ball.get_size(), 2)))

        #Draw paddles
        self.screen.blit(self.paddle, self.paddlePos)
        self.screen.blit(self.paddle, self.AIpaddlePos)
        self.screen.blit(self.paddle, self.centerPaddlePos)

        #Draw score
        scoreTxt = self.font.render("Score: " + str(self.AIScore) + " / " + str(self.playerScore), True, (10,10,10))
        self.screen.blit (scoreTxt, (XSIZE - 220, WALL_SIZE * 2))

        #Draw end message
        if self.ended == True:
            endString = "You Win!"
        elif self.ended == False:
            endString = "You lose..."
        if self.ended != None:
            endTxt = self.font.render(endString, True, (10,10,10))
            self.screen.blit (endTxt, (WALL_SIZE * 5, WALL_SIZE * 5))

        #Refresh the screen
        pygame.display.flip()

    #Sub functions below
    def SpawnBall(self):
        #Calculate a random direction for the ball to move in, so that it will be moving with SPEED in that direction
        xSpeed = random.random() * SPEED
        #Make sure the ball still has a decent amount of horizontal speed
        if xSpeed < 1:
            xSpeed = 1
        ySpeed = math.sqrt(float(SPEED) ** 2 - xSpeed ** 2)
        if random.randint(0,1) == 1:
            xSpeed = -xSpeed
        self.ballSpeed = (xSpeed, -ySpeed)
        self.ballPos = (XSIZE/2, WALL_SIZE)

    def CheckAndCalculateCollision(self):
        #Check for left wall
        if self.ballPos[0] < WALL_SIZE:
            self.playerScore += 1
            self.SpawnBall()
        #Check for right wall
        if self.ballPos[0] > XSIZE - WALL_SIZE:
            self.AIScore += 1
            self.SpawnBall()
        #Check for top wall
        if self.ballPos[1] <  WALL_SIZE:
            #Reverse Y velocity
            self.ballSpeed = (self.ballSpeed[0], - self.ballSpeed[1])
        #Check for bottom wall
        if self.ballPos[1] >  YSIZE - WALL_SIZE:
            #Reverse Y velocity
            self.ballSpeed = (self.ballSpeed[0], - self.ballSpeed[1])

        #Check for center paddle (just flip x direction)
        if CheckTounching(self.ballPos, self.centerPaddlePos, self.paddle.get_size()):
            #Reverse X velocity
            self.ballSpeed = (- self.ballSpeed[0], self.ballSpeed[1])            

        #Check for right paddle
        if CheckTounching(self.ballPos, self.paddlePos, self.paddle.get_size()):
            #Re-aim the ball, based on the point at which it hit the paddle
            self.ballSpeed = (- self.ballSpeed[0], self.ballSpeed[1])
            directX = -1           
            contactPos = self.ballPos[1] - self.paddlePos[1]
            contactRatio = contactPos / self.paddle.get_size()[1]
            adjContactRatio = contactRatio * 2 - 1
            ySpeed = adjContactRatio * SPEED
            xSpeed = math.sqrt(float(SPEED) ** 2 - ySpeed ** 2)
            self.ballSpeed = (xSpeed * directX, ySpeed)
        
        #Check for left paddle
        if CheckTounching(self.ballPos, self.AIpaddlePos, self.paddle.get_size()):
            #Re-aim the ball, based on the point at which it hit the paddle
            directX = 1
            contactPos = self.ballPos[1] - self.AIpaddlePos[1]
            contactRatio = contactPos / self.paddle.get_size()[1]
            adjContactRatio = contactRatio * 2 - 1
            ySpeed = adjContactRatio * SPEED
            xSpeed = math.sqrt(float(SPEED) ** 2 - ySpeed ** 2)
            self.ballSpeed = (xSpeed * directX, ySpeed)
        

#Run the game
game = BreakIn()
