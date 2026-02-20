""" This script creates the physical PNG images of printable piano sheets. """

import os
import shutil
import numpy as np
import cv2

def generate_seamless_piano():

    # Sets A4 resolution (3508x2480). Sets top margin.
    page_width, page_height = 3508, 2480
    keys_top_y = int(page_height * 0.25)
    output_dir = "piano_pages"

    # Deletes piano_pages folder if it exists, then recreates it (clean slate).
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # It mathematically calculates which keys have a black key to their right.
    has_black_to_right = set()
    has_black_to_right.add(0)

    # Uses octave_pattern to populate has_black_to_right set for the whole piano.
    # Octave Pattern: C-Yes, D-Yes, E-No, F-Yes, G-Yes, A-Yes, B-No
    octave_pattern = [True, True, False, True, True, True, False]

    current_wk = 2  # Starts at C1.

    for _ in range(7):
        for has_black in octave_pattern:
            if has_black:
                has_black_to_right.add(current_wk)
            current_wk += 1

    # Defines how many white keys fit on each page.
    wk_per_page = [9, 9, 9, 9, 9, 7]

    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker_id = 0
    wk_start_index = 0
    print("Generating 88-Key Seamless Piano...")

    for page_num, num_keys in enumerate(wk_per_page, 1):

        # Creates a white image.
        img = np.ones((page_height, page_width, 3), dtype=np.uint8) * 255
        wk_width = page_width / num_keys
        bk_width = wk_width * 0.55
        bk_height = (page_height - keys_top_y) * 0.65

        # Draws rectangles and outlines for white keys based on wk_width.
        for i in range(num_keys):
            x1 = int(i * wk_width)
            x2 = int((i + 1) * wk_width)

            # Fill Off-White
            cv2.rectangle(img, (x1, keys_top_y), (x2, page_height), (250, 250, 245), -1)

            # Outline
            cv2.rectangle(img, (x1, keys_top_y), (x2, page_height), (0, 0, 0), 3)

        # Checks has_black_to_right. Draws black rectangles centered on the lines between white keys.
        # Includes logic for "Left Edge Seam" (half black key on the left edge).
        if (wk_start_index - 1) in has_black_to_right:
            bk_x1 = int(0 - (bk_width / 2))
            bk_x2 = int(0 + (bk_width / 2))
            cv2.rectangle(
                img,
                (bk_x1, keys_top_y),
                (bk_x2, int(keys_top_y + bk_height)),
                (0, 0, 0),
                -1,
            )

        # Standard Black Keys
        for i in range(num_keys):
            global_idx = wk_start_index + i
            if global_idx in has_black_to_right:
                center_x = int((i + 1) * wk_width)
                bk_x1 = int(center_x - (bk_width / 2))
                bk_x2 = int(center_x + (bk_width / 2))
                cv2.rectangle(
                    img,
                    (bk_x1, keys_top_y),
                    (bk_x2, int(keys_top_y + bk_height)),
                    (0, 0, 0),
                    -1,
                )

        # Generates two ArUco markers (marker_id and marker_id+1).
        # Places markers in the top-left and top-right corners.
        marker_img_l = cv2.aruco.generateImageMarker(aruco_dict, marker_id, 300)
        marker_img_l = cv2.cvtColor(marker_img_l, cv2.COLOR_GRAY2BGR)
        img[150:450, 150:450] = marker_img_l
        marker_img_r = cv2.aruco.generateImageMarker(aruco_dict, marker_id + 1, 300)
        marker_img_r = cv2.cvtColor(marker_img_r, cv2.COLOR_GRAY2BGR)
        img[150:450, page_width - 450 : page_width - 150] = marker_img_r

        # Saves the PNG.
        filename = os.path.join(output_dir, f"Page_{page_num}.png")
        cv2.imwrite(filename, img)
        print(f"Generated Page {page_num} (Markers {marker_id}, {marker_id+1})")

        # Increments marker_id by 2 for the next page.
        marker_id += 2
        wk_start_index += num_keys

# Ensures the function only runs if the file is executed directly.
if __name__ == "__main__":
    # Generates 6 PNG files representing the 88-key piano.
    generate_seamless_piano()
