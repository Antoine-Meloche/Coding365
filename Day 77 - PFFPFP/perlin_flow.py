from PIL import Image, ImageDraw
from perlin_noise import PerlinNoise
import random
import math

from datetime import datetime

TWO_PI = math.pi * 2

num = input('How many images should be generated?: ')
start = datetime.now()

for j in range(int(num)):
    image = Image.new('RGB', (500, 500), color="#000000")
    pixels = image.load()
    draw = ImageDraw.Draw(image)

    noise = PerlinNoise(seed=random.uniform(0,999))

    for _ in range(10):
        color = [random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)]

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

            velocity[0] += math.cos(noise([x*.01, y*.01, 0.5]) * TWO_PI)
            velocity[1] += math.sin(noise([x*.01, y*.01, 0.5]) * TWO_PI)
    
            angle = math.atan(velocity[1] / velocity[0])
    
            velocity[0] = math.cos(angle) * 10
            velocity[1] = math.sin(angle) * 10

            color[0] += round(noise([i, 0, 0.5]))
            color[1] += round(noise([i, 500, 0.5]))
            color[2] += round(noise([i, 1000, 0.5]))

            draw.line([(prev_x, prev_y), (x, y)], fill=(color[0], color[1], color[2]))

    image.save(f'flow_{j}.png')
    print(f'flow_{j}.png saved')
    print(f'time: {datetime.now() - start}')
