import pyglet
from random import randint


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
