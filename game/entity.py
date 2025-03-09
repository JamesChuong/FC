# the class to create entities w/ animation n stuff

from panda3d.core import CardMaker, Texture
from math import sqrt
import requests
import time

class Entity:
    def __init__(self, parent, loader, textures, camera, size=[2, 2], pos=[0, 5, 5], hpr=[0, 0, 0], movementSpeed=0.01):
        if loader is None or parent is None or textures is None:
            raise Exception("you must pass a parent, loader and textures")

        cm = CardMaker("card")
        cm.set_frame(-size[0], size[0], -size[1], size[1])
        self.card = parent.attach_new_node(cm.generate())

        self.texture = loader.loadTexture(textures[0])
        self.card.set_texture(self.texture)

        self.textures = textures
        self.card.set_pos(pos[0], pos[1], pos[2])
        self.card.set_hpr(hpr[0], hpr[1], hpr[2])
        self.animationSpeed = 10 # number of frames before updating texture
        self.movementSpeed = movementSpeed
        self.camera = camera

        self.card.setBillboardPointEye()
        self.index = 0

    def animateTexture(self, task):
        frame = self.textures[int(task.time % len(self.textures))]

        texture = loader.loadTexture(frame)
        # texture = Texture()
        # texture.load(self.fetch_image())
        self.card.set_texture(texture)

        # time.sleep(1)
        return task.cont

    def moveTowardsPlayer(self, task):
        card_pos = self.card.get_pos()
        player_pos = self.camera.get_pos()

        direction = player_pos - card_pos 
        norm = sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2)
        direction = (direction / norm) * self.movementSpeed
        print(direction)

        self.card.set_pos(card_pos[0] + direction[0], card_pos[1] + direction[1], card_pos[2])

        return task.cont

    def fetch_image(self):
        url = "https://lfqdjc8cbikxmk-8888.proxy.runpod.net/james.png"
        res= requests.get(url)

        if res.status_code == 200:
            self.texture = res.content
        else:
            raise Exception("API endpoint failed")
        
