import math
import sys

from direct.actor.Actor import Actor
from direct.interval.MetaInterval import Sequence
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from panda3d.core import Point3, Vec3, Quat, WindowProperties


class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        self.captureMouse()
        self.setupControls()

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

    def setupCamera(self):

        self.disableMouse()
        # Set initial camera position
        self.camera.setPos(0, 0, 3)
        # Movement settings
        self.speed = 10  # Movement speed
        self.sensitivity = 0.09  # Mouse sensitivity
        self.keys = {"w": False, "s": False, "a": False, "d": False}
        # Fixed camera height above the ground
        self.camera_height = 5  # Adjust this value as needed
        self.camLens.setFov(100)

    def set_key(self, key, value):
        self.keys[key] = value

    def captureMouse(self):

        md = self.win.getPointer(0)
        self.lastMouseX = md.getX()
        self.lastMouseY = md.getY()

        properties = WindowProperties()
        properties.setCursorHidden(True)
        properties.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(properties)

    def setupControls(self):
        self.accept("escape", self.releaseMouse)
        self.accept("mouse1", self.captureMouse)

    def releaseMouse(self):
        properties = WindowProperties()
        properties.setCursorHidden(False)
        properties.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(properties)

    def updateMouseMovement(self, task):
        """
        Update the camera's orientation based on mouse movement.
        """
        dt = globalClock.getDt()

        # Get the mouse movement
        md = self.win.getPointer(0)
        mouseX = md.getX()
        mouseY = md.getY()

        # Calculate the change in mouse position
        mouseChangeX = mouseX - self.win.getXSize() // 2
        mouseChangeY = mouseY - self.win.getYSize() // 2

        # Update the camera's heading and pitch
        self.camera.setH(self.camera.getH() - mouseChangeX * self.sensitivity)
        self.camera.setP(min(90, max(self.camera.getP() - mouseChangeY * self.sensitivity, -90)))

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

        # Normalize movement to avoid diagonal speed boost
        if move_direction.length() > 0:
            move_direction.normalize()

        # Move camera in the direction it's facing
        movement = self.camera.getQuat().xform(move_direction) * self.speed * dt
        new_pos = self.camera.getPos() + movement

        # Lock the camera to the ground by fixing its Z-coordinate
        new_pos.z = self.camera_height
        self.camera.setPos(new_pos)

        return task.cont  # Continue running the task


app = MyApp()
app.run()