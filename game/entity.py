# the class to create entities w/ animation n stuff

from panda3d.core import CardMaker

class Entity:
    def __init__(self, parent, loader, textures, size=[2, 2], pos=[0, 5, 5], hpr=[0, 0, 0]):
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

        self.card.setBillboardPointEye()
        self.index = 0

    def animateTexture(self, task):
        frame = self.textures[int(task.time % len(self.textures))]
        print(frame)

        texture = loader.loadTexture(frame)
        self.card.set_texture(texture)
        return task.cont

