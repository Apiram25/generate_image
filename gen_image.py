import numpy as np
import cv2 as cv

np.random.seed(44)

# Parameters
height = 700
width = 512
vp_height = -500
vanishing_point = (255, vp_height)
inter_row_distance = 80

nb_of_plants_rows = 7
max_number_plants_per_row = 15
nb_plant_types = 4

img = np.zeros((height, width), np.uint8)

plants_rows = []
initial_plant_positions = []
plant_types = []
for i in range(nb_of_plants_rows):
    # Get position of lines crossing in the vanishing point
    cv.line(img, (i * inter_row_distance, height), vanishing_point, 255, 1)
    coordinates = np.where(img != 0)
    row_coordinates = np.array(list(zip(coordinates[1], coordinates[0])))
    plants_rows.append(row_coordinates)
    img = np.zeros((height, width), np.uint8)
    
    # Generate initial positions of the plants
    nb_plants = np.random.randint(1, max_number_plants_per_row)
    random_selection = np.random.choice(np.arange(vp_height, height, 50), nb_plants, replace=False)
    initial_plant_positions.append(random_selection)
    plant_markers = np.random.choice(nb_plant_types, nb_plants)
    plant_types.append(plant_markers)
    

nb_of_weeds_rows = 56
inter_row_weeds_distance = 10
max_number_weeds_per_row = 2

weeds_rows = []
initial_weeds_positions = []
weeds_types = []
for i in range(nb_of_weeds_rows):
    cv.line(img, (i * inter_row_weeds_distance, height), vanishing_point, 255, 1)
    weeds_coordinates = np.where(img != 0)
    weeds_row_coordinates = np.array(list(zip(weeds_coordinates[1], weeds_coordinates[0])))
    weeds_rows.append(weeds_row_coordinates)
    img = np.zeros((height, width), np.uint8)
    
    # Generate initial positions of the weeds
    nb_weeds = np.random.randint(1, max_number_weeds_per_row)
    random_selection = np.random.choice(np.arange(vp_height, height, 30), nb_weeds, replace=False)
    initial_weeds_positions.append(random_selection)
    weeds_markers = np.random.choice(nb_plant_types, nb_weeds)
    weeds_types.append(weeds_markers)
   
# Idea: move plants down across rows to create an image sequence
# Find highest plant across all rows
highest_plant = np.min(sum([list(sublist) for sublist in initial_plant_positions], []))
for move_distance in range(0, -1 * vp_height + height-1, 10):
    # Stop generating images when the last plant is below the bottom third of the image
    if (highest_plant + move_distance) > height/3 * 2:
        break
    
    img = np.zeros((height, width), np.uint8)
    # Draw lines of plants rows
    # for i in range(nb_of_plants_rows):
    #     cv.line(img, (i * inter_row_distance, height), vanishing_point, 255, 1)   
        
    # Draw plants    
    nb_plants_per_row = []
    current_plant_positions = []
    visible_plant_positions = []
    for row_idx in range(nb_of_plants_rows):
        current_plant_positions = np.asarray(initial_plant_positions[row_idx] + move_distance)
        current_row_plant_types = plant_types[row_idx][current_plant_positions < height]
        visible_plant_positions = current_plant_positions[current_plant_positions < height]
        plant_positions = plants_rows[row_idx][visible_plant_positions]
        nb_visible_plants = len(plant_positions)
        for i, center in enumerate(plant_positions):
            if (center[0] < 0) or (center[1] < 0) or (center[0] > width) or (center[1] > height):
                nb_visible_plants = nb_visible_plants - 1
            else:
                perspective_coef = center[1]/height
                if current_row_plant_types[i] == 0:
                    cv.circle(img, center, int(20 * perspective_coef), 255, -1)
                elif current_row_plant_types[i] == 1:
                    cv.drawMarker(img,center,255,markerType = cv.MARKER_CROSS,markerSize = int(50 * perspective_coef),thickness = 5)
                elif current_row_plant_types[i] == 2:
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
        row_last_point = weeds_rows[row_idx][-1][1]
        current_row_weeds_types = weeds_types[row_idx][(current_weeds_positions >= 0) & (current_weeds_positions <= row_last_point)]
        visible_weeds_positions = current_weeds_positions[(current_weeds_positions >= 0) & (current_weeds_positions <= row_last_point)] 
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

