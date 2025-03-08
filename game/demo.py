import math
from direct.actor.Actor import Actor
from direct.interval.MetaInterval import Sequence
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from panda3d.core import Point3, Vec3, Quat


class myApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()

        self.scene = self.loader.loadModel("models/environment")
        self.scene.reparentTo(self.render)
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

        # Create a panda model
        self.pandaActor = Actor("models/panda-model", {'walk': "models/panda-walk4"})
        self.pandaActor.setScale(0.0030, 0.003, 0.005)
        self.pandaActor.reparentTo(self.render)

        self.pandaActor.loop("walk")

        self.camera.reparentTo(self.pandaActor)
        self.camera.setPos(0, 0.2, 1.5)

        # Movement settings
        self.speed = 10  # Movement speed
        self.sensitivity = 0.002  # Mouse sensitivity
        self.keys = {"w": False, "s": False, "a": False, "d": False}

        # Accept key events
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(key + "-up", self.set_key, [key, False])

        self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2)

        self.taskMgr.add(self.updateMouseMovement, "updateMouseMovement")
        self.taskMgr.add(self.updateMovement, "updateMovement")

    def set_key(self, key, value):
        self.keys[key] = value

    def updateMouseMovement(self, task):
        md = self.win.getPointer(0)
        mouse_x = md.getX() - self.win.getXSize() // 2
        heading = self.pandaActor.getH() - mouse_x * self.sensitivity
        self.pandaActor.setH(heading)  # Update panda's heading

        mouse_y = md.getY() - self.win.getYSize() // 2

        # Adjust the camera's pitch based on mouse_y movement
        pitch = self.camera.getP() - mouse_y * self.sensitivity
        pitch = max(-20, min(20, pitch))

        quat = Quat()
        hpr = Vec3(self.pandaActor.getH(), pitch, 0)

        quat.setHpr(hpr)
        self.camera.setQuat(quat)

        # Reset the mouse position to the center of the screen
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

        # Move panda in the direction it's facing
        movement = self.pandaActor.getQuat().xform(move_direction) * self.speed * dt
        self.pandaActor.setPos(self.pandaActor.getPos() + movement)

        return task.cont  # Continue running the task


app = myApp()

app.run()