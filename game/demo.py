import math
import sys

from direct.actor.Actor import Actor
from direct.interval.MetaInterval import Sequence
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from panda3d.core import Point3, Vec3, Quat, WindowProperties
import requests

from entity import Entity

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        self.captureMouse()
        self.setupControls()
        self.gravity = 30
        self.on_ground = True
        self.vertical_velocity = 0
        self.jump_speed = 10
        self.is_paused = False
        self.scene = self.loader.loadModel("models/environment")
        self.scene.reparentTo(self.render)
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

        self.setupCamera()

        # Accept key events
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(key + "-up", self.set_key, [key, False])

        self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2)

        self.taskMgr.add(self.updateMouseMovement, "updateMouseMovement")
        self.taskMgr.add(self.updateMovement, "updateMovement")

        textures = []
        url = "https://lfqdjc8cbikxmk-8888.proxy.runpod.net/james.png?str=1.0&prompt=smiling%20face&num=20"
        requests.get(url)
        for i in range(3):
            url = "https://lfqdjc8cbikxmk-8888.proxy.runpod.net/james.png?str=0.1&prompt=smiling%20face&num=4"
            res= requests.get(url)
            if res.status_code != 200:
                raise Exception("API endpoint failed")

            name = "textures/" + str(i) + ".png"
            with open(name, "wb") as f:
                f.write(res.content)

            textures.append(name)

        self.new_entity = Entity(self.render, self.loader, textures, self.camera, movementSpeed=4)
        self.taskMgr.add(self.new_entity.animateTexture, "animateTexture")
        self.taskMgr.add(self.new_entity.moveTowardsPlayer, "moveTowardsPlayer")


    def setupCamera(self):
        self.disableMouse()
        # Set initial camera position
        self.camera.setPos(0, 0, 3)
        # Movement settings
        self.speed = 10  # Movement speed
        self.sensitivity = 0.09  # Mouse sensitivity
        self.keys = {"w": False, "s": False, "a": False, "d": False, "space": False}
        # Fixed camera height above the ground
        self.camera_height = 5  # Adjust this value as needed
        self.camLens.setFov(100)

    def set_key(self, key, value):
        self.keys[key] = value

    def captureMouse(self):

        md = self.win.getPointer(0)

        properties = WindowProperties()
        properties.setCursorHidden(True)
        properties.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(properties)
        self.is_paused = False

    def setupControls(self):
        self.accept("escape", self.releaseMouse)
        self.accept("mouse1", self.captureMouse)


    def releaseMouse(self):
        properties = WindowProperties()
        self.is_paused = True
        properties.setCursorHidden(False)
        properties.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(properties)

    def updateMouseMovement(self, task):

        dt = globalClock.getDt()
        if self.is_paused:
            return task.cont

        # Get the mouse movement
        md = self.win.getPointer(0)
        mouseX = md.getX()
        mouseY = md.getY()

        # Calculate the change in mouse position
        mouseChangeX = mouseX - self.win.getXSize() // 2
        mouseChangeY = mouseY - self.win.getYSize() // 2

        # Update the camera's heading and pitch
        self.camera.setH(self.camera.getH() - mouseChangeX * self.sensitivity)
        self.camera.setP(min(90, max(self.camera.getP() - mouseChangeY * self.sensitivity, -90))) # Prevent flipping underside of player

        # Reset the mouse position to the center of the window
        self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2)

        return task.cont

    def updateMovement(self, task):
        dt = globalClock.getDt()  # Time since last frame

        # Handle movement
        move_direction = Vec3(0, 0, 0)
        if self.keys["w"]:
            move_direction += Vec3(0, 1, 0)
        if self.keys["s"]:
            move_direction += Vec3(0, -1, 0)
        if self.keys["a"]:
            move_direction += Vec3(-1, 0, 0)
        if self.keys["d"]:
            move_direction += Vec3(1, 0, 0)
        if self.keys["space"] and self.on_ground:
            self.on_ground = False
            self.vertical_velocity = self.jump_speed

        self.vertical_velocity += (-1) * self.gravity * dt

        # Normalize movement to avoid diagonal speed boost
        if move_direction.length() > 0:
            move_direction.normalize()

        # Move camera in the direction it's facing
        movement = self.camera.getQuat().xform(move_direction) * self.speed * dt
        new_pos = self.camera.getPos() + movement
        new_pos.z += self.vertical_velocity * dt

        if(new_pos.z < self.camera_height):

            # Lock the camera to the ground by fixing its Z-coordinate
            new_pos.z = self.camera_height
            self.on_ground = True
            self.vertical_velocity = 0

        self.camera.setPos(new_pos)

        return task.cont  # Continue running the task


app = MyApp()
app.run()
