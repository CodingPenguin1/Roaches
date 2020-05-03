import pyglet
from math import inf, atan2, cos, pi, sin, sqrt
import numpy as np


def headingBetween(pointA, pointB):
    return -np.degrees(atan2(pointB[1] - pointA[1], pointB[0] - pointA[0]))


def distanceBetween(pointA, pointB):
    return sqrt(pow(pointA[0] - pointB[0], 2) + pow(pointA[1] - pointB[1], 2))


def translate(value, minVal, maxVal):
    return float(value - minVal) / float(maxVal - minVal)


class Roach(pyglet.sprite.Sprite):
    INITIAL_HEALTH = 100
    MAX_SPEED = 10
    TURN_RATE = 4
    LIGHT_DAMAGE_FACTOR = 1

    def __init__(self, image, worldSize, x=0, y=0,
                 # These are for pyglet
                 blend_src=770, blend_dest=771, batch=None, group=None, usage='dynamic', subpixel=False):
        super(Roach, self).__init__(image, x=x, y=y, blend_src=blend_src, blend_dest=blend_dest, batch=batch, group=group, usage=usage, subpixel=subpixel)

        # For display
        self.position = [x, y]
        self.rotation = 0
        self.image = image

        # Keep the bugs in the world
        self.worldWidth, self.worldHeight = worldSize

        # For learning
        self.health = Roach.INITIAL_HEALTH
        self.fitness = 0
        self.brain = None
        self.genome = None
        self.genomeID = None

    def useBrain(self, light, genTimer):
        # 2 inputs: light level at center of bug and angle between the direction the bug is facing and the nearest light source
        # 2 outputs: how hard to turn and fast to go (these aren't instantaneous jumps)

        # Direction to the light
        lightDirection = headingBetween(self.position, light.position) - self.rotation
        lightDirection + 360
        lightDirection %= 360

        # Brightness of the light at the roach
        lightDistance = distanceBetween(self.position, light.position)
        lightLevel = 0
        if lightDistance < light.radius:
            lightLevel = light.brightness * ((light.radius - lightDistance) / light.radius)

        # Scale inputs to be in range [0, 1]
        adjustedDirection = translate(lightDirection, -180, 180)
        adjustedDistance = translate(lightLevel, 0, light.brightness)

        # Define input vector
        inputs = (adjustedDirection, adjustedDistance, 1.0)

        # Do the black magic and get outputs
        outputs = self.brain.activate(inputs) if self.brain is not None else (0, 0, 0, 0)

        # Update turning and speed
        self.rotation += (outputs[0] - outputs[1]) * Roach.TURN_RATE
        speed = abs(outputs[2] - outputs[3]) * Roach.MAX_SPEED
        self.position = (self.position[0] + speed * cos(pi * self.rotation / 180), self.position[1] - speed * sin(pi * self.rotation / 180))

        # Keep the bugs in the world
        self.position = (max(min(self.position[0], self.worldWidth), 0), max(min(self.position[1], self.worldHeight), 0))

        # Update health
        self.health -= lightLevel * Roach.LIGHT_DAMAGE_FACTOR

        # If health is 0, die
        if self.health <= 0:
            self.visible = False
            self.fitness = genTimer
