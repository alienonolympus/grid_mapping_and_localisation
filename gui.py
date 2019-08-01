'''File containing the class controlling the GUI'''
import Tkinter as tk
from threading import Thread
from Queue import Queue
from time import sleep

'''
GUI object that uses Tkinter to display information from the robot\'s sensors.
Additionally, the GUI acts as the main thread and the wrapper to connect the other objects.
'''
class GUI(object):
    '''
    Initialises GUI.
    Takes canvas_size (tuple containing width and height) as the first argument.
    Takes the robot_handler as the second argument.
    '''
    def __init__(self, robot_handler, grid):
        # Initialise variables
        self.root = tk.Tk()
        self.canvas_width, self.canvas_height = grid.canvas_width, grid.canvas_height
        self.canvas = tk.Canvas(self.root, width = self.canvas_width, height = self.canvas_height)
        self.graph = grid
        self.robot = robot_handler
        self.nodes = {}
        self.current_location_marker = None

        # Initialise buttons
        self.frame = tk.Frame(self.root)
        self.map_btn = tk.Button(self.frame, text = 'Map')
        self.map_btn.bind('<Button-1>', self.map)
        self.localise_btn = tk.Button(self.frame, text = 'Localise')
        self.localise_btn.bind('<Button-1>', self.localise)
        self.return_btn = tk.Button(self.frame, text = 'Return')
        self.return_btn.bind('<Button-1>', self.return_to_start)
        self.stop_btn = tk.Button(self.frame, text = 'Stop')
        self.stop_btn.bind('<Button-1>', self.stop)
        self.map_btn.pack(side = 'left')
        self.localise_btn.pack(side = 'left')
        self.return_btn.pack(side = 'left')
        self.stop_btn.pack(side = 'left')

        # Initialise threads
        self.main_thread = Thread(target = self.main)
        self.main_thread.daemon = True
        self.mapping_thread = None
        self.localising_thread = None
        self.returning_thread = None
        self.display_thread = Thread(target = self.update_graph)
        self.display_thread.daemon = True

    '''Starts the Tkinter process.'''
    def start(self):
        self.canvas.pack()
        self.frame.pack()
        self.main_thread.start()
        self.root.mainloop()
    
    '''Main process.'''
    def main(self):
        self.graph.set_grid_rows(5)
        self.graph.set_grid_cols(5)
        self.graph.set_start((self.graph.grid_rows / 2, self.graph.grid_columns / 2))
        self.graph.make_grid()
        self.graph.compute_node_locations()
        self.display_graph()
        self.display_thread.start()

    '''Start mapping the surrounding environment.'''
    def map(self, event = None):
        if not self.graph.mapping:
            self.graph.mapping = True
            self.mapping_thread = Thread(target = self.graph.map, args=(self.robot,))
            self.mapping_thread.daemon = True
            self.mapping_thread.start()

    '''Start localisation.'''
    def localise(self, event = None):
        if not self.graph.localising:
            self.graph.localising = True
            self.localising_thread = Thread(target = self.graph.localise, args=(self.robot,))
            self.localising_thread.daemon = True
            self.localising_thread.start()

    '''Start returning to start position.'''
    def return_to_start(self, event = None):
        if not self.graph.returning:
            self.graph.returning = True
            self.returning_thread = Thread(target = self.graph.return_to_start, args=(self.robot,))
            self.returning_thread.daemon = True
            self.returning_thread.start()

    '''Stop every single process.'''
    def stop(self, event = None):
        try:
            self.graph.mapping = False
            self.mapping_thread.join()
            self.graph.localising = False
            self.localising_thread.join()
            self.graph.returning = False
            self.returning_thread.join()
        except RuntimeError:
            pass
        except AttributeError:
            pass

    '''Update the graph with the current obstacle list.'''
    def update_graph(self):
        while True:
            for node in self.graph.nodes:
                if node == self.graph.start_node:
                    self.canvas.itemconfig(self.nodes[node], fill = '#f00')
                elif node in self.graph.obs_list:
                    self.canvas.itemconfig(self.nodes[node], fill = '#0f0')
                else:
                    self.canvas.itemconfig(self.nodes[node], fill = '#00f')
                if node == self.graph.current_location:
                    self.canvas.coords(self.current_location_marker, self.graph.node_display_locations[node][0], self.graph.node_display_locations[node][1])
                    self.canvas.itemconfig(self.current_location_marker, text = {
                        'up': '^',
                        'right': '>',
                        'left': '<',
                        'down': 'v'
                    }[self.graph.current_direction])
            sleep(0.1)

    '''Display the graph on the Tkinter canvas.'''
    def display_graph(self):        
        for node in self.graph.nodes:
            for neighbour in self.graph.nodes[node]:
                self.canvas.create_line(self.graph.node_display_locations[node][0], self.graph.node_display_locations[node][1], self.graph.node_display_locations[neighbour][0], self.graph.node_display_locations[neighbour][1], width = 2)
        for node in self.graph.nodes:
            x_top_left = int(self.graph.node_display_locations[node][0] - 0.5 * self.graph.column_width)
            y_top_left = int(self.graph.node_display_locations[node][1] - 0.5 * self.graph.row_height)
            x_bottom_right = int(self.graph.node_display_locations[node][0] + 0.5 * self.graph.column_width)
            y_bottom_right = int(self.graph.node_display_locations[node][1] + 0.5 * self.graph.row_height)
            if node == self.graph.start_node:
                self.nodes[node] = self.canvas.create_oval(x_top_left, y_top_left, x_bottom_right, y_bottom_right, outline = '#000', fill = '#f00', width = 2)
            elif node in self.graph.obs_list:
                self.nodes[node] = self.canvas.create_oval(x_top_left, y_top_left, x_bottom_right, y_bottom_right, outline = '#000', fill = '#0f0', width = 2)
            else:
                self.nodes[node] = self.canvas.create_oval(x_top_left, y_top_left, x_bottom_right, y_bottom_right, outline = '#000', fill = '#00f', width = 2)
        self.current_location_marker = self.canvas.create_text(self.graph.node_display_locations[self.graph.start_node][0], self.graph.node_display_locations[self.graph.start_node][1], text = '^', fill = '#fff', font = ('Arial', 30))
    
    '''Highlight the graph based on the path.'''
    def highlight_path(self, path):
        for node in path:
            if not node == self.graph.start_node and not node == self.graph.goal_node:
                self.canvas.itemconfig(self.nodes[node], fill = '#ff0')

