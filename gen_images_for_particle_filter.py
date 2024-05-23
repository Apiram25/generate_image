import numpy as np
import cv2 as cv


class World:
    def __init__(self, width, height, speed):
        self.width = width
        self.height = height
        self.speed = speed


# Visualizer draws plants and particles
class Visualizer:
    def __init__(self, world):
        self.world = world
        self.img = np.zeros((world.height, world.width), np.uint8)

    def draw_plants(self, plants):
        for row_idx in range(plants.nb_rows):
            plant_positions, plant_types = plants.getPlantsToDraw(row_idx)
            # Draw
            for i, center in enumerate(plant_positions):
                if (center[0] < 0) or (center[1] < 0) or (center[0] > self.world.width) or (
                        center[1] > self.world.height):
                    # nb_visible_plants = nb_visible_plants - 1
                    pass
                else:
                    perspective_coef = center[1] / self.world.height
                    if plant_types[i] == 0:
                        cv.circle(self.img, center, int(20 * perspective_coef), (255, 255, 255), -1)
                    elif plant_types[i] == 1:
                        cv.drawMarker(self.img, center, (255, 255, 255), markerType=cv.MARKER_CROSS,
                                      markerSize=int(50 * perspective_coef), thickness=5)
                    elif plant_types[i] == 2:
                        cv.drawMarker(self.img, center, (255, 255, 255), markerType=cv.MARKER_TILTED_CROSS,
                                      markerSize=int(50 * perspective_coef), thickness=5)
                    else:
                        cv.drawMarker(self.img, center, (255, 255, 255), markerType=cv.MARKER_STAR,
                                      markerSize=int(50 * perspective_coef), thickness=5)

    def draw_particles(self, particles, n):
        for i in range(n):
            # Coordinates of the particle
            center = np.asarray([int(self.world.width / 2), int(particles[i][1][0])])

            perspective_coef = center[1] / self.world.height

            # Color of the particle in fonction of the its weight
            if particles[i][0] > 0.70:
                color = (0, 0, 255)
                thickness = 5
            elif particles[i][0] > 0.30:
                color = (255, 0, 0)
                thickness = 4
            else:
                color = (0, 255, 0)
                thickness = 2

            cv.drawMarker(self.img, center, color, markerType=cv.MARKER_DIAMOND,
                          markerSize=int((7 * thickness) * perspective_coef), thickness=thickness)

    def draw_complete_particle(self, offset, position, ir, skew, convergence, ip):

        # Drawing of the particular particle using offset and position
        self.draw_particular_plant(offset, position)

        # Drawing the horizontally neighboring plants to the particular plant
        self.draw_horizontal_neighbors(offset, position, ir)

    def draw_particular_plant(self, offset, position):
        if not (self.are_coordinates_valid(offset, position)):
            print("Error: offset and/or position has an invalid value")
            return -1
        center = np.asarray([offset, position])

        perspective_coef = center[1] / self.world.height
        color = (0, 255, 0)

        cv.drawMarker(self.img, center, color, markerType=cv.MARKER_DIAMOND,
                      markerSize=int(40 * perspective_coef), thickness=4)

    def draw_horizontal_neighbors(self, offset, position, ir):
        """
        Draws the horizontal neighbours of the particular plant, in other words plants that are located to the left,
        right and at the same height as the particular plant.
        """

        # Drawing parameters
        perspective_coef = position / self.world.height
        color = (255, 0, 0)

        # Drawing left neighbors
        leftOffset = offset - ir

        while self.are_coordinates_valid(leftOffset, position):
            center = np.asarray([leftOffset, position])

            cv.drawMarker(self.img, center, color, markerType=cv.MARKER_DIAMOND,
                          markerSize=int(40 * perspective_coef), thickness=4)

            leftOffset -= ir

        # Drawing right neighbors
        rightOffset = offset + ir

        while self.are_coordinates_valid(rightOffset, position):
            center = np.asarray([rightOffset, position])

            cv.drawMarker(self.img, center, color, markerType=cv.MARKER_DIAMOND,
                          markerSize=int(40 * perspective_coef), thickness=4)

            rightOffset += ir

    def draw_top_particular_plant(self, offset, position, skew):
        return True

    def are_coordinates_valid(self, x, y):
        """
        Returns a boolean indicating whether (x, y) is inside the image or not (valid position or not).
        """
        if x < 0 or x > self.world.width:
            return False

        if y < 0 or y > self.world.height:
            return False

        return True

    def draw(self, plants, particles, n_particles):
        # Empty image
        self.img = np.zeros((self.world.height, self.world.width, 3), np.uint8)

        # Draw plants and particles
        self.draw_plants(plants)
        self.draw_particles(particles, n_particles)

        # Testing of the function draw_complete_particle
        #self.img = np.zeros((self.world.height, self.world.width, 3), np.uint8)

        offset = 250
        position = self.world.height - 40
        ir = 70

        #self.draw_complete_particle(offset, position, ir, -1, -1, -1)

    def clear(self):
        self.img = np.zeros((self.world.height, self.world.width, 3), np.uint8)


