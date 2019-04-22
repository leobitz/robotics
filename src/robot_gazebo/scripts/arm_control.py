#!/usr/bin/env python
import rospy

from robot_lib.msg import ArmAngles
from geometry_msgs.msg import Vector3

import constants as Constant
import math


class ArmControl:
    def changeArmPosition(self, desiredPose):
        print(desiredPose)
        finArmAngles = self.moveArm(desiredPose)

        if finArmAngles is None:
            return ArmAngles()
        else:
            finArmAngles = self.getBestAngles(desiredPose, finArmAngles)

        finalArmAngles = ArmAngles()
        finalArmAngles.armBase_armBaseTop = self.radToDeg(finArmAngles[0])
        finalArmAngles.armBaseTop_arm1 = self.radToDeg(finArmAngles[1])
        finalArmAngles.arm1_arm2 = self.radToDeg(finArmAngles[2])
        finalArmAngles.arm2_gripper = self.radToDeg(finArmAngles[3])

        finalArmAngles.P = Constant.P
        finalArmAngles.I = Constant.I
        finalArmAngles.D = Constant.D

        print(finalArmAngles)
        return finalArmAngles

    def getBestAngles(self, finalPose, candidateAngles):
        if abs(candidateAngles[0][0]) > math.pi:
            minBase = candidateAngles[0][1]
        else:
            minBase = candidateAngles[0][0]
        print(candidateAngles[0], " = ", minBase)
        return (
            minBase,
            (math.pi / 2) - candidateAngles[1][1][0],
            candidateAngles[1][1][1],
            -(candidateAngles[1][1][2]),
        )

    def getCurrentArmAngles(self):
        ang = ArmAngles()
        ang.armBase_armBaseTop = 10
        ang.armBaseTop_arm1 = 10
        ang.arm1_arm2 = 10
        ang.arm2_gripper = 10

        return ang

    def isPositionReachable(self, finalPose):
        totArmLength = Constant.ARM_1 + Constant.ARM_2

        if finalPose.z > totArmLength - Constant.ARM_BASE_TOP:
            return False

        distance = math.sqrt(finalPose.x ** 2 + finalPose.y ** 2 + finalPose.z ** 2)

        if distance > totArmLength:
            return False

        return True

    def getInitHeight(self):
        x = Constant.MAIN_LENGTH

        return x / 10 + x / 6 + x / 6 + x / 20 + x / 16

    def getBestBaseAng(self, finalPose, finalBaseAngle):
        if finalPose.x >= 0 and finalPose.y >= 0:
            return finalBaseAngle

        elif finalPose.x < 0 and finalPose.y >= 0:
            return math.pi - finalBaseAngle

        elif finalPose.x < 0 and finalPose.y < 0:
            return math.pi + finalBaseAngle

        else:
            return -1 * finalBaseAngle

    def getArmBaseAng(self, finalPose):
        # return self.getBestBaseAng(finalPose, math.atan2(finalPose.y, finalPose.x))
        return math.atan2(finalPose.y, finalPose.x)

    def moveArm(self, finalPose):
        if self.isPositionReachable(finalPose):
            armBaseAng = self.getArmBaseAng(finalPose)

            ny = float(finalPose.z)
            nx = math.sqrt(finalPose.x ** 2 + finalPose.y ** 2)

            beta = math.acos(
                ((Constant.ARM_1 ** 2) + (Constant.ARM_2 ** 2) - (nx ** 2) - (ny ** 2))
                / (2.0 * Constant.ARM_1 * Constant.ARM_2)
            )
            alpha = math.acos(
                ((nx ** 2) + (ny ** 2) + (Constant.ARM_1 ** 2) - (Constant.ARM_2 ** 2))
                / (2.0 * Constant.ARM_1 * math.sqrt((nx ** 2) + (ny ** 2)))
            )
            gamma = math.atan2(ny, nx)

            if armBaseAng < 0:
                baseAngles = [armBaseAng + (2 * math.pi), armBaseAng]
            else:
                baseAngles = [armBaseAng, armBaseAng - (2 * math.pi)]

            armAngles = [
                (gamma - alpha, beta - math.pi, (gamma - alpha + beta - math.pi)),
                (gamma + alpha, math.pi - beta, (math.pi - beta - gamma - alpha)),
            ]
            print(armAngles)
            return (baseAngles, armAngles)

        else:
            print("Position unreachable")
            return None

    def radToDeg(self, rad):
        return rad * 180 / math.pi


armControl = ArmControl()
pub = None


def main():
    global pub
    # p = Vector3(2.0/3, 2.0/3, 0)
    # callback(p)
    rospy.init_node("IK")

    sub = rospy.Subscriber("/my_car/arm_effector/pose", Vector3, callback)
    pub = rospy.Publisher("/my_car/joint/angles", ArmAngles, queue_size=10)

    rospy.spin()


def callback(desiredPose):
    global pub

    pub.publish(armControl.changeArmPosition(desiredPose))
    # armControl.changeArmPosition(desiredPose)


if __name__ == "__main__":
    main()


armControl = ArmControl()
pub = None


def main():
    global pub
    # p = Vector3(2.0/3, 2.0/3, 0)
    # callback(p)
    rospy.init_node("IK")

    sub = rospy.Subscriber("/my_car/arm_effector/pose", Vector3, callback)
    pub = rospy.Publisher("/my_car/joint/angles", ArmAngles, queue_size=10)

    rospy.spin()


def callback(desiredPose):
    global pub

    pub.publish(armControl.changeArmPosition(desiredPose))
    # armControl.changeArmPosition(desiredPose)


if __name__ == "__main__":
    main()