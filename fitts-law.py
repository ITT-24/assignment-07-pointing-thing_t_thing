import pyglet
from pyglet.gl import glClearColor
import argparse
import pandas as pd
import numpy as np
import time

"""
- display fitt's law study setup 
    - different conditions:
        - 3+ target radii
        - 3+ target distances
- log data automatically
- set important paramerters with cmd-line-parameters and config file
    - participant id, num trials
- Option to add latency to pointer

- [ ] (2P) The Fitts’ Law application works
- [ ] (2P) Data is logged correctly
- [ ] (2P) Latency can be added
- [ ] (1P) The application can be parametrized

"""

WIDTH = 500
HEIGHT = 500
window = pyglet.window.Window(WIDTH, HEIGHT, caption="Fitt's Law Test")

COLOR = (207, 207, 207)
MARKED = (255, 0, 0)
NUM_OF_CIRCLES = 7
REPETITIONS = 3

LOGS_FOLDER = "logs"
HEADER = ["id", "trial", "radius", "distance", "mt", "errors", "accuracy"]

# ----- Parameterization ----- #

def parse_cmd_input():
    """Read and parse the command line parameters"""
    config_file = None

    parser = argparse.ArgumentParser( 
        prog="fitt's Law application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="A setup for a fitt's law study, that can be adjusted with parameters",
        epilog="""----- config.csv syntax -----\n
        id,trials,radii,distances,lag\n
        0,3,5 10 50,10 50 100,0
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
    def __init__(self,config_file) -> None:
        df = pd.read_csv(config_file)
        self.parse_file(df)

    def parse_file(self, df):
        # set parameters
        print(df.head())
        self.participant_id = df.at[0, "id"]
        self.num_trials = df.at[0, "trials"]
        rs = df.at[0,"radii"]
        self.target_radii = self.parse_field_to_list(rs)
        ds = df.at[0,"distances"]
        self.target_distances = self.parse_field_to_list(ds)
        self.lag = df.at[0,"lag"]

    def parse_field_to_list(self, field:str)-> list[str]:
        l = field.split(" ")
        return l


# ----- FITT'S LAW EXPERIMENT ----- #

class Experiment():
    def __init__(self, config) -> None:
        c = config
        self.d = c.target_distances # distance between targets 
        self.r = c.target_radii     # width/radius of the target
        self.id = c.participant_id 
        self.num_trials = c.num_trials 
        self.current_trial = 0

    def start_experiment(self):
        self.start_trial(self.current_trial)
        pass

    def start_trial(self, i):
        ts.create_targets(int(self.r[i]), int(self.d[i]))
        ts.mark_targets()

    def next_round(self):
        print("data", ts.data)
        self.save_round()

        ts.clear_targets()

        self.current_trial += 1
        if self.current_trial != self.num_trials:
            self.start_trial(self.current_trial)
        else:
            ts.clear_targets()
            # l = pyglet.text.Label("done :D", x=ts.center[0], y=ts.center[1], batch=ts.batch)
            # ts.targets.append(l)
            # l.draw()
            print("done :D")

    def save_round(self):
        print("saveing the current round")
        filename = f"{LOGS_FOLDER}/{self.id}-{self.current_trial}.csv"
        df = pd.DataFrame(ts.data, columns=HEADER)
        df.to_csv(filename, encoding="utf-8")

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

    def create_targets(self, radius, distance):
        # TODO: only create circles, that are within bounds
        self.data = [] # reset for every round  
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
            self.previous_index = 0 # reset if end is reached

        if self.first:
            self.marked = self.targets[self.previous_index]
            self.first = False
        else: # mark opposite
            offset = int(np.ceil(len(self.targets) / 2))
            idx = self.previous_index + offset
            if idx >= len(self.targets):
                # handle as if first
                self.previous_index = 0
                idx = self.previous_index
            else:
                self.previous_index += 1 
                self.first = True
            self.marked = self.targets[idx]
        self.marked.color = MARKED
    """ 
       0 1        0 2
     6     2    5     4
      5 4 3      3 1 6
    """

    def process_click(self, x, y):
        if len(ts.targets) <= 1:
            return
        
        hit, distance = self.check_collision(x, y)
        if hit:
            self.mark_targets()

            if self.first:
                self.start = time.time()
            else:
                self.end = time.time()
                mt = self.end - self.start
                self.process_data(mt, distance)

            self.error_counter = 0

        else: 
            self.error_counter += 1

        self.hit_counter += 1
        if self.hit_counter == REPETITIONS * 2:
            ex.next_round()
            self.hit_counter = 0

    def measure_distance(self, x1, y1, x2, y2):
        """via: pyglet_click.py AS-demo"""
        distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return distance

    def check_collision(self, x, y)-> tuple[bool, int]:
        """Check if the enemies collied with the hand or with the window border"""
        distance = self.measure_distance(self.marked.x, self.marked.y, x, y)
        if distance < self.current_radius:
            return (True, distance)
        return (False, distance)

    def process_data(self, mt, acc):
        """Create a row of data to, that will later create a dataframe of the full round"""
        trial = ex.current_trial
        r = int(ex.r[trial])
        d = int(ex.d[trial])
        data = [int(ex.id), ex.current_trial, r, d, mt, self.error_counter, float(acc)]
        self.data.append(data)
# header = ["id", "trial", "radius", "distance", "mt", "errors", "accuracy"]


# ----- WINDOW INTERACTION ----- #

glClearColor(255, 255, 255, 1.0)
@window.event
def on_draw():
    window.clear()
    ts.batch.draw()

@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.ESCAPE:
        window.close()
    if symbol == pyglet.window.key.Q:
        window.close()

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == pyglet.window.mouse.LEFT:
        # only check collision, if trial is running
        ts.process_click(x, y)

# ----- INIT ----- #

config = Config(parse_cmd_input())
ex = Experiment(config)
ts = Targets()

# ----- RUN APP ----- #

if __name__ == "__main__":
    ex.start_experiment()
    pyglet.app.run()


"""
@window.event
def on_mouse_release(x, y, button, modifiers):
    if button == pyglet.window.mouse.LEFT:
        pass


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if buttons & pyglet.window.mouse.LEFT:
        pass
"""