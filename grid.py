'''File containing the grid class and search class.'''
import random, math
from time import sleep

# Constants
DIRECTION_MAP = {
    'up': (1, 0),
    'right': (0, 1),
    'down': (-1, 0),
    'left': (0, -1)
}
DIRECTION_TURN_RIGHT = {
    'up': 'right',
    'right': 'down',
    'down': 'left',
    'left': 'up'
}
DIRECTION_TURN_LEFT = {
    'up': 'left',
    'left': 'down',
    'down': 'right',
    'right': 'up'
}
OPPOSITE_DIRECTIONS = {
    'up': 'down',
    'left': 'right',
    'down': 'up',
    'right': 'left'
}
DIRECTION_TO_ANGLE = {
    'right': 0.0,
    'up': math.pi / 2,
    'left': math.pi,
    'down': math.pi * 3 / 2
}
ANGLE_TO_MOVEMENT = {
    math.pi * 3 / 2: ['right'],
    math.pi: ['right', 'right'],
    math.pi / 2: ['left'],
    0: [],
    - math.pi / 2: ['right'],
    - math.pi: ['left, left'],
    - math.pi * 3 / 2: ['left']
}

'''Stores the grid in an object.'''
class Grid(object):
    '''Initialises grid object with the canvas with and height.'''
    def __init__(self, canvas_width, canvas_height):
        self.nodes = {}
        self.start_node = None
        self.goal_node = None
        self.grid_rows = None
        self.grid_columns = None
        self.obs_list = []
        self.node_display_locations={}
        self.canvas_width = float(canvas_width)
        self.canvas_height = float(canvas_height)
        self.row_height = None
        self.column_width = None
        self.mapping = False
        self.localising = False
        self.returning = False
        self.current_location = self.start_node
        self.current_direction = 'up'
        self.visited = []

    '''Sets the number of rows in the grid.'''
    def set_grid_rows(self, rows):
        self.grid_rows = int(rows)
        self.row_height = float(self.canvas_height) / float(self.grid_rows * 2.0 + 1.0)

    '''Sets the number of columns in the grid.'''
    def set_grid_cols(self, cols):
        self.grid_columns = int(cols)
        self.column_width = float(self.canvas_width) / float(self.grid_columns * 2.0 + 1.0)

    '''Adds a node.'''
    def add_node(self, name):
        self.nodes[name] = set([])

    '''Sets the starting node.'''
    def set_start(self, name):
        self.start_node = name
        self.current_location = self.start_node

    '''Returns the name of the starting node.'''
    def get_start_node(self):
        return self.start_node

    '''Sets the name of the goal node.'''
    def set_goal(self, name):
        self.goal_node = name

    '''Get the name of the goal node.'''
    def get_goal_node(self):
        return self.goal_node

    '''Add make two nodes each others' neighbours.'''
    def add_neighbour(self, node1, node2):
        self.nodes[node1].add(node2)
        self.nodes[node2].add(node1)

    '''Initialise the grid.'''
    def make_grid(self):
        for row in xrange(self.grid_rows):
            for column in xrange(self.grid_columns):
                if not [row, column] in self.obs_list:
                    self.add_node((row, column))

        for row in xrange(self.grid_rows):
            for column in xrange(self.grid_columns):
                if not [row, column] in self.obs_list:
                    difference = [(1, 0), (0, 1), (-1, 0), (0, -1)]
                    for diff in difference:
                        neighbour_row, neighbour_column = map(lambda x, y: x + y, (row, column), diff)
                        if 0 <= neighbour_row < self.grid_rows and 0 <= neighbour_column < self.grid_columns and not [neighbour_row, neighbour_column] in self.obs_list:
                            self.add_neighbour((row, column), (neighbour_row, neighbour_column))

    '''Compute where to display the grid.'''
    def compute_node_locations(self):
        for node in self.nodes:
            x = self.column_width * (2.0 * float(node[1]) + 1.5)
            y = self.canvas_height - self.row_height * (2.0 * float(node[0]) + 1.5)
            self.node_display_locations[node] = (x, y)

    '''Map the entire grid.'''
    def map(self, robot):
        count = 1
        while self.mapping:
            self.visited.append(self.current_location)
            if count % 5 == 0:
                pass
                if set(self.visited) == set(self.connected_nodes(self.start_node)):
                    self.mapping = False
                    break
            node_in_front = tuple(map(lambda x, y: x + y, self.current_location, DIRECTION_MAP[self.current_direction]))
            if robot.obstacle_in_front() or node_in_front in self.obs_list:
                if not node_in_front in self.obs_list and node_in_front != self.start_node:
                    self.obs_list.append(node_in_front)
                direction = False
                neighbours = []
                neighbours.append(node_in_front)
                for d in OPPOSITE_DIRECTIONS:
                    if d != self.current_direction and OPPOSITE_DIRECTIONS[d] != self.current_direction:
                        neighbours.append(tuple(map(lambda x, y: x + y, self.current_location, DIRECTION_MAP[d])))
                neighbours.append(tuple(map(lambda x, y: x + y, self.current_location, DIRECTION_MAP[OPPOSITE_DIRECTIONS[self.current_direction]])))
                for neighbour in neighbours:
                    if not neighbour in self.obs_list:
                        diff = tuple(map(lambda x, y: x - y, neighbour, self.current_location))
                        target_direction = None
                        for d in DIRECTION_MAP:
                            if DIRECTION_MAP[d] == diff:
                                target_direction = d
                                break
                        current_direction_angle = DIRECTION_TO_ANGLE[self.current_direction]
                        target_direction_angle = DIRECTION_TO_ANGLE[target_direction]
                        angle_diff = target_direction_angle - current_direction_angle
                        movement = ANGLE_TO_MOVEMENT[angle_diff]
                        robot.move(movement)
                        self.current_direction = target_direction
                        break
            else:
                if self.facing_border():
                    direction = random.choice(['left', 'right'])
                else:
                    direction = random.choice(['forwards', 'forwards', 'forwards', 'forwards', 'forwards', 'forwards', 'left', 'right'])
                if direction == 'forwards':
                    robot.forwards()
                    self.current_location = tuple(map(lambda x, y: x + y, self.current_location, DIRECTION_MAP[self.current_direction]))
                elif direction == 'left':
                    robot.left()
                    self.current_direction = DIRECTION_TURN_LEFT[self.current_direction]
                elif direction == 'right':
                    robot.right()
                    self.current_direction = DIRECTION_TURN_RIGHT[self.current_direction]
            count += 1
        robot.robot.set_musical_note(50)
        sleep(0.3)
        robot.robot.set_musical_note(0)

    '''Determine the location of the robot given a random direction and location.'''
    def localise(self, robot):
        possible_locations = self.connected_nodes(self.start_node)
        possible_directions = ['up', 'right', 'down', 'left']
        possible_places = [(possible_location[0], possible_location[1], possible_direction) for possible_location in possible_locations for possible_direction in possible_directions]
        while self.localising:
            if len(possible_places) == 1:
                break
            possible_places_in_front = [tuple(map(lambda x, y: x + y, (possible_place[0], possible_place[1]), DIRECTION_MAP[possible_place[2]]) + [possible_place[2]]) for possible_place in possible_places]
            if robot.obstacle_in_front():
                for i in xrange(len(possible_places)):
                    if not (possible_places_in_front[i][0], possible_places_in_front[i][1]) in self.obs_list:
                        possible_places[i] = False
                possible_places = filter(lambda x: x, possible_places)
                direction = random.choice(['left', 'right'])
                if direction == 'left':
                    robot.left()
                    possible_places = [(possible_place[0], possible_place[1], DIRECTION_TURN_LEFT[possible_place[2]]) for possible_place in possible_places]
                elif direction == 'right':
                    robot.right()
                    self.current_direction = DIRECTION_TURN_RIGHT[self.current_direction]
                    possible_places = [(possible_place[0], possible_place[1], DIRECTION_TURN_RIGHT[possible_place[2]]) for possible_place in possible_places]
            else:
                if self.facing_border():
                    direction = random.choice(['left', 'right'])
                else:
                    direction = random.choice(['forwards', 'forwards', 'forwards', 'forwards', 'forwards', 'forwards', 'left', 'right'])
                if direction == 'forwards':
                    robot.forwards()
                    possible_places = possible_places_in_front
                elif direction == 'left':
                    robot.left()
                    possible_places = [(possible_place[0], possible_place[1], DIRECTION_TURN_LEFT[possible_place[2]]) for possible_place in possible_places]
                elif direction == 'right':
                    robot.right()
                    possible_places = [(possible_place[0], possible_place[1], DIRECTION_TURN_RIGHT[possible_place[2]]) for possible_place in possible_places]
        self.current_location = (possible_places[0][0], possible_places[0][1])
        self.current_direction = possible_places[0][2]
        robot.robot.set_musical_note(50)
        sleep(0.3)
        robot.robot.set_musical_note(0)

    '''Return to start node.'''
    def return_to_start(self, robot):
        path = self.bfs(self.current_location, self.start_node)
        if path:
            directions, self.current_direction = robot.path2directions(path, self.current_direction)
            robot.move(directions)
        self.current_location = path[-1]
        robot.robot.set_musical_note(50)
        sleep(0.3)
        robot.robot.set_musical_note(0)
        

    '''BFS to find a path.'''
    def bfs(self, start, goal):
        visited = set([])
        queue = [(start, [start])]
        while queue:
            node, path = queue.pop(0)
            visited.add(node)
            for neighbour in self.nodes[node] - set(path):
                if neighbour in self.obs_list:
                    continue
                if neighbour == goal:
                    return path + [neighbour]
                else:
                    queue.append((neighbour, path + [neighbour]))

    '''Uses BFS to find the number of nodes connected in some way to the hamster.'''
    def connected_nodes(self, start):
        visited = set([])
        queue = [(start, [start])]
        while queue:
            node, path = queue.pop(0)
            node = tuple(node)
            visited.add(node)
            for neighbour in self.nodes[node] - set(path):
                if not neighbour in self.obs_list:
                    queue.append((neighbour, path + [neighbour]))
        return visited

    '''Check if the robot is facing the border of the grid.'''
    def facing_border(self):
        if self.current_direction == 'up' and self.current_location[0] == self.grid_rows - 1:
            return True
        elif self.current_direction == 'right' and self.current_location[1] == self.grid_columns - 1:
            return True
        elif self.current_direction == 'down' and self.current_location[0] == 0:
            return True
        elif self.current_direction == 'left' and self.current_location[1] == 0:
            return True
        else:
            return False

        