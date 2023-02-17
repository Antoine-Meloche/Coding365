from PIL import Image, ImageDraw
import math
import opensimplex
from random import randrange
import random
from io import BytesIO


def gen_osfield(colour):
    colour = list(colour)
    TWO_PI = math.pi * 2

    image = Image.new('RGB', (500, 500), color="#000")
    pixels = image.load()
    draw = ImageDraw.Draw(image)

    opensimplex.seed(randrange(0,999))

    for _ in range(10):
        x = random.randrange(0, 500)
        y = random.randrange(0, 500)

        velocity = [1, 1]
    
        for i in range(10000):
            prev_x, prev_y = x, y

            x += velocity[0]
            y += velocity[1]
    
            if x >= 500:
                x -= 500
                prev_x = x
            elif x <= 0:
                x += 500
                prev_x = x

            if y >= 500:
                y -= 500
                prev_y = y
            elif y <= 0:
                y += 500
                prev_y = y

            velocity[0] += math.cos(opensimplex.noise2(x=x*.001, y=y*.001) * TWO_PI)
            velocity[1] += math.sin(opensimplex.noise2(x=x*.001, y=y*.001) * TWO_PI)
    
            angle = math.atan(velocity[1] / velocity[0])
    
            velocity[0] = math.cos(angle) * 10
            velocity[1] = math.sin(angle) * 10

            colour[0] += randrange(0, 1)
            colour[1] += randrange(0, 1)
            colour[2] += randrange(0, 1)

            draw.line([(prev_x, prev_y), (x, y)], fill=tuple(colour))

    img_io = BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io
