# -*- coding: utf-8 -*-

import os
from PIL import Image


def load_texture(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Texture file not found: {file_path}")

    image = Image.open(file_path)
    image = image.convert("RGBA")

    return image


class Texture(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.image = load_texture(file_path)
        self.width, self.height = self.image.size
