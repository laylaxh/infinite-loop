from direct.showbase.InputStateGlobal import inputState
from direct.showbase.DirectObject import DirectObject

from direct.actor.Actor import Actor

from panda3d.core import Vec3
from panda3d.core import BitMask32

from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import ZUp


class Player(DirectObject):

    def __init__(self):

        # Input
        self.accept('space', self.doJump)

        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('reverse', 's')
        inputState.watchWithModifiers('turnLeft', 'a')
        inputState.watchWithModifiers('turnRight', 'd')

        health = 100
        self.isNotWalking = False
        self.isJumping = False

    def processInput(self, dt):
        speed = Vec3(0, 0, 0)
        omega = 0.0

        # Change speed of robot
        if inputState.isSet('forward'): speed.setY(24.0)
        if inputState.isSet('reverse'): speed.setY(-4.0)
        if inputState.isSet('left'):    speed.setX(-3.0)
        if inputState.isSet('right'):   speed.setX(3.0)
        if inputState.isSet('turnLeft'):  omega = 120.0
        if inputState.isSet('turnRight'): omega = -120.0

        if inputState.isSet('forward') or inputState.isSet('reverse') or inputState.isSet('left') or \
                inputState.isSet('right'):
            if self.isNotWalking is False:
                self.actorNP.loop("walk")
                self.isNotWalking = True

        else:
            if self.isNotWalking:
                self.actorNP.stop()
                self.actorNP.loop("idle")
                self.isNotWalking = False

        if self.character.isOnGround() and self.isJumping:
            if self.isNotWalking:
                self.actorNP.stop("jump")
                self.actorNP.loop("walk")
                self.isJumping = False

        self.character.setAngularMovement(omega)
        self.character.setLinearMovement(speed, True)

    def createPlayer(self, render, world):
        h = 3.38
        w = 0.4
        shape = BulletCapsuleShape(w + 0.3, h - 2 * w, ZUp)

        self.character = BulletCharacterControllerNode(shape, 0.4, 'Robot')
        self.characterNP = render.attachNewNode(self.character)
        self.characterNP.setPos(2, 0, 18)

        self.characterNP.setH(45)
        self.characterNP.setCollideMask(BitMask32.allOn())
        world.attachCharacter(self.character)

        self.actorNP = Actor('../models/robot/lack.egg', {
            'walk': '../models/robot/lack-run.egg',
            'idle': '../models/robot/lack-idle.egg',
            'jump': '../models/robot/lack-jump.egg',
            'land': '../models/robot/lack-land.egg',
            'damage': '../models/robot/lack-damage.egg'})

        self.actorNP.reparentTo(self.characterNP)
        self.actorNP.setScale(0.15)
        self.actorNP.setH(180)
        self.actorNP.setPos(0, 0, -0.06)

    def doJump(self):
        self.isJumping = True

        # self.jump = loader.loadSfx("../sounds/jump.mp3")
        # self.jump.setVolume(0.8)

        self.character.setMaxJumpHeight(18.0)
        self.character.setJumpSpeed(8.0)
        self.character.doJump()
        self.actorNP.play("jump")
        self.actorNP.setPlayRate(0.8, "jump")
        # self.actorNP.play("land")
        # self.actorNP.setPlayRate(0.8, "land")

    def startPosLevel1(self):
        self.characterNP.setPos(2, 0, 5)

    def startPosLevel2(self):
        self.characterNP.setPos(-218, 496, 5)

    def cameraFollow(self, floater):
        base.disableMouse()

        desiredPos = self.characterNP.getPos() + self.characterNP.getQuat().xform(Vec3(3, -20, 6.5))
        base.camera.setPos(desiredPos)

        # If the camera is too far from robot, move it closer.
        # If the camera is too close to robot, move it farther.
        camvec = self.characterNP.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if (camdist > 20.0):
            base.camera.setPos(base.camera.getPos() + camvec * (camdist - 20))
            camdist = 20.0
        if (camdist < 10.0):
            base.camera.setPos(base.camera.getPos() - camvec * (10 - camdist))
            camdist = 10.0

        # Camera follows floater that's slightly above player
        floater.setPos(self.characterNP.getPos())
        floater.setZ(self.characterNP.getZ() + 2.5)
        base.camera.lookAt(floater)


