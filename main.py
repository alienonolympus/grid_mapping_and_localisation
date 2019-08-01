'''Main file connecting the GUI and robot together.'''
import sys
from threading import Thread
from HamsterAPI.comm_usb import RobotComm
from gui import GUI
from robot_handler import RobotHandler
from grid import Grid

# Constants
MAX_ROBOT_NUM = 1

def main():
    robot_comm = RobotComm(MAX_ROBOT_NUM)
    robot_comm.start()
    robot_list = robot_comm.robotList
    
    while not robot_list:
        pass

    robot = RobotHandler(robot_list[0])
    grid = Grid(500, 500)
    gui = GUI(robot, grid)
    gui.start()


if __name__ == '__main__':
    sys.exit(main())