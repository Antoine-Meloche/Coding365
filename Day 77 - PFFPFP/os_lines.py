import opensimplex
from random import randrange
import random
from PIL import Image


def gen_lines(colour):
	opensimplex.seed(randrange(0, 999))

	image = Image.new('RGB', (750, 750), color="#000")
	pixels = image.load()

	for i in range(15):
		for z in range(2):
		    for x in range(0, 750):
		        y = opensimplex.noise2(x/75, i+z*10)*30+50*(i+1)
		        try:
		        	pixels[x,y] = colour
		        except Exception:
		        	pass

	img_io = BytesIO()
	image.save(img_io, 'PNG')
	img_io.seek(0)
	return img_io
	#image.save('random.png')
