# Draw Bot Encoding

Run `CanvasPrinter.py`.

Select an image you want to import into RecRoom. I suggest the image is already converted into a RecRoom color palette (Photoshop ACO swatch files are included), and scaled to the appropriate size.

If the image is not converted it will automatically get converted, but the image quality might be worse as a result of no image dithering yet being implemented.

After the data has been encoded, you will be prompted to import all data to RecRoom. For this you need the invention called "Variable Data Import".

If you run `Encoding.py` directly, all encoded image data will be printed into the console. If the image is large/colorful it might have too much encoded data to display in `CMD` (by default 9000 lines).


Currently, only 2560x1440 and 1920x1080 resolutions supported.
