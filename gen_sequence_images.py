import numpy as np
import cv2 as cv

np.random.seed(44)

# Image parameters
height = 700
width = 500

# Parameters to generate image and to be tracked
inter_row_distance = 80
inter_plant_distance = 110
offset = 0  # between -(width/2) and +(width/2)
skew = 0  # TODO
convergence = 0  # TODO

# Field parameters
vp_height = -500   
vp_width = 250 + offset
vanishing_point = (vp_width, vp_height)
distance = np.absolute(height - vp_height) 

# Plants generation parameters
nb_of_plants_rows = 7
max_number_plants_per_row = distance / inter_plant_distance  # modified
nb_plant_types = 4

img = np.zeros((height, width), np.uint8)

plants_rows = []
initial_plant_positions = []
plant_types = []
for i in range(nb_of_plants_rows):
    # Get position of lines crossing in the vanishing point
    cv.line(img, (i * inter_row_distance + offset, height), vanishing_point, 255, 1)
    coordinates = np.where(img != 0)
    row_coordinates = np.array(list(zip(coordinates[1], coordinates[0])))
    plants_rows.append(row_coordinates)
    img = np.zeros((height, width), np.uint8)
    
    # Generate initial positions of the plants 
    nb_plants = np.random.randint(1, max_number_plants_per_row)
    # Modified for the particle filter
    random_selection = np.random.choice(np.arange(vp_height, height, inter_plant_distance), nb_plants, replace=False)  
    initial_plant_positions.append(random_selection)
    plant_markers = np.random.choice(nb_plant_types, nb_plants)
    plant_types.append(plant_markers)
    
# Weeds generation parameters
nb_of_weeds_rows = 56
inter_row_weeds_distance = 10
max_number_weeds_per_row = 2

weeds_rows = []
initial_weeds_positions = []
weeds_types = []
for i in range(nb_of_weeds_rows):
    cv.line(img, (i * inter_row_weeds_distance + offset, height), vanishing_point, 255, 1)
    weeds_coordinates = np.where(img != 0)
    weeds_row_coordinates = np.array(list(zip(weeds_coordinates[1], weeds_coordinates[0])))
    weeds_rows.append(weeds_row_coordinates)
    img = np.zeros((height, width), np.uint8)
    
    # Generate initial positions of the weeds
    nb_weeds = np.random.randint(0, max_number_weeds_per_row)
    random_selection = np.random.choice(np.arange(vp_height, height, 30), nb_weeds, replace=False)
    initial_weeds_positions.append(random_selection)
    weeds_markers = np.random.choice(nb_plant_types, nb_weeds)
    weeds_types.append(weeds_markers)
   
# Idea: move plants down across rows to create an image sequence
# Find highest plant across all rows
highest_plant = np.min(sum([list(sublist) for sublist in initial_plant_positions], []))
for move_distance in range(0, -1 * vp_height + height-1, 10):
    print("Move distance : {}".format(move_distance))

    # Stop generating images when the last plant is below the bottom third of the image
    if (highest_plant + move_distance) > height/3 * 2:
        break
    
    img = np.zeros((height, width), np.uint8)
    
    # Draw lines of plants rows
    for i in range(nb_of_plants_rows):
        cv.line(img, (i * inter_row_distance + offset, height), vanishing_point, 255, 1)   
        
    # Draw plants    
    nb_plants_per_row = []
    current_plants_positions = []
    visible_plants_positions = []
    for row_idx in range(nb_of_plants_rows):
        current_plants_positions = np.asarray(initial_plant_positions[row_idx] + move_distance)
        last_point_of_row = plants_rows[row_idx][-1][1]
        current_row_plants_types = plant_types[row_idx][(current_plants_positions >= 0) & (current_plants_positions <= last_point_of_row)]
        visible_plants_positions = current_plants_positions[(current_plants_positions >= 0) & (current_plants_positions <= last_point_of_row)] 
        print("Visible plant positions : {}".format(visible_plants_positions))
        plant_positions = plants_rows[row_idx][visible_plants_positions]
        nb_visible_plants = len(plant_positions)

        # The tracked plant's height
        if (row_idx == np.floor(nb_of_plants_rows/2)): 
            print(np.max(visible_plants_positions))


        for i, center in enumerate(plant_positions):
            if (center[0] < 0) or (center[1] < 0) or (center[0] > width) or (center[1] > height):
                nb_visible_plants = nb_visible_plants - 1
            else:
                perspective_coef = center[1]/height
                if current_row_plants_types[i] == 0:
                    cv.circle(img, center, int(20 * perspective_coef), 255, -1)
                elif current_row_plants_types[i] == 1:
                    cv.drawMarker(img,center,255,markerType = cv.MARKER_CROSS,markerSize = int(50 * perspective_coef),thickness = 5)
                elif current_row_plants_types[i] == 2:
                    cv.drawMarker(img,center,255,markerType = cv.MARKER_TILTED_CROSS,markerSize = int(50 * perspective_coef),thickness = 5)
                else:
                    cv.drawMarker(img,center,255,markerType = cv.MARKER_STAR,markerSize = int(50 * perspective_coef),thickness = 5)
        nb_plants_per_row.append(nb_visible_plants) 
    #print(nb_plants_per_row)
    
    # Draw weeds    
    nb_weeds_per_row = []
    current_weeds_positions = []
    visible_weeds_positions = []
    for row_idx in range(nb_of_weeds_rows):
        current_weeds_positions = np.asarray(initial_weeds_positions[row_idx] + move_distance)
        last_point_of_row = weeds_rows[row_idx][-1][1]
        current_row_weeds_types = weeds_types[row_idx][(current_weeds_positions >= 0) & (current_weeds_positions <= last_point_of_row)]
        visible_weeds_positions = current_weeds_positions[(current_weeds_positions >= 0) & (current_weeds_positions <= last_point_of_row)] 
        weeds_positions = weeds_rows[row_idx][visible_weeds_positions]
        nb_visible_weeds = len(weeds_positions)
        for i, center in enumerate(weeds_positions):
            if (center[0] < 0) or (center[1] < 0) or (center[0] > width) or (center[1] > height):
                nb_visible_weeds = nb_visible_weeds - 1
            else:
                perspective_coef = center[1]/height
                if current_row_weeds_types[i] == 0:
                    cv.circle(img, center, int(5 * perspective_coef), 255, -1)
                elif current_row_weeds_types[i] == 1:
                    cv.drawMarker(img,center,255,markerType = cv.MARKER_CROSS,markerSize = int(10 * perspective_coef),thickness = 5)
                elif current_row_weeds_types[i] == 2:
                    cv.drawMarker(img,center,255,markerType = cv.MARKER_TILTED_CROSS,markerSize = int(10 * perspective_coef),thickness = 5)
                else:
                    cv.drawMarker(img,center,255,markerType = cv.MARKER_STAR,markerSize = int(10 * perspective_coef),thickness = 5)
        nb_weeds_per_row.append(nb_visible_weeds) 
    #print(nb_weeds_per_row)
    
    cv.imshow("Crop rows", img)
    k = cv.waitKey(0)

