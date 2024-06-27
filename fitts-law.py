import argparse
import numpy as np
import os
import pyglet
import pandas as pd
import threading
import time

from pyglet.gl import glClearColor
from collections import deque

WIDTH = 700
HEIGHT = 700
window = pyglet.window.Window(WIDTH, HEIGHT, caption="Fitt's Law Test")

COLOR = (207, 207, 207)
MARKED = (255, 0, 0)
NUM_OF_CIRCLES = 7
REPETITIONS = 7 # amount of clicks / 2 (gets doubled later on, so always even amount of clicks)

CURSOR_RADIUS = 5
CURSOR_COLOR = (0, 0, 0)

LOGS_FOLDER = "logs"
HEADER = ["id", "trial", "radius", "distance", "latency", "hit", "time", "accuracy", "click_x", "click_y", "target_x", "target_y", "click_time"]

# ----- Parameterization ----- #

def parse_cmd_input():
    """Read and parse the command line parameters"""
    config_file = None

    parser = argparse.ArgumentParser(
        prog="fitt's Law application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="A setup for a fitt's law study, that can be adjusted with parameters",
        epilog="""----- config.csv format -----\n
        id,repetitions,radii,distances,latency,device\n
        0,3,25 15 40,110 30 70,0.15,mouse
        -> radii & distances in px
        -> latency in seconds
        """
    )

    parser.add_argument('-c', '--config', type=str, metavar='',
                        default="config.csv",
                        required=False,
                        action="store",
                        help="""The path to the config file you want to use. 
                        Defaults to the included 'config.csv' in the current folder""")

    args = parser.parse_args()

    if args.config:
        config_file = args.config

    return config_file


class Config:
    """Parses the config file to a readable format"""

    def __init__(self, config_file) -> None:
        df = pd.read_csv(config_file)
        self.parse_file(df)
        self.check_config()

    def parse_file(self, df):
        print(df.head())
        self.participant_id = df.at[0, "id"]
        self.trials = df.at[0, "repetitions"]
        rs = df.at[0, "radii"]
        self.target_radii = self.parse_field_to_list(rs)
        ds = df.at[0, "distances"]
        self.target_distances = self.parse_field_to_list(ds)
        self.lag = df.at[0, "latency"]
        self.device = df.at[0, "device"]

    def parse_field_to_list(self, field: str) -> list[str]:
        l = field.split(" ")
        return l
    
    def check_config(self):
        if len(self.target_distances) != len(self.target_radii):
            print("[Not enough values]:")
            print("radii and distances must have the same amount of values!")
            window.close()
            exit(-1)

# ----- FITT'S LAW EXPERIMENT ----- #

class Experiment():
    def __init__(self, config) -> None:
        c = config
        self.d = c.target_distances  # distance between targets
        self.r = c.target_radii     # width/radius of the target
        self.id = c.participant_id
        self.trials = c.trials
        self.current_trial = 0
        self.condition = 0
        self.lag = c.lag
        self.df = pd.DataFrame(columns=HEADER)
        self.device = c.device

    def start_experiment(self):
        self.start_trial()
        pass

    def start_trial(self):
        if self.condition == len(self.r):
            self.condition = 0 # reset conditions
        i = self.condition
        ts.create_targets(int(self.r[i]), int(self.d[i]))
        ts.mark_targets()

    def next_round(self):
        self.current_trial += 1
        self.condition += 1

        self.save_round()
        ts.clear_targets()

        if self.current_trial != self.trials:
            self.start_trial()
        else: 
            ts.clear_targets()
            window.set_mouse_visible(True) 
            self.end_experiment()
            window.close()

    def end_experiment(self):
        """Checks several failsaves before saving (or discarding) the collected data"""
        if not os.path.isdir(LOGS_FOLDER):
            os.makedirs(LOGS_FOLDER)
            print("creating a new folder for the logs...")

        filename = f"{LOGS_FOLDER}/{self.id}-{self.device}.csv"

        if start_screen.latency_enabled and self.device != "latency": 
            filename = f"{LOGS_FOLDER}/{self.id}-latency.csv"
            self.device = "latency"

        if os.path.isfile(filename): 
            print(f"\nThere already exists a file for this exact experiment condition: {filename}")
            print("Do you want to save your data separately?")
            print("y --> will create a timestamped file.")
            print("n --> will not save the file")
            print("o --> override the current file")
            save_order = input("y/n/o:")

            if save_order == "y":
                filename = f"{LOGS_FOLDER}/{self.id}-{self.device}-{time.time()}.csv"
            elif save_order == "n":
                return
        
        self.df.to_csv(filename, mode="w", encoding="utf-8")
        print("done :D")

    def save_round(self):
        df = pd.DataFrame(ts.data, columns=HEADER)
        if self.df.empty:
            self.df = df
        else:
            self.df = pd.concat([self.df, df], ignore_index=True)