# Weeds needs to be added
class Plants:
    def __init__(self, world, vp_height, vp_width, ir, ip, o, s, c, nb_rows, nb_plant_types):
        # Initialize plants positions
        # World contains the width and height of the image
        self.world = world

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

        # Plants generation parameters
        vp_distance = np.absolute(world.height - vp_height)

        self.nb_rows = nb_rows
        self.nb_plant_types = nb_plant_types
        self.max_number_plants_per_row = np.ceil(vp_distance / self.inter_plant_distance)

        # List containing positions of all the plants
        self.plant_positions = []
        self.plants_rows = []
        self.plant_types = []

        # Initialize standard deviation noise for plants motion
        self.std_move_distance = 0

        # Initialize standard deviation noise for plants position measurement
        self.std_meas_position = 0

    def generate_plants(self):
        for i in range(self.nb_rows):
            # Empty image
            img = np.zeros((self.world.height, self.world.width), np.uint8)

            # Get position of lines crossing in the vanishing point
            cv.line(img, (i * self.inter_row_distance + self.offset, self.world.height), self.vanishing_point, 255, 1)
            coordinates = np.where(img != 0)
            row_coordinates = np.array(list(zip(coordinates[1], coordinates[0])))
            self.plants_rows.append(row_coordinates)

            # Generate initial positions of the plants for a row
            # number of plants in the row : between 70% and 100% of the maximum number of plants per row
            nb_plants = np.random.randint(np.floor(0.70 * self.max_number_plants_per_row),
                                          self.max_number_plants_per_row)
            # random positions for each plant
            random_selection = np.random.choice(np.arange(self.vp_height, self.world.height, self.inter_plant_distance),
                                                nb_plants, replace=False)
            # add of a little noise
            for j in range(len(random_selection)):
                selection = random_selection[j]
                # Gaussian centered around the original coordinates
                random_selection[j] = np.random.normal(selection, 11, 1)

            self.plant_positions.append(random_selection)

            # Mapping a type for each plant
            plant_markers = np.random.choice(self.nb_plant_types, nb_plants)
            self.plant_types.append(plant_markers)

        # Find highest plant across all rows
        # self.highest_plant = np.min(sum([list(sublist) for sublist in self.initial_plant_positions], []))

    def move(self, desired_move_distance):
        # Compute relative motion (true motion is desired motion with some noise)
        move_distance = np.random.normal(loc=desired_move_distance, scale=self.std_move_distance, size=1)[0]

        # Move every plants
        for row_idx in range(self.nb_rows):
            for i in range(len(self.plant_positions[row_idx])):
                self.plant_positions[row_idx][i] += move_distance

    def getPlantsToDraw(self, row_idx):
        """
        Returns a list containing the positions and a list containing the type of the plants to draw given a row index.
        Used by the visualizer.

        :param row_idx: Index of the row where we look for plants
        :returns (list containing the positions, list containing the types):
        """

        if row_idx < 0 or row_idx >= self.nb_rows:
            print("Error the row index is incorrect")
            return -1

        current_plants_positions = np.asarray(self.plant_positions[row_idx])
        last_point_of_row = self.plants_rows[row_idx][-1][1]
        visible_plants_positions = current_plants_positions[
            (current_plants_positions >= 0) & (current_plants_positions <= last_point_of_row)]

        plant_positions = self.plants_rows[row_idx][visible_plants_positions]
        plant_types = self.plant_types[row_idx][
            (current_plants_positions >= 0) & (current_plants_positions <= last_point_of_row)]

        return plant_positions, plant_types


# Main
# Initialize world
world = World(500, 700, 10)

# Initialize visualizer
visualizer = Visualizer(world)

# Initialize plants
plants = Plants(world, -100, 250, 80, 110, o=0, s=0, c=0, nb_rows=7, nb_plant_types=4)
plants.generate_plants()

# Number of steps
steps = 70

# Setpoint (desired) motion distance
plants_setpoint_motion_move_distance = 11

# Visualize
for i in range(steps):
    # Simulate plants motion (required motion will not excatly be achieved)
    plants.move(plants_setpoint_motion_move_distance)

    # Visualization
    visualizer.clear()
    visualizer.draw_plants(plants)
    cv.imshow("Crop rows", visualizer.img)
    cv.waitKey(0) # Show maximum normalized particle weight (converges to 1.0) and correctness (0 = correct)

