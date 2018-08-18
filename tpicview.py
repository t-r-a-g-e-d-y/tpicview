#!/usr/bin/env python3
import time

from PIL import Image

def image_to_ansi(image, scale=1.0, sample_method='point'):
    '''
    :param image: PIL Image
    :param scale: scale factor
    :param sample_method: `point` or `average`
    '''
    # the 0.25 multiplier makes a rendered image more closely
    # match the size of the original image
    if scale != 1.0:
        scale = scale * 0.25
        new_size = (int(image.width*scale), int(image.height*scale))
        image = image.resize(new_size)
    else:
        new_size = (int(image.width*0.25), int(image.height*0.25))
        image = image.resize(new_size)

    if image.mode != 'RGB':
        image = image.convert('RGB')

    width, height = image.size
    ansi_image = ''

    color_code = '\033[38;2;{};{};{}m\033[48;2;{};{};{}m▀'
    for y in range(0, height-4, 4):
        for x in range(0, width-2, 2):
            if sample_method == 'average':
                top_pxls = [image.getpixel((_x, _y)) for _y in range(y, y+2) for _x in range(x, x+2)]
                bot_pxls = [image.getpixel((_x, _y)) for _y in range(y+2, y+4) for _x in range(x, x+2)]

                top_px = average_pixels(top_pxls)
                bot_px = average_pixels(bot_pxls)
            elif sample_method == 'point':
                top_px = image.getpixel((x, y))
                bot_px = image.getpixel((x, y+2))
            else:
                raise ValueError('sample_method must be one of `average`, `point`')

            ansi_image += color_code.format(*top_px, *bot_px)

        ansi_image += '\033[0m\n'

    return ansi_image

def average_pixels(pixels):
    '''
    :param pixels: list of (r,g,b) tuples
    '''
    num_pixels = len(pixels)
    return [sum(px) // num_pixels for px in zip(*pixels)]

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

def play_gif(image, scale, maxfps=24, hide_fps=False, sample_method='point'):
    '''
    :param image: PIL Image
    :param scale: scale factor
    :param sample_method: `point` or `average`
    '''
    print('\033[2J') # clear screen
    start_time = last_time = time.time()
    count = 0

    while(1):
        print('\033[;H') # move cursor to 0,0
        ansi_image = image_to_ansi(image, scale, sample_method)
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
            play_gif(image, args.scale, args.fps, args.hide_fps, args.sample)
        except KeyboardInterrupt:
            print('\033[0m\033[2J')
            exit()
    else:
        ansi_image = image_to_ansi(image, args.scale, args.sample)
        print(ansi_image, end='')

if __name__ == '__main__':
    import argparse

    sample_methods = [
        'average',
        'point'
    ]

    parser = argparse.ArgumentParser(description='View image or play gif in the terminal')
    parser.add_argument('file', help='Image to display')
    parser.add_argument('-sc', '--scale', default=1.0, help='Scale factor', metavar='n', type=float)
    parser.add_argument('-f', '--fps', default=24, help='Max FPS (for gifs)', metavar='n', type=int)
    parser.add_argument('-sp', '--sample', default='point', help='Sample method', choices=sample_methods)
    parser.add_argument('--hide-fps', default=False, help='Don\'t print FPS (for gifs)', action='store_true')
    args = parser.parse_args()

    main(args)
