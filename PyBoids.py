import random
import time
import pygame
import threading
import weakref
import gc
import math
from pygame.locals import *
import numpy as np
import vectormath as vm


class Bird:
    pos_x = 0
    pos_y = 0
    speed_x = 0
    speed_y = 0
    rotation = 0
    enhance_factor = 2
    sprite = pygame.image.load("bird.png")
    sprite = pygame.transform.scale(sprite, (10, 14))
    observing = False
    terminate = False
    visibility_range = 30
    neighbours = []

    resx = 0
    resy = 0

    def __init__(self, resolution, observing = False):
        self.pos_x = random.randint(0, resolution[0])
        self.pos_y = random.randint(0, resolution[1])
        self.resx = resolution[0]
        self.resy = resolution[1]
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

    def GetPosition(self):
        return (int(self.pos_x), int(self.pos_y))

    def GetVelocity(self):
        return (self.speed_x, self.speed_y)

    def UpdateHeading(self):
        newx = self.pos_x + self.speed_x
        newy = (self.pos_y + self.speed_y) * -1
        angle = (180 / math.pi) * math.atan2(self.speed_x, self.speed_y)
        self.rotation = angle + 180
        # print(angle)
        # self.rotation = 45 + 180

    def GetSpritePosition(self):
        return [int(self.pos_x) - 5, int(self.pos_y) - 7]

    def Update(self):
        if (self.observing):
            telemetry_thread = threading.Thread(target=self.StartTelemetry)
            telemetry_thread.start()

        while True:
            self.pos_x += self.speed_x * self.enhance_factor
            self.pos_y += self.speed_y * self.enhance_factor

            if (self.pos_x > self.resx):
                self.pos_x = 0
            elif (self.pos_x < 0):
                self.pos_x = self.resx
            if (self.pos_y > self.resy):
                self.pos_y = 0
            elif (self.pos_y < 0):
                self.pos_y = self.resy

            self.UpdateHeading()
            # print(str(len(self.neighbours)))

            if (self.terminate):
                break
            if (len(self.neighbours) != 0):
                # self.SteerTowards(self.GetFinalVel())
                self.SetVelocity(self.GetFinalVel())
            time.sleep(0.01)

    def SetVelocity(self, velocity):
        try:
            self.speed_x = velocity[0]
            self.speed_y = velocity[1]
        except:
            # print("Failed to set velocity : " + str(id(self)))
            None

    def GetFinalVel(self):
        separation = self.SteerTowards(self.AvoidCollision())
        alignment = self.GetNeighbourVelAverage()
        coheasion = self.SteerTowards(self.GetNeighbourPosAverage())
        mouse = self.SteerTowards( pygame.mouse.get_pos())

        # if bool(pygame.mouse.get_focused()):
        #     return np.average([alignment, mouse], axis=0)
        # else:
        #     return alignment

        # return np.sum([coheasion, alignment], axis=0)
        return alignment


    def AvoidCollision(self):
        array = []
        for b in self.neighbours:
            array.append(self.GetAvoidVel(b.GetPosition()))
        return np.average(array, axis=0)

    def GetAvoidVel(self, p):
        escape_angle = 10
        # print(p)
        p = list(p)
        cx = self.pos_x
        cy = self.pos_y
        s = math.sin(escape_angle)
        c = math.cos(escape_angle)
        # translate point back to origin:
        p[0] -= cx
        p[1] -= cy
        # rotate point
        xnew = p[0] * c - p[1] * s
        ynew = p[0] * s + p[1] * c

        # translate point back:
        p[0] = int(xnew + cx)
        p[1] = int(ynew + cy)
        return p

    def GetNeighbourPosAverage(self):
        pos_list = []
        for x in self.neighbours:
            pos_list.append(x.GetPosition())
        return np.average(pos_list, axis=0)

    def GetNeighbourVelAverage(self):
        vel_list = []
        for x in self.neighbours:
            vel_list.append(x.GetVelocity())
        return np.average(vel_list, axis=0)

    def Terminate(self):
        #print("Killing self (" + str(id(self)) + ")")
        self.terminate = True

    def StartTelemetry(self):
        # print("") 
        # print("[+] Telemetry for observing bird: ")
        while True:     
            if (self.terminate):
                break
            # print("\t Neighbour Count : " + str(len(self.neighbours)) + " X : " + str(int(self.pos_x)) + " Y : " + str(int(self.pos_y)) + " VX : " + str(self.speed_x) + " VY : " + str(self.speed_y), end='\r')
            time.sleep(0.25)


    
    def GetEquationOfLine(self, points):
        x_coords, y_coords = zip(*points)
        A = np.vstack([x_coords,np.ones(len(x_coords))]).T
        m, c = np.lstsq(A, y_coords)[0]
        return (m,c)

    def SteerTowards(self, target):
        try:
            traget = pygame.math.Vector2(target[0], target[1])
            start  = pygame.math.Vector2(self.pos_x, self.pos_y)
            delta = traget - start
            distance = delta.length() 
            direction = delta.normalize()
            vel = direction * 1
            # self.speed_x = vel[0]
            # self.speed_y = vel[1]

            return (vel[0], vel[1])
        except:
            # print("Normal Failed...")
            None

