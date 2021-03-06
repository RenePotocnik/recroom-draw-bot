"""
Converts a PNG image into strings of predefined length
How is it encoded:
    the number in front of a char represents how many pixels of the same color are in a row,
    chars !#$%&()*+,./:;<=>?@[Ñ]^_{|}~¢£¤¥¦§¨©ª«¬Ö®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÈÌÐ represent the color.
    There's 62 colors including eraser and tan, eraser is not recommended as it leaves an edge
"""
import os
import subprocess
import sys
import time
import tkinter
import subprocess
from math import sqrt
from pathlib import Path
from tkinter import filedialog
from typing import Tuple, List, NamedTuple

try:
    import pyautogui
    import pyperclip
    from PIL import Image, ImageGrab
except ModuleNotFoundError:
    print(f'Please execute the following line and run the script again:\n'
          f'{sys.executable} -m pip install -U PyAutoGUI pyperclip Pillow')
    # Ask the user to install all the necessary packages automatically
    if input("Proceed to run the command automatically? [yes/no] ").find("yes") != -1:
        subprocess.call(f"{sys.executable} -m pip install -U PyAutoGUI pyperclip Pillow")
    exit()


class ImageCoords(NamedTuple):
    min_y: int
    min_x: int

    max_y: int
    max_x: int


ListCreateSize: int = 50  # The max. size of a `List Create`. 50 using `List Add`, 64 using `List Create`
MaxStringLength: int = 280  # Maximum length string

# The Max. size of a square canvas
MaxSquareCanvasSize: tuple[int, int] = (1024, 1024)
# The Max. size of a rectangle canvas. It can be horizontal or vertical
MaxRectangleCanvasSize: Tuple[tuple[int, int], tuple[int, int]] = ((1024, 1429), (1429, 1024))

# Typing alias for color
PixelColor = Tuple[int, int, int]

# All of RecRoom color in order + tan marker + eraser
RR_PALETTE: dict = {
    (228, 80, 80): "!",
    (211, 23, 24): "#",
    (117, 7, 6): "$",
    (123, 47, 47): "%",
    (239, 127, 79): "&",
    (245, 92, 25): "(",
    (193, 55, 9): ")",
    (127, 66, 47): "*",
    (247, 215, 106): "+",
    (244, 197, 31): ",",
    (181, 99, 0): ".",
    (130, 97, 56): "/",
    (137, 177, 81): ":",
    (105, 161, 24): ";",
    (47, 76, 9): "<",
    (66, 82, 43): "=",
    (103, 190, 122): ">",
    (16, 101, 34): "?",
    (6, 59, 17): "@",
    (51, 76, 55): "[",
    (103, 218, 205): "Ñ",
    (0, 155, 137): "]",
    (0, 80, 71): "^",
    (51, 86, 82): "_",
    (101, 199, 236): "{",
    (2, 172, 234): "|",
    (6, 87, 117): "}",
    (49, 91, 105): "~",
    (100, 161, 244): "¢",
    (23, 107, 221): "£",
    (7, 57, 128): "¤",
    (50, 79, 121): "¥",
    (165, 133, 242): "¦",
    (80, 24, 221): "§",
    (46, 18, 120): "¨",
    (86, 72, 121): "©",
    (225, 148, 242): "ª",
    (121, 66, 131): "«",
    (66, 24, 74): "¬",
    (88, 61, 92): "Ö",
    (238, 120, 178): "®",
    (234, 46, 79): "¯",
    (130, 9, 63): "°",
    (104, 56, 78): "±",
    (126, 64, 25): "²",
    (69, 40, 22): "³",
    (61, 29, 14): "´",
    (36, 16, 5): "µ",
    (197, 132, 92): "¶",
    (143, 99, 72): "·",
    (90, 62, 48): "¸",
    (37, 28, 21): "¹",
    (246, 239, 233): "º",  # Second-whitest white that is not an eraser    Tag = "º"
    (192, 188, 185): "»",
    (153, 149, 146): "¼",
    (124, 120, 119): "½",
    (99, 100, 102): "¾",
    (73, 74, 78): "¿",
    (45, 46, 50): "À",
    (25, 23, 24): "È",
    # (255, 181, 136): "Ì",  # Tan
    # (254, 254, 254): "Ð"  # # Pure white/eraser. It causes weird edges so it should be avoided.
}

# All the RecRoom colors in one list. [R, G, B, R, G, B,...]
ALL_COLORS = [num for tup in RR_PALETTE.keys() for num in tup]


