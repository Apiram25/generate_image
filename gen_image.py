import numpy as np
import cv2 as cv

np.random.seed(45)

# Parameters
height = 700
width = 512
vp_height = -500
vanishing_point = (255, vp_height)
inter_row_distance = 80
nb_of_rows = 7
max_number_plants_per_row = 15
nb_plant_types = 4

img = np.zeros((height, width), np.uint8)

# Get position of lines crossing in the vanishing point
rows = []
initial_plant_positions = []
plant_types = []
for i in range(nb_of_rows):
    cv.line(img, (i * inter_row_distance, height), vanishing_point, 255, 1)
    coordinates = np.where(img != 0)
    row_coordinates = np.array(list(zip(coordinates[1], coordinates[0])))
    rows.append(row_coordinates)
    img = np.zeros((height, width), np.uint8)
    
    # Generate initial positions of the plants
    nb_plants = np.random.randint(1, max_number_plants_per_row)
    random_selection = np.random.choice(np.arange(vp_height, height, 50), nb_plants, replace=False)
    initial_plant_positions.append(random_selection)
    markers = np.random.choice(nb_plant_types, nb_plants)
    plant_types.append(markers)
   
# Idea: move plants down across rows to create an image sequence
# Find highest plant across all rows
highest_plant = np.min(sum([list(sublist) for sublist in initial_plant_positions], []))
for move_distance in range(0, -1 * vp_height + height-1, 10):
    # Stop generating images when the last plant is below the bottom third of the image
    if (highest_plant + move_distance) > height/3 * 2:
        break
    # Draw lines of rows
    img = np.zeros((height, width), np.uint8)
    for i in range(nb_of_rows):
        cv.line(img, (i * inter_row_distance, height), vanishing_point, 255, 1)   
    # Draw plants    
    nb_plants_per_row = []
    current_plant_positions = []
    visible_plant_positions = []
    for row_idx in range(len(rows)):
        current_plant_positions = np.asarray(initial_plant_positions[row_idx] + move_distance)
        current_row_plant_types = plant_types[row_idx][current_plant_positions < height]
        visible_plant_positions = current_plant_positions[current_plant_positions < height] 
        plant_positions = rows[row_idx][visible_plant_positions]
        nb_plants = len(plant_positions)
        for i, center in enumerate(plant_positions):
            if (center[0] < 0) or (center[1] < 0) or (center[0] > width) or (center[1] > height):
                nb_plants = nb_plants - 1
            else:
                if current_row_plant_types[i] == 0:
                    cv.circle(img, center, 12, 255, -1)
                elif current_row_plant_types[i] == 1:
                    cv.drawMarker(img,center,255,markerType = cv.MARKER_CROSS,markerSize = 35,thickness = 5)
                elif current_row_plant_types[i] == 2:
                    cv.drawMarker(img,center,255,markerType = cv.MARKER_TILTED_CROSS,markerSize = 35,thickness = 5)
                else:
                    cv.drawMarker(img,center,255,markerType = cv.MARKER_STAR,markerSize = 35,thickness = 5)
        nb_plants_per_row.append(nb_plants) 
    #print(nb_plants_per_row)
    cv.imshow("Crop rows", img)
    k = cv.waitKey(0)

