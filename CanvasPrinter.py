import ctypes

import Encoding
import Importing


def screen_size_acceptable() -> bool:
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return screensize == (2560, 1440)


def main():
    img_data: list[str] = Encoding.main()

    if input(
            "Copy into List Create of Variable? Default: Variable. [enter number]\n1. List Create\n2. Variable\n> ").find(
            "1") != -1:
        Importing.copy_into_recroom_listcreate(img_data=img_data, auto_continue=False, delay=0.3)
    else:
        # Insert beginning and end. Required when using my Image Printer Bot
        img_data.insert(0, "BEGIN")
        img_data.append("END")
        Importing.copy_into_rr_variable(img_data, delay=0.4, pause_at_50=False, stop_at_500=False)


if not screen_size_acceptable():
    print("Your monitor is not 2560x1440. More dimensions will be added in future updates")
    exit(input("Press enter to exit"))

main()

input("Press enter to exit")
