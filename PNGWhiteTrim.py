from PIL import Image # pip install Pillow
import sys
import glob
from PIL import ImageOps
import numpy as np
import os
import ntpath

# Trim all png images with white background in a folder

_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
folderName = os.path.join(_thisDir, "IPNP_Pictures")

maxsize = 300

filePaths = glob.glob(folderName + "/*.png")
print (filePaths)
newfolderName = os.path.join(_thisDir, "IPNP_Pictures_new")

#os.mkdir(newfolderName)

for filePath in filePaths:
    image = Image.open(filePath)
    image.load()

    # remove alpha channel
    invert_im = image.convert("RGB")

    # invert image (so that white is 0)
    invert_im = ImageOps.invert(invert_im)
    imageBox = invert_im.getbbox()
    imageBox = tuple(np.asarray(imageBox))

    cropped=image.crop(imageBox)

    image_width = (imageBox[2] - imageBox[0])
    image_height = (imageBox[3] - imageBox[1])

    if image_width >= image_height:
        mult_ratio = (float(maxsize) / image_width)
    else:
        mult_ratio = (float(maxsize) / image_height)

    upscaled = cropped.resize((int(image_width * mult_ratio), int(image_height * mult_ratio)))

    filePath_basename = (ntpath.basename(filePath))
    upscaled.save(newfolderName + os.sep + filePath_basename)
