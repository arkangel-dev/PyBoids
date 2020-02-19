import random
import time
import pygame
import threading
import weakref
import gc
import math
from pygame.locals import *

class Bird:
    pos_x = 0
    pos_y = 0
    speed_x = 0
    speed_y = 0
    rotation = 0
    enhance_factor = 2
    sprite = pygame.image.load("bird.png")
    sprite = pygame.transform.scale(sprite, (10, 13))
    observing = False
    terminate = False
    neighbours = []

    def __init__(self, observing = False):
        self.pos_x = random.randint(0, 700)
        self.pos_y = random.randint(0, 700)
        self.speed_x = self.InitVelocity()
        self.speed_y = self.InitVelocity()  

    def Refresh(self):
        if (self.observing):
            self.sprite = pygame.image.load("bird_o.png")
            self.sprite = pygame.transform.scale(self.sprite, (10, 13))

    def InitVelocity(self):
        x = 0
        while (True):
            x = random.uniform(-1, 1)
            if ((x > 0.5) or (x < -0.5)):
                break
        return x

    # def getAngle(self, a, b, c):
    #     ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    #     return ang + 360 if ang < 0 else ang

    def UpdateHeading(self):
        newx = self.pos_x + self.speed_x
        newy = (self.pos_y + self.speed_y) * -1
        angle = (180 / math.pi) * math.atan2(self.speed_x, self.speed_y)
        self.rotation = angle + 180
        # print(angle)
        # self.rotation = 45 + 180

    def Update(self):
        if (self.observing):
            telemetry_thread = threading.Thread(target=self.StartTelemetry)
            telemetry_thread.start()

        while True:
            self.pos_x += self.speed_x * self.enhance_factor
            self.pos_y += self.speed_y * self.enhance_factor

            if (self.pos_x > 700):
                self.pos_x = 0
            elif (self.pos_x < 0):
                self.pos_x = 700
            if (self.pos_y > 700):
                self.pos_y = 0
            elif (self.pos_y < 0):
                self.pos_y = 700

            self.UpdateHeading()
            # print(str(len(self.neighbours)))

            if (self.terminate):
                break

            time.sleep(0.01)

    def Terminate(self):
        #print("Killing self (" + str(id(self)) + ")")
        self.terminate = True

    def StartTelemetry(self):
        print("") 
        print("[+] Telemetry for observing bird: ")
        while True:     
            if (self.terminate):
                break
            print(
                "\t Neighbour Count : " + str(len(self.neighbours)) + " X : " + str(self.pos_x) + " Y : " + str(self.pos_y), end='\r')
            time.sleep(0.25)

    # def AvoidCollision(self): 
        



class Environment:
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((700, 700))
    # birdList = []
    # birdArray = weakref.WeakValueDictionary()
    birdArray = []
    clock = pygame.time.Clock()
    boid_mem = pygame.image.load("bird.png")
    boid_mem = pygame.transform.scale(boid_mem, (10, 13))
    threadList = []
    done = False
    Running = False
    ObserverAdded = False

    def AddBoidArray(self, count):
        print("Creating " + str(count) + " bird threads...")
        if not self.Running:
            for x in range(0, count):
                bird = Bird()
                oid = id(bird)
                # self.Remember(bird)
                # self.birdList.append(bird)
                self.birdArray.append(bird)
                updateThread = threading.Thread(target=bird.Update)

                # print("New Bird : " + str(oid))
                # print("     x : " + str(bird.pos_x) + " y : " + str(bird.pos_y))
                # print("     vx : " + str(bird.speed_x) + " vy : " + str(bird.speed_y))
                # print("")

                updateThread.start()
        else:
            print("Cannot add members while simulation is running...")

    def AddObservingMember(self):
        if not self.Running:
            if not (self.ObserverAdded):
                bird = Bird()
                bird.observing = True
                bird.Refresh()
                oid = id(bird)
                self.birdArray.append(bird)
                updateThread = threading.Thread(target=bird.Update)
                self.threadList.append(updateThread)
                
                print("New Observing Bird : " + str(oid))
                # print("     x : " + str(bird.pos_x) + " y : " + str(bird.pos_y))
                # print("     vx : " + str(bird.speed_x) + " vy : " + str(bird.speed_y))
                # print("")

                updateThread.start()
                self.ObserverAdded = True
            else:
                print("Observing bird already added...")
        else:
            print("Cannot add members while simulation is running...")


    def Start(self):
            self.Running = True
            while not self.done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.done = True
                        self.Running = False
                        print("")
                        print("Killing " + str(len(self.birdArray)) + " bird threads...")
                        for thread in self.birdArray:
                            thread.Terminate()

                self.screen.fill((0, 0, 0))

                for bird_c in self.birdArray:
                    # bird_c = self.Recall(birdId)
                    surf = pygame.transform.rotate(bird_c.sprite, bird_c.rotation)
                    self.screen.blit(surf, (int(bird_c.pos_x), int(bird_c.pos_y)))

                    neighbours = []
                    for bird_n in self.birdArray:
                        if (bird_n != bird_c):
                            if (self.CalculateDistance((bird_c.pos_x, bird_c.pos_y), (bird_n.pos_x, bird_n.pos_y)) < 50):
                                neighbours.append(bird_n)
                    bird_c.neighbours = neighbours
                
                pygame.display.flip()
                self.clock.tick(30)

    def CalculateDistance(self, tuplea, tupleb):
        xdiff = tuplea[0] - tupleb[0]
        ydiff = tuplea[1] - tupleb[1]
        xdiff = xdiff * xdiff
        ydiff = ydiff * ydiff
        diff = xdiff + ydiff
        result = math.sqrt(diff)
        return result

    def Remember(self, obj):
        # oid = id(obj)
        # self.birdArray[oid] = obj
        # return oid
        self.birdArray.append(obj)

    # def Recall(self, oid):
    #     for obj in gc.get_objects():
    #         if id(obj) == oid:
    #             return obj

