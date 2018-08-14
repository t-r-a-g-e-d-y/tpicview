#!/usr/bin/env python3
import time

from PIL import Image

def image_to_ansi(image, scale=1.0):
    '''
    :param image: PIL Image
    :param scale: scale factor
    '''
    if scale != 1.0:
        new_size = (int(image.width*scale), int(image.height*scale))
        image = image.resize(new_size)

    width, height = image.size
    ansi_image = ''

    b_left = 0
    b_upper = 0
    b_right = 4
    b_lower = 8

    color_code = '\033[38;2;{};{};{}m\033[48;2;{};{};{}m▀'
    while (b_right <= width and b_lower <= height):
        while (b_right <= width):
            bounding_box = [b_left, b_upper, b_right, b_lower]

            region_top = image.crop(bounding_box)
            region_bot = region_top.crop([0, 4, 4, 8])

            avg_top = average_color(region_top)
            avg_bot = average_color(region_bot)

            ansi_image += color_code.format(*avg_top, *avg_bot)

            b_left += 4
            b_right += 4

        ansi_image += '\033[0m\n'

        b_left = 0
        b_right = 4
        b_upper += 8
        b_lower += 8

    return ansi_image

def average_color(image):
    '''
    :param image: PIL Image

    Returns average color of `image` as (r,g,b)

    https://stackoverflow.com/questions/12703871
    '''
    num_pixels = image.width * image.height
    colors = image.getcolors() # A list of (count, rgb) values
    color_sum = [(c[0] * c[1][0], c[0] * c[1][1], c[0] * c[1][2]) for c in colors]
    average = ([sum(c)//num_pixels for c in zip(*color_sum)])
    return average

def squeeze(val, oldmin=0, oldmax=255, newmin=0, newmax=1):
    return ((val - oldmin) * (newmax - newmin) / (oldmax - oldmin)) + newmin

def play_gif(image, scale, maxfps=24, hide_fps=False):
    '''
    :param image: PIL Image
    :param scale: scale factor
    '''
    print('\033[2J')
    start_time = last_time = time.time()
    count = 0

    while(1):
        print('\033[;H')
        frame = image.convert('RGB')
        ansi_image = image_to_ansi(frame, scale)
        print(ansi_image, end='')

        try:
            image.seek(image.tell()+1)
        except EOFError:
            image.seek(0)

        elapsed = time.time() - last_time
        if elapsed < 1 / maxfps:
            time.sleep(1 / maxfps - elapsed)
        last_time = time.time()

        if not hide_fps:
            print('FPS: {:.0f}'.format(count / (last_time - start_time)))
        count += 1

def main(args):
    image = Image.open(args.file)

    if image.format == 'GIF':
        try:
            play_gif(image, args.scale, args.fps, args.hide_fps)
        except KeyboardInterrupt:
            print('\033[0m\033[2J')
            exit()
    else:
        ansi_image = image_to_ansi(image, args.scale)
        print(ansi_image, end='')

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='View image or play gif in the terminal')
    parser.add_argument('file', help='Image to display')
    parser.add_argument('-s', '--scale', default=1.0, help='Scale factor', metavar='n', type=float)
    parser.add_argument('-f', '--fps', default=24, help='Max FPS (for gifs)', metavar='n', type=int)
    parser.add_argument('--hide-fps', default=False, help='Don\'t print FPS (for gifs)', action='store_true')
    args = parser.parse_args()

    main(args)
