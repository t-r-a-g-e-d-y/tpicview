tpicview
-
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

---
### Point Sample

![Point Sample](point_sample.jpg)

### Average Sample

![Average Sample](average_sample.jpg)

### Original

![Original](lena.jpg)

