import sys
from PIL import Image
import copy
import queue
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
import csv


'''
---------------Personal Notes---------------------
How to run)
1. cd /workspaces/MEM571/searching_map_HW/maps/
2. python3 /workspaces/MEM571/searching_map_HW/read_map_a*.py trivial.gif
-------------------------------------------------------
'''

'''These variables are determined at runtime and should not be changed or mutated by you'''
start = (0, 0)  # a single (x,y) tuple, representing the start position of the search algorithm
end = (0, 0)  # a single (x,y) tuple, representing the end position of the search algorithm
difficulty = ""  # a string reference to the original import file
G = 0
E = 0
e_list = []

'''These variables determine display coler, and can be changed by you, I guess'''
NEON_GREEN = (0, 255, 0)
PURPLE = (85, 26, 139)
LIGHT_GRAY = (50, 50, 50)
DARK_GRAY = (100, 100, 100)
# Colors for heuristic functions
YELLOW = (255, 255, 0) # Euclidean
ORANGE = (255, 140, 0) # Manhattan

"""
This function is meant to use the global variables [start, end, path, expanded, frontier] to search through the
provided map.
:param map: A '1-concept' PIL PixelAccess object to be searched. (basically a 2d boolean array)"""
# 
def search(map, heuristic_method):
    '''These variables are determined and filled algorithmically, and are expected (and required) be mutated by you'''
    path = []  # an ordered list of (x,y) tuples, representing the path to traverse from start-->goal
    expanded = {}  # a dictionary of (x,y) tuples, representing nodes that have been expanded
    frontier = {}  # a dictionary of (x,y) tuples, representing nodes to expand to in the future
    open = queue.PriorityQueue()
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    node_counter = 0

    # seed the queue
    open.put((heuristic_method(start,end), 0, start))
    frontier[start] = heuristic_method(start,end)

    # Start timer for comparison
    t0 = time.time()

    # Get image dimensions
    im_dims = Image.open(difficulty)
    width, height = im_dims.size
    im_dims.close()

    # Confirmation of start and end
    print("Starting at : {}".format(start))
    print("Goal : {}".format(end))

    # Main A* Loop
    while not open.empty():
        # pop the node with the lowest f score
        f, g, current_node = open.get()
        node_counter += 1

        # check if we've gotten to this node at a cheaper cost
        if current_node in expanded:
            continue

        # Mark the node as expanded (visited)
        expanded[current_node] = g
        if current_node in frontier:
            del frontier[current_node]
        
        # Check if goal has been reached
        if current_node == end:
            print("The maze has been solved!")
            print("Nodes Visited: {}".format(len(expanded)))
            print("Path Cost: {}".format(g))
            result = backtrace_path(came_from, current_node)
            path.extend(result)
            print("Length of path: {}".format(len(path)))
            break 
        
        # Expand nearby steps
        for step in next_steps(current_node, map, width, height):
            # Set cost to 1
            new_cost = cost_so_far[current_node] + 1

            if step not in cost_so_far or new_cost < cost_so_far[step]:
                cost_so_far[step] = new_cost
                # Use the specified method
                new_f = new_cost + heuristic_method(step, end)
                came_from[step] = current_node
                # add to priority queue
                open.put((new_f, new_cost, step))
                # track in frontier
                frontier[step] = new_f
    # Record time
    time_passed = time.time() - t0
    print("Time Passed: {}".format(time_passed))
    return path, expanded, frontier, time_passed, node_counter

# Function for finding the next step options and their weights
def next_steps(node, map, width, height):
    x, y = node
    steps = []

    # Each direction) right, left, up, down
    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
        nx, ny = x + dx, y + dy

        # Check boundary
        if 0 <= nx < width and 0 <= ny < height:
            if map[nx,ny] != 0:
                steps.append((nx,ny))
    return steps

def backtrace_path(came_from, current):
    # initialize
    backtrace = []
    # loop through the path
    while current is not None:
        backtrace.append(current)
        current = came_from[current]
    # flip it so we have the path
    backtrace.reverse()
    return backtrace

'''Heuristic Functions'''
def euclidean(a,b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def manhattan(a,b):
    return abs(a[0] - b[0]) + abs(a[1]-b[1])

# :param save_file: (optional) filename to save image to (no filename given means no save file)
def visualize_search(expanded, frontier, path, path_color, save_file):
    im = Image.open(difficulty).convert("RGB")
    pixel_access = im.load()

    # draw expanded pixels
    for pixel in expanded.keys():
        pixel_access[pixel[0], pixel[1]] = DARK_GRAY

    # draw frontier pixels
    for pixel in frontier.keys():
        pixel_access[pixel[0], pixel[1]] = LIGHT_GRAY

    # draw path pixels
    for pixel in path:
        pixel_access[pixel[0], pixel[1]] = path_color
    
    # draw start and end pixels
    pixel_access[start[0], start[1]] = NEON_GREEN
    pixel_access[end[0], end[1]] = NEON_GREEN

    # display and (maybe) save results
    im.show()
    im.save(save_file)
    im.close()

def save_data(rows, filename="results.csv"):
    field_names = ["heuristic", "difficulty", "path_length", "Expanded Nodes", "Nodes Explored", "Elapsed Time"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(rows)
    print("Saved Data to CSV")


if __name__ == "__main__":
    # Throw Errors && Such
    # global difficulty, start, end
    # assert sys.version_info[0] == 2  # require python 2 (instead of python 3)
    # assert len(sys.argv) == 2, "Incorrect Number of arguments"  # require difficulty input

    if len(sys.argv) < 2:
        print("Terminal Call Format)python3 read_map_a*.py <difficulty>")
        sys.exit(1)

    # Parse input arguments
    function_name = str(sys.argv[0])
    difficulty = str(sys.argv[1])

    print("================ Running " + function_name + " with " + difficulty + " difficulty. ==================")

    # Hard code start and end positions of search for each difficulty level
    if difficulty == "trivial.gif":
        start = (8, 1)
        end = (20, 1)
    elif difficulty == "medium.gif":
        start = (8, 201)
        end = (110, 1)
    elif difficulty == "hard.gif":
        start = (10, 1)
        end = (401, 220)
    elif difficulty == "very_hard.gif":
        start = (1, 324)
        end = (580, 1)
    elif difficulty == "my_maze.gif":
        start = (0, 0)
        end = (500, 205)
    elif difficulty == "my_maze2.gif":
        start = (0, 0)
        end = (599, 350)
    else:
        assert False, "Incorrect difficulty level provided"
    
    im = Image.open(difficulty).convert("1")
    px = im.load()
    width, height = im.size

    csv_rows = []

    for heuristic_method, name, color, tag in [
        (euclidean, "Euclidean", YELLOW, "euclidean"),
        (manhattan, "Manhattan", ORANGE, "manhattan")]:

        print("Applying {} heuristic...".format(name))

        path, expanded, frontier, elapsed, node_counter = search(px, heuristic_method)
        cost = len(path) - 1 if path else -1

        save_name = "solved_{}_{}.png".format(
            difficulty.replace(".gif", ""), tag)
        
        visualize_search(expanded, frontier, path, color, save_name)

        csv_rows.append({
            "heuristic" : name,
            "difficulty" : difficulty,
            "path_length" : cost,
            "Expanded Nodes" : len(expanded),
            "Nodes Explored" : node_counter,
            "Elapsed Time" : round(elapsed, 2)})
    print()
    save_data(csv_rows, "results.csv")