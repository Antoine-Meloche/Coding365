from PIL import Image, ImageDraw
from perlin_noise import PerlinNoise
from random import randrange
import math
import copy

TWO_PI = math.pi * 2

inc = 0
c = 0
cols = 0
rows = 0
zOff = 0
particles = []
flowField = []

colour = (randrange(0, 255), randrange(0, 255), randrange(0, 255), 3)

image = Image.new('RGB', (500, 500), color='#000000')
draw = ImageDraw.Draw(image)

noise = PerlinNoise(randrange(0, 999))

def setup():
    c = 10
    inc = 0.1
    cols = math.floor(500 / c)
    rows = math.floor(500 / c)

    for i in range(10000):
        particles.append(Particle())
        # Particle()

def draw():
    zOff = 0
    yOff = 0
    for y in range(rows):
        xOff = 0

        for x in range(cols):
            index = x + y * cols
            angle = noise([xOff, yOff, zOff]) * TWO_PI
            vec = (math.cos(angle), math.sin(angle))
            flowField[index] = vec
            xOff += inc
        
        yOff += inc
        zOff += 0.0002

    for particle in particles:
        particle.update()
        particle.edges()
        particle.show()
        particle.follow(flowField)

class Particle():
    pos = (randrange(0, 500), randrange(0, 500))
    vel = (0, 0)
    acc = (0, 0)
    maxspeed = 1

    prev_position = copy.deepcopy(pos)

    def follow(self, vectors):
        x = math.floor(self.pos[0] / c)
        y = math.floor(self.pos[1] / c)
        index = x + y * cols
        force = vectors[index]
        self.applyForce(force)
    
    def update(self):
        self.vel = tuple(map(sum, zip(self.vel, self.acc)))
        # FIXME: vel.limit()
        self.pos = tuple(map(sum, zip(self.pos, self.vel)))
        self.acc = (0, 0)

    def applyForce(self, force):
        self.acc = tuple(map(sum, zip(self.acc, force)))

    def show(self):
        draw.line([self.pos, self.prev_position], fill=colour)
        self.updatePrev()

    def updatePrev(self):
        self.prev_position = self.pos

    def edges(self):
        if self.pos[0] > 500:
            self.pos = (0, self.pos[1])
            self.updatePrev()
        if self.pos[1] > 500:
            self.pos = (self.pos[0], 0)
            self.updatePrev()
        if self.pos[0] < 0:
            self.pos = (500, self.pos[1])
            self.updatePrev()
        if self.pos[1] < 0:
            self.pos = (self.pos[0], 500)
            self.updatePrev()


if __name__ == "__main__":
    setup()
    draw()
    image.save('test.png')
