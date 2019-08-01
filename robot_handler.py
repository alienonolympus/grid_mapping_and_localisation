'''File containing the class controlling the robot'''
import random
from threading import Thread
from time import sleep

'''Controls the movement and sensing of the robot.'''
class RobotHandler(object):
    '''Initialises the robot.'''
    def __init__(self, robot, initial_direction = 'up'):
        self.robot = robot
        self.floor_thresh = 40
        self.prox_thresh = 60
        self.initial_direction = initial_direction

    '''Returns if there is an obstacle in front.'''
    def obstacle_in_front(self):
        return self.robot.get_proximity(0) > self.prox_thresh or self.robot.get_proximity(1) > self.prox_thresh
   
    '''Converts a grid path to directions.'''
    def path2directions(self, path, last_direction = 'up'):
        directions = []
        last_location = path.pop(0)
        for node in path:
            diff = map(lambda x, y: x - y, node, last_location)
            if diff == [0, 1]:
                if last_direction == 'right':
                    directions.append('forwards')
                elif last_direction == 'up':
                    directions.append('right')
                    directions.append('forwards')
                elif last_direction == 'left':
                    directions.append('right')
                    directions.append('right')
                    directions.append('forwards')
                elif last_direction == 'down':
                    directions.append('left')
                    directions.append('forwards')
                last_direction = 'right'
            elif diff == [1, 0]:
                if last_direction == 'right':
                    directions.append('left')
                    directions.append('forwards')
                elif last_direction == 'up':
                    directions.append('forwards')
                elif last_direction == 'left':
                    directions.append('right')
                    directions.append('forwards')
                elif last_direction == 'down':
                    directions.append('right')
                    directions.append('right')
                    directions.append('forwards')
                last_direction = 'up'
            elif diff == [0, -1]:
                if last_direction == 'right':
                    directions.append('right')
                    directions.append('right')
                    directions.append('forwards')
                elif last_direction == 'up':
                    directions.append('left')
                    directions.append('forwards')
                elif last_direction == 'left':
                    directions.append('forwards')
                elif last_direction == 'down':
                    directions.append('right')
                    directions.append('forwards')
                last_direction = 'left'
            elif diff == [-1, 0]:
                if last_direction == 'right':
                    directions.append('right')
                    directions.append('forwards')
                elif last_direction == 'up':
                    directions.append('right')
                    directions.append('right')
                    directions.append('forwards')
                elif last_direction == 'left':
                    directions.append('left')
                    directions.append('forwards')
                elif last_direction == 'down':
                    directions.append('forwards')
                last_direction = 'down'
            last_location = node
        return directions, last_direction
    
    '''Moves robot based on a list of directions.'''
    def move(self, directions):
        for direction in directions:
            if direction == 'forwards':
                self.forwards()
            elif direction == 'right':
                self.right()
            elif direction == 'left':
                self.left()
        self.robot.reset()
    
    '''Move robot forwards.'''
    def forwards(self):
        while self.robot.get_floor(0) > self.floor_thresh or self.robot.get_floor(1) > self.floor_thresh:
            if self.robot.get_floor(0) < self.floor_thresh:
                self.robot.set_wheel(0, 0)
                self.robot.set_wheel(1, 50)
            elif self.robot.get_floor(1) < self.floor_thresh:
                self.robot.set_wheel(0, 50)
                self.robot.set_wheel(1, 0)
            else:
                self.robot.set_wheel(0, 40)
                self.robot.set_wheel(1, 40)
        while self.robot.get_floor(0) < self.floor_thresh or self.robot.get_floor(1) < self.floor_thresh:
            self.robot.set_wheel(0, 40)
            self.robot.set_wheel(1, 40)
        self.robot.set_musical_note(40)
        self.robot.set_wheel(0, 0)
        self.robot.set_wheel(1, 0)
        sleep(0.1)
        self.robot.set_musical_note(0)
    
    '''Turns robot right.'''
    def right(self):
        while self.robot.get_floor(1) > self.floor_thresh:
            self.robot.set_wheel(0, 40)
            self.robot.set_wheel(1, -40)
        while self.robot.get_floor(1) < self.floor_thresh:
            self.robot.set_wheel(0, 40)
            self.robot.set_wheel(1, -40)
        #sleep(0.1)
        self.robot.set_musical_note(40)
        self.robot.set_wheel(0, 0)
        self.robot.set_wheel(1, 0)
        sleep(0.1)
        self.robot.set_musical_note(0)
    
    '''Turns robot left.'''
    def left(self):
        while self.robot.get_floor(0) > self.floor_thresh:
            self.robot.set_wheel(0, -40)
            self.robot.set_wheel(1, 40)
        while self.robot.get_floor(0) < self.floor_thresh:
            self.robot.set_wheel(0, -40)
            self.robot.set_wheel(1, 40)
        #sleep(0.1)
        self.robot.set_musical_note(40)
        self.robot.set_wheel(0, 0)
        self.robot.set_wheel(1, 0)
        sleep(0.1)
        self.robot.set_musical_note(0)
