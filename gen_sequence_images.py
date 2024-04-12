import numpy as np
import cv2 as cv

# Visualizer draws plants and particles at the same time
class Visualizer():
    def __init__(self, plants, particles):
        self.plants = plants
        self.particles = particles

    def draw_plants(self, move_distance):
        pass

    def draw_particles(self):
        pass

    def draw(self, move_distance):
        self.draw_plants(move_distance)
        self.draw_particles()

        cv.imshow("Crop rows", plants.img)
        k = cv.waitKey(0)

# Weeds needs to be added
class Plants():
    def __init__(self, height, width, vp_height, vp_width, ir, ip, o, s, c, nb_rows, nb_plant_types):
        # Image parameters
        self.height = height
        self.width = width
        self.img = np.zeros((height, width), np.uint8)

        # Parameters to generate image and to be tracked
        self.inter_row_distance = ir
        self.inter_plant_distance = ip
        self.offset = o  # between -(width/2) and +(width/2)
        self.skew = s  # TODO
        self.convergence = c  # TODO

        # Field parameters
        self.vp_height = vp_height
        self.vp_width = vp_width + self.offset
        self.vanishing_point = (vp_width, vp_height)
        self.vp_distance = np.absolute(height - vp_height)

        # Plants generation parameters
        self.nb_of_plants_rows = nb_rows
        self.max_number_plants_per_row = np.ceil(self.vp_distance / self.inter_plant_distance)  # modified
        self.nb_plant_types = nb_plant_types

        # Particular plants' height
        self.highest_plant = -1
        self.tracked_plant = -1

        #
        self.initial_plant_positions = []
        self.plants_rows = []
        self.plant_types = []

    def generate_plants(self):
        for i in range(self.nb_of_plants_rows):
            # Get position of lines crossing in the vanishing point
            cv.line(self.img, (i * self.inter_row_distance + self.offset, self.height), self.vanishing_point, 255, 1)
            coordinates = np.where(self.img != 0)
            row_coordinates = np.array(list(zip(coordinates[1], coordinates[0])))
            self.plants_rows.append(row_coordinates)
            self.img = np.zeros((self.height, self.width), np.uint8)

            # Generate initial positions of the plants
            nb_plants = np.random.randint(1, self.max_number_plants_per_row)
            print("max number of plants per row : {}".format(self.max_number_plants_per_row))
            print("nb_plants : {}".format(nb_plants))
            # Modified for the particle filter
            random_selection = np.random.choice(np.arange(self.vp_height, self.height, self.inter_plant_distance), nb_plants, replace=False)
            self.initial_plant_positions.append(random_selection)
            plant_markers = np.random.choice(self.nb_plant_types, nb_plants)
            self.plant_types.append(plant_markers)

        # Find highest plant across all rows
        self.highest_plant = np.min(sum([list(sublist) for sublist in self.initial_plant_positions], []))

    def move(self, move_distance):
        # Idea: move plants down across rows to create an image sequence

        # Stop generating images when the last plant is below the bottom third of the image
        if (self.highest_plant + move_distance) > self.height/3 * 2:
            return

        self.img = np.zeros((self.height, self.width), np.uint8)

        # Draw plants
        nb_plants_per_row = []
        current_plants_positions = []
        visible_plants_positions = []
        for row_idx in range(self.nb_of_plants_rows):
            current_plants_positions = np.asarray(self.initial_plant_positions[row_idx] + move_distance)
            last_point_of_row = self.plants_rows[row_idx][-1][1]
            current_row_plants_types = self.plant_types[row_idx][(current_plants_positions >= 0) & (current_plants_positions <= last_point_of_row)]
            visible_plants_positions = current_plants_positions[(current_plants_positions >= 0) & (current_plants_positions <= last_point_of_row)]
            # print("Visible plant positions : {}".format(visible_plants_positions))
            plant_positions = self.plants_rows[row_idx][visible_plants_positions]
            nb_visible_plants = len(plant_positions)

            # The tracked plant's height
            if (row_idx == np.floor(self.nb_of_plants_rows/2)):
                try:
                    self.tracked_plant = np.max(visible_plants_positions)
                except:
                    self.tracked_plant = -1
                    print("The last plant to track has gone")


            for i, center in enumerate(plant_positions):
                if (center[0] < 0) or (center[1] < 0) or (center[0] > self.width) or (center[1] > self.height):
                    nb_visible_plants = nb_visible_plants - 1
                else:
                    perspective_coef = center[1]/self.height
                    if current_row_plants_types[i] == 0:
                        cv.circle(self.img, center, int(20 * perspective_coef), 255, -1)
                    elif current_row_plants_types[i] == 1:
                        cv.drawMarker(self.img,center,255,markerType = cv.MARKER_CROSS,markerSize = int(50 * perspective_coef),thickness = 5)
                    elif current_row_plants_types[i] == 2:
                        cv.drawMarker(self.img,center,255,markerType = cv.MARKER_TILTED_CROSS,markerSize = int(50 * perspective_coef),thickness = 5)
                    else:
                        cv.drawMarker(self.img,center,255,markerType = cv.MARKER_STAR,markerSize = int(50 * perspective_coef),thickness = 5)
            nb_plants_per_row.append(nb_visible_plants)
            #print(nb_plants_per_row)

    def measure(self):
        return self.tracked_plant


# main
plants = Plants(700, 500, -500, 250, 80, 110, o=0, s=0, c=0, nb_rows=7, nb_plant_types=4)
plants.generate_plants()

for move_distance in range(0, -1 * plants.vp_height + plants.height-1, 10):
    plants.move(move_distance)
    print("Tracked plant's height : {}".format(plants.measure()))
    cv.imshow("Crop rows", plants.img)
    k = cv.waitKey(0)
