SMALLEST_BALL_WIDTH = 10
SMALLEST_BALL_HEIGHT = 10

SMALLEST_GOAL_WIDTH = 40
SMALLEST_GOAL_HEIGHT = 40

LARGEST_WIDTH = 180 # Not implemented yet
LARGEST_HEIGHT = 180 # Not implemented yet

BLUE_BOUNDS = ([90, 170, 0], [120, 255, 255])
BLACK_BOUNDS = ([0, 0, 0], [179, 255, 40])
GREEN_BOUNDS = ([75, 20, 20], [90, 255, 255]) # TODO figure out best bounds for this
RED_LOWER_BOUNDS = [0, 170, 75], [10, 255, 255]
RED_UPPER_BOUNDS = [140, 170, 75], [179, 255, 255]

BOUNDARY_COLOR = (255, 255, 255)
CROSSHAIR_COLOR = (255, 255, 255)

CAMERA_FOCAL_LENGTH = 10 # mm # maximum of 20 mm but minimum of 10 mm
REAL_DIMS = (120, 120, 91.875) # cm

FLANN_INDEX_KDTREE = 1

SEND_MODE = 'print'