class Targets():
    """Draws and processes targets with different radii around the window center"""

    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.targets = []
        self.center = [WIDTH/2, HEIGHT/2]
        self.angle = (2 * np.pi / NUM_OF_CIRCLES)
        self.marked = None
        self.previous_index = 0
        self.first = True
        self.hit_counter = 0
        self.error_counter = 0
        self.start = 0
        self.end = 0
        self.data = []
        self.timestamp = 0

    def create_targets(self, radius, distance):
        # TODO: only create circles, that are within bounds
        self.data = []  # reset for every round
        self.current_radius = radius
        for i in range(0, NUM_OF_CIRCLES):
            self.add_circle(i, radius, distance)

    def add_circle(self, count, radius, distance):
        """Math see answers to: https://stackoverflow.com/q/5300938"""
        angle = self.angle * count
        x = self.center[0] + (distance * np.cos(angle))
        y = self.center[1] + (distance * np.sin(angle))
        c = pyglet.shapes.Circle(x, y, radius, color=COLOR, batch=self.batch)
        self.targets.append(c)

    def clear_targets(self):
        self.targets = []
        self.marked = None

    def mark_targets(self):
        """Mark targets to click with red. The next target is opposite of the previous"""
        for t in self.targets:
            t.color = COLOR

        if self.previous_index == len(self.targets):
            self.previous_index = 0  # reset if end is reached

        if self.first:
            self.marked = self.targets[self.previous_index]
            self.first = False
        else:  # mark target on the opposite side of the circle
            offset = int(np.ceil(len(self.targets) / 2))
            idx = self.previous_index + offset
            if idx >= len(self.targets):
                # handle as if self.first
                self.previous_index = 0
                idx = self.previous_index
            else:
                self.previous_index += 1
                self.first = True
            self.marked = self.targets[idx]
        self.marked.color = MARKED

        # messure time until click
        self.timestamp = time.time()
    """ 
       0 1        0 2
     6     2 -> 5     4
      5 4 3      3 1 6
    """

    def process_click(self, x, y):
        if len(ts.targets) <= 1:
            return

        click_time = self.timestamp
        t = time.time() - click_time  # end time

        hit, distance = self.check_collision(x, y)

        self.hit_counter += 1
        self.process_data(t, hit, distance, x, y, self.marked.x, self.marked.y, click_time)
        self.mark_targets()

        if self.hit_counter == REPETITIONS:
            ex.next_round()
            self.hit_counter = 0

    def measure_distance(self, x1, y1, x2, y2):
        """via: pyglet_click.py AS-demo"""
        distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return distance

    def check_collision(self, x, y) -> tuple[bool, int]:
        """Check if the cursor collides with the targets"""
        distance = self.measure_distance(self.marked.x, self.marked.y, x, y)
        if distance < self.current_radius:
            return (True, distance)
        return (False, distance)

    def process_data(self, time, hit, acc, m_x, m_y, c_x, c_y, click_time):
        """Create a row of data, that will later create a dataframe of the full experiment"""
        trial = ex.condition
        r = int(ex.r[trial])
        d = int(ex.d[trial])
        if not start_screen.latency_enabled:
            ex.lag = 0
        data = [int(ex.id), trial, r, d, ex.lag,
                hit, time, float(acc), m_x, m_y, c_x, c_y, click_time]
        self.data.append(data)


