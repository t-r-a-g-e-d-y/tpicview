**tpicview** is a simple tool for displaying images in a terminal using ANSI color codes and the ▀ character.


### Usage

```
usage: tpicview [-h] [-sc n] [-sp {average,point}] [-f n] [-hf] [-T]
                [file [file ...]]

View images and play gifs in the terminal.

positional arguments:
  file                  Image(s) to display

optional arguments:
  -h, --help            show this help message and exit
  -sc n, --scale n      Scale factor
  -sp {average,point}, --sample {average,point}
                        Sample method
  -f n, --fps n         Max FPS (for gifs)
  -hf, --hide-fps       Don't print FPS (for gifs)
  -T, --thumbnail       Thumbnail display of files
```

### Requirements

`Pillow>=5.2.0`


### Examples

#### Gif Playback

![Gif Playback](https://thumbs.gfycat.com/PoliteBoldKillifish-size_restricted.gif)

#### Average Sample

![Average Sample](average_sample.jpg)

#### Point Sample

![Point Sample](point_sample.jpg)

#### Original

![Original](lena.jpg)

