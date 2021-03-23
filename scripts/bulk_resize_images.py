from PIL import Image, ImageEnhance
import os

folder = r"C:\Users\greg\Downloads\200_200_images"

for root, dir_names, file_names in os.walk(folder):
	for file_name in file_names:
		path = os.path.join(root, file_name)
		print(path)
		image = Image.open(path)
		image = image.convert('RGBA')

		background_color = (255, 255, 255, 0)
		width, height = image.size
		if width > height:
			squared = Image.new(image.mode, (width, width), background_color)
			squared.paste(image, (0, (width - height) // 2))
		elif width < height:
			squared = Image.new(image.mode, (height, height), background_color)
			squared.paste(image, ((height - width) // 2, 0))
		else:
			squared = image

		squared.thumbnail((200, 200), Image.ANTIALIAS)
		squared.save(path, quality=95, optimize=True)
