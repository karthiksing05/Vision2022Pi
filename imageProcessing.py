import numpy as np
import cv2

from params import *

VERSION = cv2.__version__

# These functions are for ball and color tracking
def _get_color(bounds:tuple, frame, color_str:str, num_items:int=3):
    """
    Given a set of bounds and the frame/picture, this function will detect a
    number of items of the color and return a formatted frame for viewing, 
    the coords of each object, and the mask used on top of the frame to detect
    the colored objects.

    NOTE: This is a helper function to be used in the main function (might not
    work in a raw instance, better to call the main function in this file)
    """


    if type(frame) == str:
        frame = cv2.imread(frame)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    image = frame

    lower, upper = bounds

    lower = np.array(lower, dtype="uint8")
    upper = np.array(upper, dtype="uint8")

    mask = cv2.inRange(image, lower, upper)
    output = cv2.bitwise_and(image, image, mask=mask)

    if VERSION[0] == '3':
        _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cont_sorted = list(sorted(contours, key=cv2.contourArea, reverse=True)[:num_items])

    boxes_img = output
    final_img = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
    coords = {}
    for item in cont_sorted:
        x, y, w, h = cv2.boundingRect(item)
        big_enough = (w > SMALLEST_WIDTH) and (h > SMALLEST_HEIGHT)
        small_enough = True
        if big_enough and small_enough:
            coords[(x, y, w, h)] = color_str
            cv2.rectangle(boxes_img, (x, y),(x+w, y+h), BOUNDARY_COLOR, 2)
            cv2.rectangle(final_img, (x, y),(x+w, y+h), BOUNDARY_COLOR, 2)

    final_img, centers = _get_centers(coords, final_img)
    boxes_img, centers = _get_centers(coords, boxes_img)

    formattedFrame = np.hstack([final_img, boxes_img])

    data = []
    coords_items = list(coords.items())
    idx = 0
    for key, val in centers.items():
        entry = {}
        entry["objNumber"] = idx
        entry["center"] = key
        entry["width"] = coords_items[idx][0][3]
        entry["height"] = coords_items[idx][0][2]
        entry["x"] = coords_items[idx][0][0]
        entry["y"] = coords_items[idx][0][1]
        entry["color"] = val
        data.append(entry)
        idx += 1

    return formattedFrame, data, coords, boxes_img, centers

def _get_red(frame, num_items:int=3):
    """
    Because red is a bit special in that it is shown in both the top and 
    bottom of the hue spectrum, it is important to provide two bound
    settings and merge the masks in order to get the best possible object
    detection.
    """

    if type(frame) == str:
        frame = cv2.imread(frame)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    image = frame

    red1Lower, red1Upper = RED_LOWER_BOUNDS
    red2Lower, red2Upper = RED_UPPER_BOUNDS

    red1Lower = np.array(red1Lower, dtype="uint8")
    red1Upper = np.array(red1Upper, dtype="uint8")

    red2Lower = np.array(red2Lower, dtype="uint8")
    red2Upper = np.array(red2Upper, dtype="uint8")

    mask1 = cv2.inRange(image, red1Lower, red1Upper)
    mask2 = cv2.inRange(image, red2Lower, red2Upper)

    mask = mask1 | mask2

    output = cv2.bitwise_and(image, image, mask=mask)

    if VERSION[0] == '3':
        _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cont_sorted = list(sorted(contours, key=cv2.contourArea, reverse=True))
    cont_sorted = cont_sorted[:num_items]

    boxes_img = output
    final_img = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
    coords = {}
    for item in cont_sorted:
        x, y, w, h = cv2.boundingRect(item)
        if (w > SMALLEST_WIDTH) and (h > SMALLEST_HEIGHT):
            coords[(x, y, w, h)] = 'red'
            cv2.rectangle(boxes_img, (x, y),(x+w, y+h), BOUNDARY_COLOR, 2)
            cv2.rectangle(final_img, (x, y),(x+w, y+h), BOUNDARY_COLOR, 2)

    final_img, centers = _get_centers(coords, final_img)
    boxes_img, centers = _get_centers(coords, boxes_img)

    formattedFrame = np.hstack([final_img, boxes_img])

    data = []
    coords_items = list(coords.items())
    idx = 0
    for key, val in centers.items():
        entry = {}
        entry["objNumber"] = idx
        entry["center"] = key
        entry["width"] = coords_items[idx][0][3]
        entry["height"] = coords_items[idx][0][2]
        entry["x"] = coords_items[idx][0][0]
        entry["y"] = coords_items[idx][0][1]
        entry["color"] = val
        data.append(entry)
        idx += 1

    return formattedFrame, data, coords, boxes_img, centers

def _get_centers(coords:dict, frame):
    """
    This function's role is to return the centers of each object 
    and the corresponding colors of each object's centers.
    """

    if type(frame) == str:
        frame = cv2.imread(frame)

    newFrame = frame

    centers = {}
    for coord, color in coords.items():
        x, y, w, h = coord
        center = (int(x + (w / 2)), int(y + (h / 2)))
        centers[center] = color
        cv2.drawMarker(newFrame, center, CROSSHAIR_COLOR, thickness=2)

    return newFrame, centers

