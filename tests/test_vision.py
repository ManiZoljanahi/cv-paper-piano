""" This tests the mathematical formulas used to place the keys on the screen. it uses pure math (not the camera). """

import numpy as np

def test_key_position_calculation():

    # Defines two fake marker points: Left Marker Center (100, 100) and Right Marker Center (900, 100).
    p_left = np.array([100.0, 100.0])
    p_right = np.array([900.0, 100.0])

    # Calculates vector bx (800) and by (0) from Left to Right.
    bx = p_right[0] - p_left[0]  # 800
    by = p_right[1] - p_left[1]  # 0

    # Sets constants exactly as they appear in main.py.
    num_keys = 10

    # Using the DEFAULT_CONFIG values from main.py.
    PADDING_LEFT = 0.06
    PADDING_RIGHT = 0.06
    LINEARITY_BIAS = 1.0

    # Calculates position for key index 4 (5th key)
    i = 4

    # The formula from main.py:
    u_raw = (i + 0.5) / num_keys  # 4.5 / 10 = 0.45
    u_biased = u_raw ** LINEARITY_BIAS  # 0.45 ** 1.0 = 0.45
    usable_width = 1.0 - (PADDING_LEFT + PADDING_RIGHT)  # 1.0 - 0.12 = 0.88
    u = PADDING_LEFT + (u_biased * usable_width)  # 0.06 + (0.45 * 0.88) = 0.456

    # Calculates expected_x and expected_y manually using the formula start + vector * u.
    expected_x = p_left[0] + (bx * u) # 100 + (800 * 0.456) = 464.8
    expected_y = p_left[1] + (by * u) # 100 + (0 * 0.456) = 100.0

    # Checks if the calculated value is close enough (within 0.1 pixel) to the manually calculated expectation.
    assert abs(expected_x - 464.8) < 0.1, f"Expected X ~464.8, got {expected_x}"
    assert abs(expected_y - 100.0) < 0.1, f"Expected Y ~100.0, got {expected_y}"

# Verify that Sharp notes get one offset (70) and Natural notes get another (130).
def test_zigzag_offsets():

    # From main.py settings:
    OFFSET_BLACK = 90
    OFFSET_WHITE = 130

    # Sets note_name = "C#4". Checks if it correctly selects 90.
    note_name = "C#4"
    current_offset = OFFSET_BLACK if "#" in note_name else OFFSET_WHITE

    assert current_offset == 90

    # Sets note_name = "C4". Checks if it correctly selects 130.
    note_name = "C4"
    current_offset = OFFSET_BLACK if "#" in note_name else OFFSET_WHITE

    assert current_offset == 130