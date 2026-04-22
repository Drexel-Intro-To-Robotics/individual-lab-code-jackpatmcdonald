import sys
from PIL import Image
import copy
import queue
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


'''
---------------Personal Notes---------------------
How to run)
1. cd /workspaces/MEM571/searching_map_HW/maps/
2. python3 /workspaces/MEM571/searching_map_HW/read_map.py trivial.gif
-------------------------------------------------------
'''

'''
These variables are determined at runtime and should not be changed or mutated by you
'''
start = (0, 0)  # a single (x,y) tuple, representing the start position of the search algorithm
end = (0, 0)  # a single (x,y) tuple, representing the end position of the search algorithm
difficulty = ""  # a string reference to the original import file
G = 0
E = 0
e_list = []
'''
These variables determine display coler, and can be changed by you, I guess
'''
NEON_GREEN = (0, 255, 0)
PURPLE = (85, 26, 139)
LIGHT_GRAY = (50, 50, 50)
DARK_GRAY = (100, 100, 100)

'''
These variables are determined and filled algorithmically, and are expected (and required) be mutated by you
'''
path = []  # an ordered list of (x,y) tuples, representing the path to traverse from start-->goal
expanded = {}  # a dictionary of (x,y) tuples, representing nodes that have been expanded
frontier = {}  # a dictionary of (x,y) tuples, representing nodes to expand to in the future

open = queue.PriorityQueue()
came_from = {}
cost_so_far = {}

def search(map):
    """
    This function is meant to use the global variables [start, end, path, expanded, frontier] to search through the
    provided map.
    :param map: A '1-concept' PIL PixelAccess object to be searched. (basically a 2d boolean array)
    """
    # Get image dimensions
    im_dims = Image.open(difficulty)
    width, height = im_dims.size
    im_dims.close()

    # Confirmation of start and end
    print("Starting at : {}".format(start))
    print("Goal : {}".format(end))

    # Main Dijkstra loop
    while not open.empty():
        # go to node with lowest known cost
        current_cost, current_node = open.get()

        # check if we've gotten to this node at a cheaper cost
        if current_node in expanded:
            continue

        # Mark the node as expanded (visited)
        expanded[current_node] = current_cost

        # Remove node from frontier since its been visited
        if current_node in frontier:
            del frontier[current_node]
        
        # Check if goal has been reached
        if current_node == end:
            node = end
            while node is not None:
                path.append(node)
                node = came_from.get(node)
            path.reverse()
            print("The maze has been solved!")
            print("Path Cost: {}".format(current_cost))
            print("Length of path: {}".format(len(path)))
            return 
        
        # Expand nearby steps
        for step in next_steps(current_node, map, width, height):
            # Set cost to 1
            new_cost = cost_so_far[current_node] + 1

            if step not in cost_so_far or new_cost < cost_so_far[step]:
                cost_so_far[step] = new_cost
                came_from[step] = current_node

                # add to priority queue
                open.put((new_cost, step))
                # track in frontier
                frontier[step] = new_cost

    # sanity check if goal wasnt reached
    print("No path found from {} to {}".format(start, end))
    pass

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


def visualize_search(save_file="do_not_save.png"):
    """
    :param save_file: (optional) filename to save image to (no filename given means no save file)
    """
    im = Image.open(difficulty).convert("RGB")
    pixel_access = im.load()

    # draw start and end pixels
    pixel_access[start[0], start[1]] = NEON_GREEN
    pixel_access[end[0], end[1]] = NEON_GREEN

    # draw path pixels
    for pixel in path:
        pixel_access[pixel[0], pixel[1]] = PURPLE

    # draw frontier pixels
    for pixel in frontier.keys():
        pixel_access[pixel[0], pixel[1]] = LIGHT_GRAY

    # draw expanded pixels
    for pixel in expanded.keys():
        pixel_access[pixel[0], pixel[1]] = DARK_GRAY

    # display and (maybe) save results
    # im.show()
    # if (save_file != "do_not_save.png"):
    #     im.save(save_file)
    im.save("solved_maze.png")
    im.close()

if __name__ == "__main__":
    # Throw Errors && Such
    # global difficulty, start, end
    # assert sys.version_info[0] == 2  # require python 2 (instead of python 3)
    # assert len(sys.argv) == 2, "Incorrect Number of arguments"  # require difficulty input

    # Parse input arguments
    function_name = str(sys.argv[0])
    difficulty = str(sys.argv[1])
    print("================ Running " + function_name + " with " + difficulty + " difficulty.==================")

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
    G = 1000000000000000000
    E = 1000000000000000000
    open.put((0, start))
    came_from[start] = None
    cost_so_far[start] = 0
    # Perform search on given image
    im = Image.open(difficulty)
    im = im.convert('1')
    search(im.load())
    visualize_search("solved_maze.png")