class Cursor:
    """ A simulated cursor with added latency("lag")
        Latency = time delay between the cause and the effect
    """
    def __init__(self, latency):
        self.batch = pyglet.graphics.Batch()
        self.cursor = pyglet.shapes.Circle(0, 0, CURSOR_RADIUS, color=CURSOR_COLOR, batch=self.batch)
        self.position_queue = deque()
        self.lock = threading.Lock()
        self.latency = latency
        self.latency_enabled = False 

        # Update cursor 60 times per second (necessary for latency)
        pyglet.clock.schedule_interval(self.update_cursor, 1/60)

    def on_move(self, x, y, dx, dy):
        #  program captures all input, starts a thread per event, actually triggers input after delay
        if start_screen.latency_enabled:
            with self.lock:
                self.position_queue.append((x, y, time.time()))
        else:
            self.cursor.x = x
            self.cursor.y = y

    def update_cursor(self, dt):
        if start_screen.latency_enabled:
            current_time = time.time()
            with self.lock:
                while self.position_queue and current_time - self.position_queue[0][2] >= self.latency:
                    x, y, _ = self.position_queue.popleft()
                    self.cursor.x = x
                    self.cursor.y = y

class StartScreen:
    def __init__(self) -> None:
        self.show = True
        self.batch = pyglet.graphics.Batch()
        
        self.message = pyglet.text.Label(
            "Click on the red circle to start!",
            font_name='Times New Roman',
            font_size=20,
            bold=True,
            x=WIDTH//2, y=HEIGHT//1.3,
            anchor_x='center', anchor_y='center',
            batch=self.batch
        )
        self.message.color = (0, 0, 0)
        
        self.start_circle = pyglet.shapes.Circle(
            WIDTH//2, HEIGHT//2, 80,
            color=(255, 0, 0), batch=self.batch
        )
        
        self.latency_box = pyglet.shapes.Rectangle(
            WIDTH//2 - 100, HEIGHT//5, 200, 60, 
            color=(0, 0, 0), batch=self.batch
        )
        self.latency_label = pyglet.text.Label(
            "Add Latency To Cursor",
            font_name='Times New Roman',
            font_size=12,
            bold=True,
            x=WIDTH//2, y=HEIGHT//5 + 30,
            anchor_x='center', anchor_y='center',
            batch=self.batch
        )
        self.latency_label.color = (255, 255, 255, 255)
        self.latency_enabled = False

    def draw(self):
        self.batch.draw()

    def check_click(self, x, y):
        distance = np.sqrt((x - self.start_circle.x)**2 + (y - self.start_circle.y)**2)
        # check if player started (clicked in circle)
        if distance <= self.start_circle.radius:
            self.show = False
        # check if the latency box is clicked
        if (self.latency_box.x <= x <= self.latency_box.x + self.latency_box.width) and \
           (self.latency_box.y <= y <= self.latency_box.y + self.latency_box.height):
            self.latency_enabled = not self.latency_enabled
            if self.latency_enabled:
                self.latency_box.color = (0, 150, 0) 
            else:
                self.latency_box.color = (0, 0, 0) 


# ----- WINDOW INTERACTION ----- #

glClearColor(255, 255, 255, 1.0)

@window.event
def on_draw():
    window.clear()
    if start_screen.show:
        start_screen.draw()
    else:
        ts.batch.draw()
        # hide the mouse if experiment is started with latency
        window.set_mouse_visible(not start_screen.latency_enabled) 
        # Draw cursor only if latency is enabled
        if start_screen.latency_enabled:
            cursor.batch.draw()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.ESCAPE:
        window.close()
    if symbol == pyglet.window.key.Q:
        window.close()


@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == pyglet.window.mouse.LEFT:
        if start_screen.show:
            start_screen.check_click(x, y)
        else:
            ts.process_click(x, y)

@window.event
def on_mouse_motion(x, y, dx, dy):
    cursor.on_move(x, y, dx, dy)

# ----- INIT ----- #

config = Config(parse_cmd_input())
ex = Experiment(config)
ts = Targets()
start_screen = StartScreen()
cursor = Cursor(config.lag)

# ----- RUN APP ----- #

if __name__ == "__main__":
    ex.start_experiment()
    # cursor updates for latency
    pyglet.clock.schedule_interval(cursor.update_cursor, 1/60)
    pyglet.app.run()
