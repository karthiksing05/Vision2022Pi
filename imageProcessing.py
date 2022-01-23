import math
import numpy as np
import cv2

from params import *

VERSION = cv2.__version__

def _is_circle(con):
    perimeter = cv2.arcLength(con, True)
    area = cv2.contourArea(con)
    if perimeter == 0:
        return False, 0
    circularity = 4 * math.pi * area / (perimeter * perimeter)
    if 0.65 < circularity < 1.2:
        return True, circularity
    print(circularity)
    return False, 0

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
        is_circle, circularity = _is_circle(item)
        if is_circle:
            print(circularity)
            x, y, w, h = cv2.boundingRect(item)
            big_enough = (w > SMALLEST_BALL_WIDTH) and (h > SMALLEST_BALL_HEIGHT)
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
        return _get_color(RED_BOUNDS, frame, 'red', num_items_each)

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
                _, data, coords, output, centers = _get_color(RED_BOUNDS, frame, 'red', num_items_each)
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
