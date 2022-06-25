import subprocess
import sys
from typing import NamedTuple

import pyautogui
import pyperclip
from PIL import ImageGrab

import Encoding
import time


class ImageCoords(NamedTuple):
    min_y: int
    min_x: int

    max_y: int
    max_x: int


class Colors(NamedTuple):
    text = (55, 57, 61)  # The color of text in the Variable Input field (black)
    white = (229, 225, 216)  # The white background of the Variable Input field
    green = (187, 205, 182)  # The Variable Input field sometimes turns green - this is that color.


def is_window_active(window_title: str = "Rec Room") -> bool:
    """
    Does not return before `window_title` becomes the active window
    Returns true when `window_title` becomes the active window

    :param window_title: The title of the window
    :return: When the window becomes active
    """
    if window_title not in (pyautogui.getActiveWindowTitle() or ""):  # getActiveWindowTitle is sometimes `None`
        print(f"Waiting for {window_title} to be the active window... ", end="\r", flush=True)
        # While RecRoom window is not active, sleep
        while window_title not in (pyautogui.getActiveWindowTitle() or ""):
            time.sleep(0.1)
        print(" " * 70, end="\r")  # Empty the last line in the console
        time.sleep(0.5)
    return True


def is_color(compare_color: tuple[int, int, int], main_color: tuple[int, int, int], tolerance: int = 30) -> bool:
    """
    Compare `compare_color` to `main_color` with a given tolerance

    :param compare_color: The color that is being compared
    :param main_color: The color that is being compared
    :param tolerance: How close the colors can be (1 - 255)
    :return: Is `compare_color` same/similar as `main_color`
    """
    return ((abs(compare_color[0] - main_color[0]) < tolerance)
            and (abs(compare_color[1] - main_color[1]) < tolerance)
            and (abs(compare_color[2] - main_color[2]) < tolerance))


def found_colors(main_color: tuple[int, int, int], coordinates: ImageCoords) -> bool:
    """
    Returns True if `main_color` is found in the given coordinates

    :param main_color: The color to compare the detected color to
    :param coordinates: Coordinates of the window of pixels to be checked and compared
    :return: If the color in any of the pixels match the `main_color`
    """
    image = ImageGrab.grab()

    for coords_x in range(coordinates.min_x, coordinates.max_x):
        if is_color(image.getpixel((coords_x, coordinates.min_y)), main_color):
            return True

    return False


def copy_into_rr_variable(img_data: list[str], delay: float = 0.3, pause_at_50: bool = False, stop_at_500: bool = False):
    """
    Function copies strings of data into the RecRoom Variable.

    :param img_data: A list of strings to be imported into RecRoom
    :param delay: The delay between main actions (click > copy > confirm)
    :param pause_at_50: Should the script pause for a given amout of time every 50 imported strings (could prevent dissconnection)
    :param stop_at_500: Should the script full stop every 500 imported strings, and wait for the user to press enter (cound prevent dissconnection)
    """
    input_field: tuple[int, int] = (1294, 828)
    confirm_expand_button: tuple[int, int] = (2165, 113)  # Coords of the "Expand All" button
    confirm_scroll_bar: tuple[int, int] = (2356, 920)  # Coords of the side Scroll Bar
    num_strings: int = len(img_data)

    if input(f"\nProceed to copy all {num_strings} strings to RecRoom? [y/n] ").lower() == "y":
        time_at_start = time.time()

        "########################CONTINUE###########################"
        # If you want to continue from an existing string, set `continue_from` to `False`
        # and enter the string into the bottom `if` statement
        start_from_beginning: bool = True
        continue_from_string: str = "|Enter the string here|"
        "########################################################"

        for num, string in enumerate(img_data):
            is_window_active("Rec Room")

            if start_from_beginning or continue_from_string in string:
                start_from_beginning = True
            else:
                continue

            # Copy current string into clipboard
            pyperclip.copy(string)
            print(f"Copying string #{num}/{num_strings - 1}")

            # In RR, click on the input field
            pyautogui.click(input_field)
            time.sleep(delay)

            # Max 10 tries to successfully copy the string
            for _ in range(10):
                # Paste the string into input
                pyautogui.hotkey("ctrl", "v")
                time.sleep(delay)
                if found_colors(main_color=(55, 57, 61),
                                coordinates=ImageCoords(min_y=662, min_x=262, max_x=400, max_y=680)):
                    break
                print("Failed copy")
                pyautogui.click(input_field)
                pyautogui.hotkey("ctrl", "a")
                time.sleep(delay * 2)

            # Max 10 tries to successfully confirm the string
            for _ in range(10):
                # Click on the "confirm" area
                pyautogui.click(confirm_expand_button)
                time.sleep(delay)
                if not found_colors(main_color=(55, 57, 61),
                                    coordinates=ImageCoords(min_y=662, min_x=262, max_x=400, max_y=680)):
                    break
                print("Failed confirm")
                time.sleep(delay * 2)


            ### Optional:

            if stop_at_500 and num and num % 500 == 0:
                # Every 500 entries stop and let the player continue when they see fit
                input("Stopped. Press enter to continue")
                continue
            if pause_at_50 and num and num % 50 == 0:
                # Every 50 entries give RR some time to process and catch up. Could prevent crashing :shrug:
                time.sleep(30)

        time_to_copy = time.time() - time_at_start
        minutes = time_to_copy // 60
        seconds = time_to_copy % 60
        print(f"Copying complete. Copied {num_strings - 1} strings in {minutes} min and {seconds:.1f} sec")


def main():
    # Call function for encoding an image
    img_data: list[str] = Encoding.main()
    # Insert beginning and end.
    img_data.insert(0, "BEGIN")
    img_data.append("END")

    # Call function for copying into RecRoom
    copy_into_rr_variable(img_data, delay=0.4 , pause_at_50=False, stop_at_500=False)


if __name__ == "__main__":
    main()

# Change to `True` if you want the computer to lock (Win + L) when finished importing. 
# useful if starting print before going to sleep/work
if False:
    subprocess.call("rundll32.exe user32.dll, LockWorkStation")
