import numpy as np
import cv2 as cv

# Create a black image
width = 512
height = 700
img = np.zeros((height, width), np.uint8)
np.random.seed(42)

# Parameters
vanishing_point = (255, -255)
inter_row = 50
nb_of_rows = 11

max_number_plants_per_row = 10

# list containing row positions
rows = []

initial_plant_positions = []
# Draw lines crossing in the vanishing point
for i in range(nb_of_rows):
    cv.line(img, (i * inter_row, height), vanishing_point, 255, 1)
    coordinates = np.where(img != 0)
    row_coordinates = np.array(list(zip(coordinates[1], coordinates[0])))
    rows.append(row_coordinates)
    img = np.zeros((height, width), np.uint8)
    
    # Generate initial positions of the plants
    nb_plants = np.random.randint(1, max_number_plants_per_row)
    random_selection = np.random.choice(height, nb_plants, replace=False)
    initial_plant_positions.append(random_selection)
    #print(initial_plant_positions)
#initial_plant_positions = np.array(initial_plant_positions)

# Adding lines (if needed)
img = np.zeros((height, width), np.uint8)
for i in range(nb_of_rows):
    cv.line(img, (i * inter_row, height), vanishing_point, 255, 1)   
    
# cv.imshow("Crop rows", img)
# k = cv.waitKey(0)

# Idea: move plants down across rows to create an image sequence
nb_plants_per_row = []
# find highest plant across all rows
highest_plant = np.min(sum([list(sublist) for sublist in initial_plant_positions], []))
for move_distance in range(0, height-1, 10):
    # Continue generating new images until the highest put plant is not below the bottom third of the image
    if highest_plant + move_distance > height/3 * 2:
        break
    # Draw lines on new image
    img = np.zeros((height, width), np.uint8)
    for i in range(nb_of_rows):
        cv.line(img, (i * inter_row, height), vanishing_point, 255, 1)   
    # Draw plants    
    current_plant_positions = []
    visible_plant_positions = []
    for row_idx in range(len(rows)):
        current_plant_positions = np.asarray(initial_plant_positions[row_idx] + move_distance)
        visible_plant_positions = current_plant_positions[current_plant_positions < height]
        
        plant_positions = rows[row_idx][visible_plant_positions]
        nb_plants = len(plant_positions)
        for center in plant_positions:
            if (center[0] < 0) or (center[1] < 0) or (center[0] > height) or (center[1] > height):
                nb_plants = nb_plants - 1
            else:
                cv.circle(img, center, 7, 255, -1)  # drawing of the plants
        nb_plants_per_row.append(nb_plants)  # adding the nb of plants to the global list
    cv.imshow("Crop rows", img)
    k = cv.waitKey(0)
#print(nb_plants_per_row)

