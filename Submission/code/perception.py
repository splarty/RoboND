import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160), obs=True):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    if obs:
        color_select += 1
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    thresh =      (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    if obs:
        color_select[thresh] = 0
    else:
        color_select[thresh] = 1

    # Return the binary image
    return color_select

def color_thresh_rock(img, hsv_thresh_lower=(20, 100, 100), hsv_thresh_upper=(30, 255, 255)):
    color_select = np.zeros_like(img[:,:,0])

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    #modify the upper and lower bounds of the filter
    #to alter the filter Tektron3000. BGR
    lower_gold = np.array([hsv_thresh_lower[0], hsv_thresh_lower[1], hsv_thresh_lower[2]])
    upper_gold = np.array([hsv_thresh_upper[0], hsv_thresh_upper[1], hsv_thresh_upper[2]])

    mask = cv2.inRange(hsv, lower_gold, upper_gold)
    res = cv2.bitwise_and(img,img, mask= mask)
    color_select[mask] = 1

    return color_select


def color_thresh_obs(img, rgb_thresh_lower=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    thresh =      (img[:,:,0] < rgb_thresh_lower[0]/3)  \
                & (img[:,:,1] < rgb_thresh_lower[1]/3) \
                & (img[:,:,2] < rgb_thresh_lower[2]/3)
    # Index the array of zeros with the boolean array and set to 1
    color_select[thresh] = 1
    # Return the binary image
    return color_select

# Define a function to convert to rover-centric coordinates
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to apply a rotation to pixel positions
# Define a function to apply a rotation to pixel positions
def rotate_pix(xpix, ypix, yaw):
    # TODO:
    # Convert yaw to radians
    # Apply a rotation
    yaw_rad = (yaw/180)*np.pi
    xpix_rotated = xpix * np.cos(yaw_rad) - ypix * np.sin(yaw_rad)
    ypix_rotated = xpix * np.sin(yaw_rad) + ypix * np.cos(yaw_rad)
    # Return the result  
    return xpix_rotated, ypix_rotated

# Define a function to perform a translation
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # TODO:
    # Apply a scaling and a translation
    xpix_translated = np.int_(xpos + (xpix_rot / scale))
    ypix_translated = np.int_(ypos + (ypix_rot / scale))
    # Return the result  
    return xpix_translated, ypix_translated

# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    image = Rover.img

    dataXpos = Rover.pos[0]
    dataYpos = Rover.pos[1]
    dataYaw = Rover.yaw

    # 1) Define source and destination points for perspective transform
    dst_size = 5 
    # Set a bottom offset to account for the fact that the bottom of the image 
    # is not the position of the rover but a bit in front of it
    # this is just a rough guess, feel free to change it!
    bottom_offset = 3

    # source = np.float32([[ 14, 141], [300 ,141 ], [196,97 ], [117 ,97 ] ])

    source = np.float32([[ 13, 140], [302 ,140 ], [202,96 ], [119 ,96 ] ])
    # source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],
                      [image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],
                      [image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset], 
                      [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                      ])
    # 2) Apply perspective transform
    warped = perspect_transform(image, source, destination)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    rgb_threshold=(170, 170, 170)

    threshed = color_thresh(warped,rgb_threshold, False)
    threshedRock = color_thresh_rock(warped)
    threshedObs = color_thresh(warped, rgb_threshold)

    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    ###### NOT SURE WHY THIS IMAGE IS NOT SHOWING
    Rover.vision_image[:,:,0] = threshedObs
    Rover.vision_image[:,:,1] = threshedRock
    Rover.vision_image[:,:,2] = threshed

    # 5) Convert map image pixel values to rover-centric coords
    xpix, ypix = rover_coords(threshed)
    xpixRock, ypixRock = rover_coords(threshedRock)
    xpixObs, ypixObs = rover_coords(threshedObs)
    # 6) Convert rover-centric pixel values to world coordinates
    scale = 10
    # Get navigable pixel positions in world coords
    obstacle_x_world, obstacle_y_world = pix_to_world(xpixObs, ypixObs, dataXpos, 
                                    dataYpos, dataYaw, 
                                    Rover.worldmap.shape[0], scale)
    rock_x_world, rock_y_world = pix_to_world(xpixRock, ypixRock, dataXpos, 
                                    dataYpos, dataYaw, 
                                    Rover.worldmap.shape[0], scale)
    navigable_x_world, navigable_y_world = pix_to_world(xpix, ypix, dataXpos, 
                                    dataYpos, dataYaw, 
                                    Rover.worldmap.shape[0], scale)
    # 7) Update Rover worldmap (to be displayed on right side of screen)
    if (Rover.pitch < 0.5) and (Rover.roll < 350):
        Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1    
    # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
    #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
    #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1

    # 8) Convert rover-centric pixel positions to polar coordinates
    dist, angles = to_polar_coords(xpix, ypix)
    mean_dir = np.mean(angles)
    distRock, anglesRock = to_polar_coords(xpixRock, ypixRock)
    mean_dirRock = np.mean(anglesRock)
    distObs, anglesObs = to_polar_coords(xpixObs, ypixObs)
    mean_dirObs = np.mean(anglesObs)    
    # Update Rover pixel distances and angles
    Rover.nav_dists = dist
    Rover.nav_angles = angles
    Rover.rock_dists = distRock
    Rover.rock_angles = anglesRock
 
    
    
    return Rover