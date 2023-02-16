from PIL import Image
import math
import opensimplex
from random import randrange
from io import BytesIO

def gen_circle(colour):

    TWO_PI = math.pi * 2

    image = Image.new('RGB', (500, 500), color="#000000")
    pixels = image.load()

    radius = 200

    for _ in range(10):
        opensimplex.seed(randrange(0, 999))
        angle = 0
        x1 = 0
        y1 = 0
        while angle < TWO_PI:
            x1 = math.cos(angle)
            y1 = math.sin(angle)
            r = radius + opensimplex.noise2(x=x1, y=y1) * radius/4
            x = r * x1 + 250
            y = r * y1 + 250

            try:
                pixels[x,y] = colour
            except IndexError:
                pass

            angle += 0.005

        radius -= 30

    img_io = BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io
    #image.save('circles.png')