def get_colored_objects(frame, color='all', num_items_each:int=-1):
    """
    This function's role is to return a frame with the objects of a given color
    outlined, as well as a list of coordinates of the pixels where the objects 
    can be found and the width and height (in pixels) of each object.

    Params:
    - color:str --> the color of the object(s) you want to detect
        currently supported are: 'blue', 'red', 'black', 'all'
        Color can also be a list of specific colors you want to detect, i.e.
        only blue and black, or red and blue, etc.
    - frame ------> the frame you want to analyze
    - num_items_each:int --> the number of objects you want to detect per color
        if necessary, you can also specify a negative one here to get the
        maximum amount of objects

    Returns:
    - formattedFrame (numpy array) --> This is a frame which you can display, 
    detailing the objects it's detected and their outlines
    - data (list) --> list of all objects
    - coords (dict) --> This is a dictionary of coordinates, color of pixels on the 
    frame you inputted, with each element in the list being a tuple of the (x-coordinate, 
    y-coordinate, width (in pixels), height (in pixels))
    - output (numpy array) --> an image representing the mask of colors detected, 
    with outlines included (bounding boxes)
    - centers (dict) --> a dictionary of all the coordinates of the centers, color
    of each object detected
    """

    if color == 'blue':
        return _get_color(BLUE_BOUNDS, frame, 'blue', num_items_each)

    elif color == 'red':
        return _get_red(frame, num_items_each)

    elif color == 'black':
        return _get_color(BLACK_BOUNDS, frame, 'black', num_items_each)

    else:

        finalImg = frame
        if color == 'all':
            colorList = ['blue', 'red', 'black']
        else:
            colorList = color

        outputs = []

        all_coords = []

        for elem in colorList:

            if elem == 'blue':
                outline = (255, 0, 0)
                _, data, coords, output, centers = _get_color(BLUE_BOUNDS, frame, elem, num_items_each)
            elif elem == 'red':
                outline = (0, 0, 255)
                _, data, coords, output, centers = _get_red(frame, num_items_each)
            elif elem == 'black':
                outline = (0, 0, 0)
                _, data, coords, output, centers = _get_color(BLACK_BOUNDS, frame, elem, num_items_each)

            outputs.append(output)
            all_coords.extend(list(coords.items()))

            for x, y, w, h in coords.keys():
                cv2.rectangle(finalImg, (x, y), (x+w,y+h), outline, 2)
        if color == 'all':
            finalOutput = (outputs[0] | outputs[1] | outputs[2])
        elif len(colorList) == 2:
            finalOutput = (outputs[0] | outputs[1])
        elif len(colorList) == 1:
            finalOutput = outputs[0]

        all_coords = dict(all_coords)

        finalImg, centers = _get_centers(all_coords, finalImg)
        finalOutput, centers = _get_centers(all_coords, finalOutput)

        formattedFrame = np.hstack([finalImg, finalOutput])

        data = []
        coords_items = list(all_coords.items())
        idx = 0
        for key, val in centers.items():
            entry = {}
            entry["objNumber"] = idx
            entry["center"] = key
            entry["width"] = coords_items[idx][0][3]
            entry["height"] = coords_items[idx][0][2]
            entry["x"] = coords_items[idx][0][0]
            entry["y"] = coords_items[idx][0][1]
            entry["color"] = val
            data.append(entry)
            idx += 1

        return formattedFrame, data, coords, finalOutput, centers

# These functions are for shooting the ball at the correct arc
def get_goal_data(frame) -> dict:
    """
    This function uses a limelight OpenCV Clone to get the distance of an 
    object from the camera.

    The function returns a data entry to be sent by the transfer class.

    Params:
    - frame:Any -> the frame you would like to parse for distance.

    Returns:
    - data:dict -> a collection of entries that each contain a series of data points
    """

    data = []
    """
    data entry -> dictionary
    {
        distance: float,
        center: tuple(int, int),
        x_offset: float,
        y_offset: float
    }
    """

    lower = np.array(GREEN_BOUNDS[0], dtype="uint8")
    upper = np.array(GREEN_BOUNDS[1], dtype="uint8")

    # get the mask for green colored things
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(frame, frame, mask=mask)

    if VERSION[0] == '3':
        _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cont_sorted = list(sorted(contours, key=cv2.contourArea, reverse=True))

    coords = []
    for item in cont_sorted:
        x, y, w, h = cv2.boundingRect(item)
        big_enough = (w > SMALLEST_WIDTH) and (h > SMALLEST_HEIGHT)
        small_enough = True
        if big_enough and small_enough:
            coords.append((x, y, w, h))
            cv2.rectangle(output, (x, y),(x+w, y+h), BOUNDARY_COLOR, 2)
            cv2.rectangle(frame, (x, y),(x+w, y+h), BOUNDARY_COLOR, 2)
    
    coords = sorted(coords, key=lambda x: x[0])
    pixel_width = coords[-1][0] - coords[0][0]
    coords = sorted(coords, key=lambda x: x[1])
    pixel_height = coords[-1][1] - coords[0][1]
    tgtCenter = ((pixel_width / 2), (pixel_height / 2))

    real_width = REAL_DIMS[0]

    distance = real_width * PI_CAMERA_FOCAL_LENGTH / pixel_width

    frameCenterCoords = (frame.shape[1], frame.shape[0])

    pixelOffset = ((frameCenterCoords[0] - pixel_width), (frameCenterCoords - pixel_height))

    entry = {
        'distance': distance,
        'center': tgtCenter,
        'x_offset':pixelOffset[0],
        'y_offset':pixelOffset[1]
    }

    data.append(entry)

    return data