def get_image() -> Image:
    """
    Open file explorer, wait for user to open a PNG image
    :return: The image
    """
    print("Open image", end="\r")
    root = tkinter.Tk()
    root.withdraw()
    img_path = filedialog.askopenfilename(filetypes=[("Image", "*.png")])
    root.destroy()

    img = Image.open(img_path)

    # Check if the image is smaller than the max resolution of the canvas.
    for width, height in MaxRectangleCanvasSize:  # ((1024, 1429), (1429, 1024))
        if img.width <= width and img.height <= height:
            # The image is not too big
            break
    else:
        # If the image is too big prompt the user to continue or exit.
        if input("Max. image size is 1024*1429 (rectangle - vertical), "
                 "1429*1024 (rectangle - horizontal) or 1024*1024 (square).\n"
                 "Your image exceeds these parameters thus it will take longer to print at no noticeable difference.\n"
                 f"Selected image dimensions [W*H]: {img.width}*{img.height}\n"
                 "Do you wish to continue anyway? [yes/no] > ").find("yes") == -1:
            exit()

    # If the image has attributed `palette` its metadata is a bit different.
    # To solve this just open the image in paint and save it
    if img.palette:
        print("Image has `Palette` attribute. Open it in Paint and save.")
        os.system(f'mspaint.exe "{Path(img_path)}"')
        return None

    return img


def closest_color(pixel_color: PixelColor) -> PixelColor:
    """
    Take an RGB value and find the closest color in `RR_PALETTE`

    It is recommended you use external programs to convert and dither images.
    2 ACO (swatch) files are included if you're using Photoshop

    :param pixel_color: The color of the pixel of the image
    :return: The color from `RR_PALETTE` that is closest to `pixel_color`
    """
    r, g, b = pixel_color
    color_diffs: List[tuple[float, PixelColor]] = []
    for key in RR_PALETTE:
        cr, cg, cb = key
        color_diff = sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2)
        color_diffs.append((color_diff, key))
    return min(color_diffs)[1]


def progress_update(y: int, img: Image, prefix='Progress', suffix='', length=50) -> None:
    """
    Display a progress bar in the console
    :param y: The `y` value of the image
    :param img: The image
    :param prefix: Optional: Text in-front of the progress bar
    :param suffix: Optional: Text behind the progress bar
    :param length: Optional: The length of the progress bar
    """
    completed = int(length * y // img.height)
    empty = length - completed
    bar = "#" * completed + " " * empty
    percent = f"{100 * (y / float(img.height)):.2f}"
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end="\r")

    # Print New Line on Complete
    if y == img.height:
        print(" " * (length + 30), end="\r")


def quantize(img) -> Image:
    img = img.convert("RGB")

    palette_image = Image.new("P", img.size)
    palette_image.putpalette(ALL_COLORS)
    new_image = img.quantize(palette=palette_image,
                             dither=0 if input("Dither the image? [y/n] ").find("n") != -1 else 1).convert("RGB")

    print("Opening the final image...")
    new_image.show()

    return new_image


def encode(img: Image) -> list[str] or None:
    """
    Take an image and encode it into a list of {`MaxStringLength`}-char strings.
    ...[number of pixels][color]...

    :param img: The image to be encoded.
    :return: List of {`MaxStringLength`} char long strings
    """
    pixel_color: List[str] = []
    full_image = Image.new("RGB", img.size)
    dither = False

    img = quantize(img)

    for y in range(img.height):
        for x in range(img.width):
            p = img.getpixel((x, y))  # Gets the color of the pixel at `x, y`
            if len(p) == 4:  # If the value is RGBA, the last `int` is removed
                p = p[:3]
            try:
                # Check if the image has already been dithered, else find the closest color
                p = RR_PALETTE[p]
            except KeyError:
                dither = True
                p = closest_color(p)
                full_image.putpixel((x, y), p)
                p = RR_PALETTE[p]
                # closest_color(p)
            pixel_color.append(p)
        # Print the progress
        progress_update(y + 1, img, "Encoding")

    if dither:
        full_image.show()

    colors: List[Tuple[int, str]] = []
    count: int = 0
    current_color: str = pixel_color[0]
    # `count` is the amount of `current_color` in a row

    for c in pixel_color:
        if c != current_color:
            colors.append((count, current_color))
            count = 0
            current_color = c
        count += 1
    colors.append((count, current_color))

    print(f"Compressed {len(pixel_color)} chars into {len(colors)} chars")

    s: str = ""
    img_data: List[str] = []
    for amount, color in colors:
        if amount > 1:
            ns = f"{amount}{color}"
        else:
            ns = color

        if len(s + ns) > MaxStringLength:  # 512
            img_data.append(s)
            s = ""
        s += ns

    img_data.append(s)
    return img_data


def main(output_strings: bool = False, wait_for_input: bool = False):
    """
    Function to tie together all others.
    Prompt for image, encode and output

    :param wait_for_input: Wait for the user to continue. Useful when running this file directly so that it stays open
    :param output_strings: Print the encoded image strings into the console
    """

    img: Image = get_image()
    if not img:
        exit()

    img_data: list[str] = encode(img)

    if output_strings:
        print("Copying strings\n_______________\n")
        time.sleep(2)
        # Print all image data strings
        print("\n\n".join(img_data))

    # Print amount of {`MaxStringLength`} char long strings, image dimensions and total `List Create`s needed.
    print(f"\nGenerated {len(img_data) + 2} strings for image WxH {img.width}x{img.height}")
    print(f"Space needed: {len(img_data) // ListCreateSize} List creates (+ {len(img_data) % ListCreateSize})")

    if wait_for_input:
        input("Press enter to continue")

    return img_data


if __name__ == '__main__':
    try:
        main(output_strings=True, wait_for_input=True)
    except KeyboardInterrupt:
        pass
