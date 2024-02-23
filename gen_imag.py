import numpy as np
import cv2 as cv

# Create a black image
img = np.zeros((512, 512), np.uint8)

# Parameters
vanishing_point = (255, -255)
inter_row = 50
nb_of_rows = 11

max_number_plants_per_row = 10

# list containing row positions
row_positions = []

# Draw lines crossing in the vanishing point
for i in range(nb_of_rows):
    cv.line(img, (i * inter_row, 512), vanishing_point, 255, 1)

    coordinates = np.where(img != 0)
    row_coordinates = np.array(list(zip(coordinates[1], coordinates[0])))
    row_positions.append(row_coordinates)
    img = np.zeros((512, 512), np.uint8)  # removing the lines

# Adding lines (if needed)
img = np.zeros((512, 512), np.uint8)
for i in range(nb_of_rows):
    cv.line(img, (i * inter_row, 512), vanishing_point, 255, 1)

# list containing nb plants per row
nb_plants_per_row = []

# image sequence : we need to know how many plants are on the image at the moment
# move up plant to down plant to create an image sequence

for row in row_positions:
    nb_plants = np.random.randint(1, max_number_plants_per_row)  # nb of plants in the row
    # randmoly choosed coordinates
    # from the list of coordinates of the row
    random_selection = np.random.choice(len(row), nb_plants, replace=False)
    plant_positions = row[random_selection]  # coordinates of plants in the row
    # img = np.zeros((512, 512), np.uint8)
    for center in plant_positions:
        if (center[0] < 0) or (center[1] < 0) or (center[0] > 512) or (center[1] > 512):
            nb_plants = nb_plants - 1
        else:
            cv.circle(img, center, 7, 255, -1)  # drawing of the plants
    nb_plants_per_row.append(nb_plants)  # adding the nb of plants to the global list

print(nb_plants_per_row)

# Showing the images
cv.imshow("Crop rows", img)
k = cv.waitKey(0)
