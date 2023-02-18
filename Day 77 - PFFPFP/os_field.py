from random import randrange
import opensimplex
import math
import numpy as np
from PIL import Image, ImageDraw

TWO_PI = math.pi * 2

opensimplex.seed(randrange(0, 999))

cell_size = 5

rng = np.random.default_rng(seed=0)
ix, iy = rng.random(500//cell_size), rng.random(500//cell_size)
vectors = opensimplex.noise2array(ix, iy)

image = Image.new('RGB', (500, 500), color="#000")
pixels = image.load()
draw = ImageDraw.Draw(image)

colour = (255, 255, 255)

for i in range(1000):
    velocity = [1, 1]
    pos = [randrange(0, 500), randrange(0, 500)]
    prev_pos = pos

    for _ in range(100):
        pos = [sum(x) for x in zip(pos, velocity)]

        if pos[0] >= 500 or pos[1] >= 500 or pos[0] < 0 or pos[1] < 0: break
        
        angle = vectors[math.floor(pos[0]/cell_size), math.floor(pos[1]/cell_size)] * TWO_PI

        velocity[0] += math.cos(angle)
        velocity[1] += math.sin(angle)

        if velocity[0] > 0.5: velocity[0] = 0.5
        if velocity[1] > 0.5: velocity[1] = 0.5

        pos[0] = int(pos[0])
        pos[1] = int(pos[1])

        draw.line([tuple(prev_pos), tuple(pos)], fill=colour)
        prev_pos = pos

image.save('test.png')
