#!/usr/bin/env python3
import itertools
import shutil
import time

from PIL import Image

def image_to_ansi(image, scale=1.0, sample_method='average'):
    '''
    :param image: PIL Image
    :param scale: scale factor
    :param sample_method: `point` or `average`
    :param box_size: side length of sampling box
    '''
    x_step = 2
    y_step = x_step * 2

    # magic number so that images at 1.0 scale render
    # close to real size
    # based on 10pt monospace font
    magic_scale = x_step / 7.5

    new_width = int(image.width*magic_scale*scale)
    new_height = int(image.height*magic_scale*scale)

    image = image.resize((new_width, new_height))

    if image.mode != 'RGB':
        image = image.convert('RGB')

    width, height = image.size
    ansi_image = ''

    color_code = '\033[38;2;{};{};{}m\033[48;2;{};{};{}m▀'

    pixels = image.getdata()

    for y in range(0, height-y_step, y_step):
        for x in range(0, width-x_step, x_step):
            if sample_method == 'average':
                top_pxls = [pixels[_y*width+_x]
                            for _y in range(y, y+y_step//2)
                            for _x in range(x, x+x_step)]

                bot_pxls = [pixels[_y*width+_x]
                            for _y in range(y+y_step//2, y+y_step)
                            for _x in range(x, x+x_step)]

                top_px = average_pixels(top_pxls)
                bot_px = average_pixels(bot_pxls)
            elif sample_method == 'point':
                top_px = pixels[y*width+x]
                bot_px = pixels[(y+y_step//2)*width+x]
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

def play_gif(image, scale, maxfps=None, hide_fps=False, sample_method='point', box_size=2):
    '''
    :param image: PIL Image
    :param scale: scale factor
    :param maxfps: if provided play gif at constant fps int
    :param hide_fps: don't print fps below gif
    :param sample_method: `point` or `average`
    :param box_size: side length of sampling box
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

        if maxfps:
            elapsed = time.time() - last_time
            if elapsed < 1 / maxfps:
                time.sleep(1 / maxfps - elapsed)
            last_time = time.time()

            if not hide_fps:
                print('FPS: {:.0f}'.format(count / (last_time - start_time)))
        else:
            time.sleep(image.info['duration']/1000)
        count += 1

def thumbnail(files, size, sample_method='point'):
    ansi_images = []

    for fp in files:
        try:
            image = Image.open(fp)
        except OSError:
            # not an image file
            continue
        image.thumbnail(size)
        ansi_images.append(image_to_ansi(image, sample_method=sample_method).split('\n'))

    if not ansi_images:
        return

    term_cols, _ = shutil.get_terminal_size()
    images_per_row = term_cols // (size[0] // 8) # 8 is a magic number based on 10pt monospace font
    num_images = len(ansi_images)

    for i in range(0, num_images, images_per_row):
        zipped = list(itertools.zip_longest(*ansi_images[i:i+images_per_row]))
        width = [s.count('\033') // 2 for s in zipped[0]]
        output = ''
        for row in zipped:
            for i, segment in enumerate(row):
                if not segment:
                    output += '{}{}'.format(' ' if i else '', ' ' * width[i])
                else:
                    output += '{}{}'.format(' ' if i else '', segment)
            output += '\n'
        print(output, end='')

def main(args):
    if args.thumbnail:
        thumbnail(args.file, (256,256), args.sample)
        return

    for fp in args.file:
        try:
            image = Image.open(fp)
        except OSError:
            # not an image file
            continue

        if image.format == 'GIF' and image.info.get('duration'):
            try:
                play_gif(image, args.scale, args.fps, args.hide_fps, args.sample)
            except KeyboardInterrupt:
                print('\033[0m\033[2J')
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
    parser.add_argument('file', nargs='*', help='Image(s) to display')
    parser.add_argument('-sc', '--scale', default=1.0, help='Scale factor', metavar='n', type=float)
    parser.add_argument('-sp', '--sample', default='average', help='Sample method', choices=sample_methods)
    parser.add_argument('-f', '--fps', default=None, help='Max FPS (for gifs)', metavar='n', type=int)
    parser.add_argument('-hf', '--hide-fps', help='Don\'t print FPS (for gifs)', action='store_true')
    parser.add_argument('-T', '--thumbnail', help='Thumbnail display of files (overrides -b and -sc)', action='store_true')
    args = parser.parse_args()

    main(args)