class Environment:
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1000, 700))
    # birdList = []
    # birdArray = weakref.WeakValueDictionary()
    birdArray = []
    clock = pygame.time.Clock()
    boid_mem = pygame.image.load("bird.png")
    boid_mem = pygame.transform.scale(boid_mem, (10, 13))
    threadList = []

    resx = 0
    resy = 0

    done = False
    Running = False
    ObserverAdded = False

    def AddBoidArray(self, count):
        print("Creating " + str(count) + " bird threads...")
        # if not self.Running:
        if True:
            for x in range(0, count):
                bird = Bird((self.resx, self.resy))
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
                bird = Bird((self.resx, self.resy))
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

    def StartConsole(self):
        console_thread = threading.Thread(target=self.EnterConsole)
        console_thread.start()

    def EnterConsole(self):
        print("")
        print("[!] Console Active...")
        while self.Running:
            in_string = input("PyBoids:~ ")
            in_string = in_string.split(" ")
            first_comm = in_string[0]

            try:
                if (first_comm.__eq__("add")):
                    self.AddBoidArray(int(in_string[1]))
                else:
                    print("Invalid Command")
            except:
                print("Malformed Command")

    def Start(self):
            self.Running = True
            while not self.done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.done = True
                        self.Running = False
                        print("Killing " + str(len(self.birdArray)) + " bird threads...")
                        for thread in self.birdArray:
                            thread.Terminate()

                # Clear the screen
                self.screen.fill((0, 0, 0))

                # Update ship neighbours
                for bird_c in self.birdArray:
                    neighbours = []
                    for bird_n in self.birdArray:
                        if (bird_n != bird_c):
                            if (self.CalculateDistance((bird_c.pos_x, bird_c.pos_y), (bird_n.pos_x, bird_n.pos_y)) < bird_n.visibility_range):
                                neighbours.append(bird_n)

                                # if the current bird is an observing bird, draw the ranges
                                if (bird_c.observing):
                                    pygame.draw.line(self.screen, (0, 100, 0), bird_n.GetPosition(), bird_c.GetPosition(), 1)

                    # assign the neighbour list of the current bird
                    bird_c.neighbours = neighbours

                    # Draw the bords
                    surf = pygame.transform.rotate(bird_c.sprite, bird_c.rotation)
                    if (bird_c.observing):
                        pygame.draw.circle(self.screen, (100, 0, 0), bird_c.GetPosition(), bird_n.visibility_range, 1)   
                    self.screen.blit(surf, bird_c.GetSpritePosition())

                
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

    def __init__(self, resolution):
        self.resx = resolution[0]
        self.resy = resolution[1]
        self.screen = pygame.display.set_mode((self.resx, self.resy))

    # def Recall(self, oid):
    #     for obj in gc.get_objects():
    #         if id(obj) == oid:
    #             return obj

