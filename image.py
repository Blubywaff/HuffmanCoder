from PIL import Image
import numpy as np


def convert_to_bmp(filename):
    Image.open(filename).save('.'.join(filename.split('.')[:-1])+'.bmp')


if __name__ == "__main__":
    # convert_to_bmp('image.jpg')

    print(np.asarray(Image.open('image.jpg')).shape)
