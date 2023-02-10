from PIL import Image, ImageDraw
from perlin_noise import PerlinNoise
import random
import math

TWO_PI = math.pi * 2

num = input('How many images should be generated?: ')

for j in range(int(num)):
    image = Image.new('RGB', (2000, 2000), color="#000000")
    pixels = image.load()
    draw = ImageDraw.Draw(image)

    noise = PerlinNoise(seed=random.uniform(0,999))

    for _ in range(10):
        color = [random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)]

        x = random.randrange(0, 1500)
        y = random.randrange(0, 1500)

        velocity = [1, 1]
    
        for i in range(10000):
            prev_x, prev_y = x, y

            x += velocity[0]
            y += velocity[1]
    
            if x >= 1500:
                x -= 1500
                prev_x = x
            elif x <= 0:
                x += 1500
                prev_x = x

            if y >= 1500:
                y -= 1500
                prev_y = y
            elif y <= 0:
                y += 1500
                prev_y = y

            velocity[0] += math.cos(noise([x*.01, y*.01, 0.5]) * TWO_PI)
            velocity[1] += math.sin(noise([x*.01, y*.01, 0.5]) * TWO_PI)
    
            angle = math.atan(velocity[1] / velocity[0])
    
            velocity[0] = math.cos(angle) * 10
            velocity[1] = math.sin(angle) * 10

            color[0] += round(noise([i, 0, 0.5]))
            color[1] += round(noise([i, 500, 0.5]))
            color[2] += round(noise([i, 1000, 0.5]))

            draw.line([(prev_x+250, prev_y+250), (x+250, y+250)], fill=(color[0], color[1], color[2]))

    image.save(f'flow_{j}.png')
    print(f'flow_{j}.png saved')
