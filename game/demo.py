from direct.actor.Actor import Actor
from direct.interval.MetaInterval import Sequence
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task import Task
from panda3d.core import (Vec3, WindowProperties, AmbientLight, 
                         DirectionalLight, CardMaker, CollisionTraverser, 
                         CollisionNode, CollisionSphere, CollisionHandlerPusher)
import requests

from entity import Entity

class GameConstants:
    GRAVITY_ACCELERATION = 100
    INITIAL_JUMP_VELOCITY = 30
    PLAYER_MOVEMENT_SPEED = 20
    MOUSE_SENSITIVITY = 0.09
    PLAYER_HEIGHT = 5

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        self.initializeGameProperties()
        
        self.setupCollisions()

        self.setupEnvironment() 

        self.setupCamera()
        
        textures = []
        textures.append('textures/0.png', 'textures/1.png')

        # url = "https://lfqdjc8cbikxmk-8888.proxy.runpod.net/james.png?str=1.0&prompt=smiling%20face&num=20"
        # requests.get(url)
        # for i in range(3):
        #     url = "https://lfqdjc8cbikxmk-8888.proxy.runpod.net/james.png?str=0.1&prompt=smiling%20face&num=4"
        #     res= requests.get(url)
        #     if res.status_code != 200:
        #         raise Exception("API endpoint failed")
        #     name = "textures/" + str(i) + ".png"
        #     with open(name, "wb") as f:
        #         f.write(res.content)
        #     textures.append(name)

        self.disableMouse()

        # Key bindings
        self.accept("escape", self.releaseMouse)
        self.accept("mouse1", self.captureMouse)
        self.accept("w", self.set_key, ["w", True])
        self.accept("w-up", self.set_key, ["w", False])
        self.accept("s", self.set_key, ["s", True])
        self.accept("s-up", self.set_key, ["s", False])
        self.accept("a", self.set_key, ["a", True])
        self.accept("a-up", self.set_key, ["a", False])
        self.accept("d", self.set_key, ["d", True])
        self.accept("d-up", self.set_key, ["d", False])
        self.accept("space", self.set_key, ["space", True])
        self.accept("space-up", self.set_key, ["space", False])
        
        # Add tities
        self.new_entity = Entity(self.render, self.loader, textures, self.camera, movementSpeed=4)

        # Add tasks to task manager
        self.taskMgr.add(self.updateMouseMovement, "MouseMovementTask")
        self.taskMgr.add(self.updateMovement, "MovementTask")
        self.taskMgr.add(self.new_entity.animateTexture, "animateTexture")
        self.taskMgr.add(self.new_entity.moveTowardsPlayer, "moveTowardsPlayer")
        
        # Center mouse
        self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2)
        self.captureMouse()

    def initializeGameProperties(self):
        self.game_paused = False
        
        self.player_height = GameConstants.PLAYER_HEIGHT

        self.mouse_sensitivity = GameConstants.MOUSE_SENSITIVITY
        self.player_speed = GameConstants.PLAYER_MOVEMENT_SPEED

        self.player_on_ground = True
        self.player_vertical_velocity = 0
        self.gravity_acceleration = GameConstants.GRAVITY_ACCELERATION
        self.jump_velocity = GameConstants.INITIAL_JUMP_VELOCITY

        self.player_input = {"w": False, "s": False, "a": False, "d": False, "space": False}

    def setupCollisions(self):
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
    
        self.player_collider = self.camera.attachNewNode(CollisionNode('player'))
        self.player_collider.node().addSolid(CollisionSphere(0, 0, 0, 1.0))
    
        self.cTrav.addCollider(self.player_collider, self.pusher)
        self.pusher.addCollider(self.player_collider, self.camera)
    
        self.player_collider.show()

    def setupEnvironment(self):
        self.environment = self.loader.loadModel("models/environment")
        self.environment.reparentTo(self.render)
        self.environment.setScale(0.25, 0.25, 0.25)
        self.environment.setPos(-8, 42, 0)

        alight = AmbientLight('ambient')
        alight.setColor((0.3, 0.3, 0.3, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        dlight = DirectionalLight('directional')
        dlight.setColor((0.8, 0.8, 0.8, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(45, -45, 0)
        self.render.setLight(dlnp)
       
        cm = CardMaker('ground')
        cm.setFrame(-20, 20, -20, 20)
        ground = self.render.attachNewNode(cm.generate())
        ground.setPos(0, 0, 0)
        ground.setP(-90)
        ground.setColor((0.3, 0.3, 0.3, 1))

    def setupCamera(self):
        self.camera.setPos(0, 0, self.player_height)
        self.camLens.setFov(100)

    def set_key(self, key_pressed, is_pressed):
        self.player_input[key_pressed] = is_pressed

    def captureMouse(self):
        window_properties = WindowProperties()
        window_properties.setCursorHidden(True)
        window_properties.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(window_properties)
        self.game_paused = False

    def releaseMouse(self):
        window_properties = WindowProperties()
        window_properties.setCursorHidden(False)
        window_properties.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(window_properties)
        self.game_paused = True

    def updateMouseMovement(self, task):
        if self.game_paused:
            return task.cont

        mouse_data = self.win.getPointer(0)
        current_mouse_x, current_mouse_y = mouse_data.getX(), mouse_data.getY()
        
        mouse_delta_x = current_mouse_x - self.win.getXSize() // 2
        mouse_delta_y = current_mouse_y - self.win.getYSize() // 2

        self.camera.setH(self.camera.getH() - mouse_delta_x * self.mouse_sensitivity)
        self.camera.setP(min(90, max(self.camera.getP() - mouse_delta_y * self.mouse_sensitivity, -90)))

        self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2)
        return Task.cont

    def updateMovement(self, task):
        if self.game_paused:
            return Task.cont
            
        delta_time = globalClock.getDt()
        movement_direction = self.calculateMoveDirection()
        
        # Apply gravity and jumping
        self.player_vertical_velocity += (-1) * self.gravity_acceleration * delta_time
        
        if movement_direction.length() > 0:
            movement_direction.normalize()

        # Calculate new position
        player_movement = self.camera.getQuat().xform(movement_direction) * self.player_speed * delta_time
        new_position = self.camera.getPos() + player_movement
        new_position.z += self.player_vertical_velocity * delta_time

        # Ground collision check
        if new_position.z < self.player_height:
            new_position.z = self.player_height
            self.player_on_ground = True
            self.player_vertical_velocity = 0

        # Update position
        self.camera.setPos(new_position)
        
        # collisions
        self.cTrav.traverse(self.render)
        
        return Task.cont

    def calculateMoveDirection(self):
        movement_direction = Vec3(0, 0, 0)
        if self.player_input["w"]: movement_direction += Vec3(0, 1, 0)
        if self.player_input["s"]: movement_direction += Vec3(0, -1, 0)
        if self.player_input["a"]: movement_direction += Vec3(-1, 0, 0)
        if self.player_input["d"]: movement_direction += Vec3(1, 0, 0)
        if self.player_input["space"] and self.player_on_ground:
            self.player_on_ground = False
            self.player_vertical_velocity = self.jump_velocity
        return movement_direction

if __name__ == "__main__":
    app = MyApp()
    app.run()