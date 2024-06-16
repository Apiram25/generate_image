import numpy as np
import cv2 as cv
import json

np.random.seed(45)

def get_angle(xmin,ymin,xmax,ymax):
    a = np.array([xmin, ymax])
    b = np.array([xmin, ymin])
    c = np.array([xmax, ymax])
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    if xmin > xmax:
        return -np.degrees(angle)
    else:
        return np.degrees(angle)
    

for image_idx in range(50):
    # Field parameters
    image_height = 300
    image_width = 300
    vp_height = np.random.randint(-400,-100)
    vp_width = np.random.randint(100,200)
    vanishing_point = (vp_width, vp_height)

    # Plants generation parameters
    nb_of_plants_rows = np.random.randint(3,6)
    row_breadth = np.random.randint(0.7*image_width,image_width)
    inter_row_plants_distance = int(row_breadth / (nb_of_plants_rows-1))

    if (image_width-row_breadth) / (nb_of_plants_rows-1) > 1:
        offset = np.random.randint(0, (image_width-row_breadth) / (nb_of_plants_rows-1))
    else:
        offset = 0
        
    max_number_plants_per_row = 15
    nb_plant_types = 4
    plant_size = 50

    img = np.zeros((image_height, image_width), np.uint8)
    label = {
        "height" : image_height,
        "width" : image_width,
        "nb_of_plants_rows" : nb_of_plants_rows
    }

    plants_rows = []
    initial_plant_positions = []
    plant_types = []
    for i in range(nb_of_plants_rows):
        # Get position of lines crossing in the vanishing point
        cv.line(img, (i * inter_row_plants_distance + offset, image_height), vanishing_point, 255, 1)
        coordinates = np.where(img != 0)
        row_coordinates = np.array(list(zip(coordinates[1], coordinates[0])))
        plants_rows.append(row_coordinates)
        img = np.zeros((image_height, image_width), np.uint8)
        
        angle = get_angle(row_coordinates[-1][0],row_coordinates[0][1],row_coordinates[0][0],row_coordinates[-1][1])
        
        label[f"row_{i}"] = {"xmin": int(row_coordinates[-1][0]),
                             "ymin": int(row_coordinates[0][1]),
                             "xmax": int(row_coordinates[0][0]),
                             "ymax": int(row_coordinates[-1][1]),
                             "angle": int(angle)}
            
        # Generate initial positions of the plants
        nb_plants = np.random.randint(8, max_number_plants_per_row)
        random_selection = np.random.choice(np.arange(vp_height, image_height, 30), nb_plants, replace=False)
        initial_plant_positions.append(random_selection)
        plant_markers = np.random.choice(nb_plant_types, nb_plants)
        plant_types.append(plant_markers)
        
    # Weeds generation parameters
    nb_of_weeds_rows = 56
    inter_row_weeds_distance = 10
    max_number_weeds_per_row = 2
    weeds_size = 10

    weeds_rows = []
    initial_weeds_positions = []
    weeds_types = []
    for i in range(nb_of_weeds_rows):
        cv.line(img, (i * inter_row_weeds_distance + offset, image_height), vanishing_point, 255, 1)
        weeds_coordinates = np.where(img != 0)
        weeds_row_coordinates = np.array(list(zip(weeds_coordinates[1], weeds_coordinates[0])))
        weeds_rows.append(weeds_row_coordinates)
        img = np.zeros((image_height, image_width), np.uint8)
        
        # Generate initial positions of the weeds
        nb_weeds = np.random.randint(0, max_number_weeds_per_row)
        random_selection = np.random.choice(np.arange(vp_height, image_height, 30), nb_weeds, replace=False)
        initial_weeds_positions.append(random_selection)
        weeds_markers = np.random.choice(nb_plant_types, nb_weeds)
        weeds_types.append(weeds_markers)
    
    # Idea: move plants down across rows to create an image sequence
    # Find highest plant across all rows
    highest_plant = np.min(sum([list(sublist) for sublist in initial_plant_positions], []))
    for move_distance in range(0, -1 * vp_height + image_height-1, 10):
        # Stop generating images when the last plant is below the bottom third of the image
        if (highest_plant + move_distance) > image_height/3 * 2:
            break
        
        img = np.zeros((image_height, image_width), np.uint8)
        
        # Draw lines of plants rows
        # for i in range(nb_of_plants_rows):
        #     cv.line(img, (i * inter_row_plants_distance + offset, image_height), vanishing_point, 255, 1)   
            
        # Draw plants    
        nb_plants_per_row = []
        current_plants_positions = []
        visible_plants_positions = []
        for row_idx in range(nb_of_plants_rows):
            current_plants_positions = np.asarray(initial_plant_positions[row_idx] + move_distance)
            last_point_of_row = plants_rows[row_idx][-1][1]
            current_row_plants_types = plant_types[row_idx][(current_plants_positions >= 0) & (current_plants_positions <= last_point_of_row)]
            visible_plants_positions = current_plants_positions[(current_plants_positions >= 0) & (current_plants_positions <= last_point_of_row)] 
            plant_positions = plants_rows[row_idx][visible_plants_positions]
            nb_visible_plants = len(plant_positions)
            for i, center in enumerate(plant_positions):
                if (center[0] < 0) or (center[1] < 0) or (center[0] > image_width) or (center[1] > image_height):
                    nb_visible_plants = nb_visible_plants - 1
                else:
                    perspective_coef = center[1]/(image_height+np.abs(vp_height))
                    if current_row_plants_types[i] == 0:
                        cv.circle(img, center, int(plant_size/2 * perspective_coef), 255, -1)
                    elif current_row_plants_types[i] == 1:
                        cv.drawMarker(img,center,255,markerType = cv.MARKER_CROSS,markerSize = int(plant_size * perspective_coef),thickness = 5)
                    elif current_row_plants_types[i] == 2:
                        cv.drawMarker(img,center,255,markerType = cv.MARKER_TILTED_CROSS,markerSize = int(plant_size * perspective_coef),thickness = 5)
                    else:
                        cv.drawMarker(img,center,255,markerType = cv.MARKER_STAR,markerSize = int(plant_size * perspective_coef),thickness = 5)
            nb_plants_per_row.append(nb_visible_plants) 
        
        # Draw weeds    
        nb_weeds_per_row = []
        current_weeds_positions = []
        visible_weeds_positions = []
        for row_idx in range(nb_of_weeds_rows):
            if len(weeds_rows[row_idx]) != 0:
                current_weeds_positions = np.asarray(initial_weeds_positions[row_idx] + move_distance)
                last_point_of_row = weeds_rows[row_idx][-1][1]
                current_row_weeds_types = weeds_types[row_idx][(current_weeds_positions >= 0) & (current_weeds_positions <= last_point_of_row)]
                visible_weeds_positions = current_weeds_positions[(current_weeds_positions >= 0) & (current_weeds_positions <= last_point_of_row)] 
                weeds_positions = weeds_rows[row_idx][visible_weeds_positions]
                nb_visible_weeds = len(weeds_positions)
                for i, center in enumerate(weeds_positions):
                    if (center[0] < 0) or (center[1] < 0) or (center[0] > image_width) or (center[1] > image_height):
                        nb_visible_weeds = nb_visible_weeds - 1
                    else:
                        perspective_coef = center[1]/(image_height+np.abs(vp_height))
                        if current_row_weeds_types[i] == 0:
                            cv.circle(img, center, int(weeds_size/2 * perspective_coef), 255, -1)
                        elif current_row_weeds_types[i] == 1:
                            cv.drawMarker(img,center,255,markerType = cv.MARKER_CROSS,markerSize = int(weeds_size * perspective_coef),thickness = 5)
                        elif current_row_weeds_types[i] == 2:
                            cv.drawMarker(img,center,255,markerType = cv.MARKER_TILTED_CROSS,markerSize = int(weeds_size * perspective_coef),thickness = 5)
                        else:
                            cv.drawMarker(img,center,255,markerType = cv.MARKER_STAR,markerSize = int(weeds_size * perspective_coef),thickness = 5)
                nb_weeds_per_row.append(nb_visible_weeds) 

        
        # Put bounding boxes of plants rows
        # for i in range(nb_of_plants_rows):
        #     cv.rectangle(img, (label[f"row_{i}"]["xmin"], label[f"row_{i}"]["ymin"]), (label[f"row_{i}"]["xmax"], label[f"row_{i}"]["ymax"]), (255, 0, 0), 1)
        
        # Show image
        # cv.imshow("Crop rows", img)
        # k = cv.waitKey(0)

        # Save image
        cv.imwrite(f"data/images/sample_{image_idx}.jpg",img)
        # Save label
        json_data = json.dumps(label, indent=4)
        f = open(f'data/labels/sample_{image_idx}.json', 'w')
        f.write(json_data)
        
        print(f"Saved image {image_idx}")
        break

