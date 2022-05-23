#!/usr/bin/env python3
"""
Converts an image into a 512 char long compressed string.
How is it encoded:
    the number in front of a char represents how many pixels of the same color are in a row,
    chars !#$%&()*+,./:;<=>?@[Ñ]^_{|}~¢£¤¥¦§¨©ª«¬Ö®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÈÌÐ represent the color.
    There's 62 colors including eraser and tan, eraser is not recommended as it leaves an edge
"""
import os
import sys
import tkinter
from math import sqrt
from pathlib import Path
from tkinter import filedialog
from typing import Tuple, List, NamedTuple

try:
    import pyautogui
    import pyperclip
    from PIL import Image, ImageGrab
except ModuleNotFoundError:
    print(f'Please execute "{sys.executable} -m pip install -U PyAutoGUI pyperclip Pillow" and run this script again')
    input()


class ImageCoords(NamedTuple):
    min_y: int
    min_x: int

    max_y: int
    max_x: int


PixelColor = Tuple[int, int, int]

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
    (255, 181, 136): "Ì",
    (255, 255, 255): "Ð"  # Pure white/eraser. It causes weird edges so it should be avoided.    Tag = "Ð"
}


def get_image() -> Image:
    """
    Ask user to input string name, open it. Image has to be in the same directory as the parent directory of this file
    :return: The image path
    """
    print("Open image")
    root = tkinter.Tk()
    root.withdraw()
    img_path = filedialog.askopenfilename(filetypes=[("Image", "*.png")])
    root.destroy()

    img = Image.open(img_path)

    # If the image has attribute `palette`, open Paint and return None
    if img.palette:
        print("Image has `Palette` attribute. Open it in Paint and save.")
        os.system(f'mspaint.exe "{Path(img_path)}"')
        return None

    return img


def closest_color(pixel_color: PixelColor) -> PixelColor:
    """
    Take an RGB value and find the closest pair in `RR_PALETTE`
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


def encode(img: Image) -> list[str]:
    """
    Take an image and encodes it into a list of 512 char strings {Optional:[number of pixels][color]}
    :param img: The image to be encoded.
    :return: List of 512 char long strings
    """
    pixel_color: List[str] = []

    print("Encoding")
    for y in range(img.height):
        print(f"{int(y / img.height * 100)}%", end="\r")
        for x in range(img.width):
            p = img.getpixel((x, y))  # Gets the color of the pixel at `x, y`
            if len(p) == 4:  # If the value is RGBA, the last `int` is removed
                p = p[:3]
            try:
                # Check if the image has already been dithered, else find the closest color
                p = RR_PALETTE[p]
            except KeyError:
                p = RR_PALETTE[closest_color(p)]
                # closest_color(p)
            pixel_color.append(p)

    colors: List[Tuple[int, str]] = []
    count: int = 0
    current_color: str = pixel_color[0]
    # `count` is the amount of `current_color` in a row

    print("Compressing")
    for c in pixel_color:
        if c != current_color:
            colors.append((count, current_color))
            count = 0
            current_color = c
        count += 1
    colors.append((count, current_color))

    s: str = ""
    img_data: List[str] = []
    for amount, color in colors:
        if amount > 1:
            ns = f"{amount}{color}"
        else:
            ns = color

        if len(s + ns) > 512:
            img_data.append(s)
            s = ""
        s += ns

    img_data.append(s)
    return img_data


def main():
    # Prompt the user to input image name. If the image has attribute `palette` return None
    img: Image = get_image()
    if not img:
        exit()

    # Every image pixel is encoded into a list of 512 char long strings {[amount of pixels][color]}
    img_data: list[str] = encode(img)
    print("______________________\n")

    # Print all image data strings
    print("\n\n".join(img_data))

    # Print amount of 512 char long strings and image dimensions
    print(f"_______________________________________________\n"
          f"Generated {len(img_data)} strings for image WxH {img.width}x{img.height}")

    input()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
