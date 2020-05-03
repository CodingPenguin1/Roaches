import threading
from random import randint
from time import sleep, time

import neat
import numpy as np
import pyglet
from pyglet.sprite import Sprite
from pyglet.window import key

from Lights import Light
from Roaches import Roach

# Global Constants
genNum = 0
GEN_TIME = 300
genStart = 0
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 1500, 1000
WORLD_SIZE = SCREEN_SIZE
NUM_ROACHES = 50
LIGHT_BRIGHTNESS = 5
LIGHT_RADIUS = 100
FRAMERATE = 60
speedModifier = 1
gameWindow = pyglet.window.Window(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, fullscreen=False)


@gameWindow.event
def on_draw():
    gameWindow.clear()
    backgroundBatch.draw()
    lightBatch.draw()
    roachBatch.draw()
    hudBatch.draw()
    generationInfoLabel.draw()
    fpsDisplay.draw()


def update(dt):
    global roachesAlive, roachSprites, oldKeyboard, genStart, lightSprite, speedModifier

    genTimer = int((time() - genStart) * int(speedModifier))

    if genTimer >= GEN_TIME:
        print("KILLING ALL BUGS")
        genStart = time()
        for roach in roachSprites:
            roach.visible = False
        roachesAlive = 0
        print("There are now {} roaches alive".format(roachesAlive))

    if keyboard[key.PLUS] or keyboard[key.EQUAL]:
        speedModifier *= 1.01

    elif keyboard[key.MINUS] or keyboard[key.UNDERSCORE]:
        speedModifier /= 1.01
        if speedModifier < 1:
            speedModifier = 1

    if not generationLock.locked():
        generationInfoLabel.text = "Generation {} - {} seconds - {} roaches alive - SPEED {}x".format(genNum, genTimer, roachesAlive, int(speedModifier))
        with generationLock:
            roachCount = 0
            roachesStillAlive = False
            for i in range(int(speedModifier)):
                roachCount = 0
                roachesStillAlive = False
                for roach in roachSprites:
                    if roach.visible:
                        roachCount += 1
                        roachesStillAlive = True
                        roach.useBrain(lightSprite, genTimer)

                # If light has reached target, find a new one
                if ((lightSprite.position[0] - lightSprite.target[0])**2 + (lightSprite.position[1] - lightSprite.target[1])**2)**0.5 < lightSprite.SPEED + 1:
                    lightSprite.target = (randint(0, SCREEN_WIDTH), randint(0, SCREEN_HEIGHT))

                # Move the light towards the target
                dx = lightSprite.target[0] - lightSprite.position[0]
                dy = lightSprite.target[1] - lightSprite.position[1]
                distance = (dx**2 + dy**2)**0.5
                lightSprite.position = (lightSprite.position[0] + dx * lightSprite.SPEED / distance, lightSprite.position[1] + dy * lightSprite.SPEED / distance)

            if not roachesStillAlive:
                roachesAlive = 0
            else:
                roachesAlive = roachCount


def trainingThread():
    winner = p.run(evalBugs)


def evalBugs(genomes, config):
    global roachImage, roachBatch, roachSprites, roachesAlive, genStart, genNum

    with generationLock:
        for i, (genomeID, genome) in enumerate(genomes):
            roach = roachSprites[i]
            roach.position = (randint(0, SCREEN_WIDTH), randint(0, SCREEN_HEIGHT))
            roach.rotation = randint(0, 360)
            roach.visible = True
            genome.fitness = 0
            roach.brain = neat.nn.FeedForwardNetwork.create(genome, config)
            roach.fitness = 0
            roach.genome = genome
            roach.genomeID = genomeID

        roachesAlive = len(genomes)

        genStart = time()

    while roachesAlive > 1:
        sleep(0.1)

    print("##### THE BUGS DIED #####")
    genNum += 1

    for roach in roachSprites:
        if roach.genome is not None:
            roach.genome.fitness = roach.fitness


if __name__ == '__main__':
    ##############################################################################
    ##########                        NEAT STUFF                        ##########
    ##############################################################################

    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'config')

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    ##############################################################################
    ##########                       PYGLET STUFF                       ##########
    ##############################################################################
    generationLock = threading.Lock()

    # Set the window background color
    pyglet.gl.glClearColor(0.3, 0.3, 0.3, 1.0)

    keyboard = key.KeyStateHandler()
    oldKeyboard = key.KeyStateHandler()
    gameWindow.push_handlers(keyboard)

    # Initialize game variables and stuff
    fpsDisplay = pyglet.window.FPSDisplay(window=gameWindow)

    backgroundBatch = pyglet.graphics.Batch()
    lightBatch = pyglet.graphics.Batch()
    roachBatch = pyglet.graphics.Batch()
    hudBatch = pyglet.graphics.Batch()

    pyglet.resource.path = ['resources']
    pyglet.resource.reindex()

    roachImage = pyglet.resource.image('images/roach.png')
    roachImage.anchor_x = roachImage.width / 2
    roachImage.anchor_y = roachImage.height / 2

    lightImage = pyglet.resource.image('images/light.png')
    lightImage.anchor_x = lightImage.width / 2
    lightImage.anchor_y = lightImage.height / 2

    generationInfoLabel = pyglet.text.Label('Hello, world',
                                            font_name=None,
                                            color=(0, 0, 0, 100),
                                            font_size=20,
                                            x=5, y=SCREEN_HEIGHT - 5,
                                            anchor_x='left', anchor_y='top')

    lightSprite = Light(lightImage, WORLD_SIZE, LIGHT_BRIGHTNESS, LIGHT_RADIUS,
                        x=randint(0, SCREEN_WIDTH), y=randint(0, SCREEN_HEIGHT),
                        batch=lightBatch)
    lightSprite.scale = LIGHT_RADIUS * 2 / lightImage.width

    roachSprites = []
    roachesAlive = 0
    for i in range(NUM_ROACHES):
        roach = Roach(roachImage, WORLD_SIZE, batch=roachBatch)
        roach.visible = False
        roachSprites.append(roach)

    # Create the generational training thread
    trainingThread = threading.Thread(target=trainingThread)

    trainingThread.start()

    pyglet.clock.schedule_interval(update, 1 / FRAMERATE)

    pyglet.app.run()
