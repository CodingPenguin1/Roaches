import pyglet
from random import randint
from math import inf


def distanceBetween(pointA, pointB):
    return ((pointA[0] - pointB[0])**2 + (pointA[1] - pointB[1])**2)**0.5


class Light(pyglet.sprite.Sprite):
    SPEED = 5

    def __init__(self, image, worldSize, brightness, radius, x=0, y=0,
                 # These are for pyglet
                 blend_src=770, blend_dest=771, batch=None, group=None, usage='dynamic', subpixel=False):
        super(Light, self).__init__(image, x=x, y=y, blend_src=blend_src, blend_dest=blend_dest, batch=batch, group=group, usage=usage, subpixel=subpixel)

        self.worldWidth, self.worldHeight = worldSize
        self.brightness = brightness  # Light value at the center of the light
        self.radius = radius  # How far the light reaches before becoming 0
        self.target = (randint(0, self.worldWidth), randint(0, self.worldHeight))

    def targetNearestRoach(self, roachList):
        minDistance = inf
        newTarget = self.target

        for roach in roachList:
            if roach.visible:
                distance = distanceBetween(self.position, roach.position)
                if distance < minDistance:
                    minDistance = distance
                    newTarget = roach.position

        self.target = newTarget
