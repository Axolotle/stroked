# Stroked

An attempt to make a font drawing software with GTK.
This software will be designed to draw stroke font (single-line font) and based on a restrictive pixel grid only.
It will be possible to generate font files by providing the desired line thickness and I will try to find a solution to generate fonts that can be used by CNC/plotters.

## BUILD

I didn't quite understand what i was supposed to do so for now you can install this software by building it yourself after installing the following dependencies.

### Run-time Dependencies
- python3
- python3-gi
- python3-gi-cairo
- gir1.2-gtk-3.0
- python3-defcon
- python3-ufo2ft

### Build Dependencies
- pkg-config
- meson

### Building

```bash
# get the source files
git clone https://github.com/Axolotle/stroked.git
cd stroked/

# init meson
meson _build
# build the thing
ninja -C _build
```

### Run without installing

```bash
# from your/path/to/stroked
ninja -C _build run
# or from your/path/to/stroked/_build
ninja run
```

### Installing

```bash
# from your/path/to/stroked
sudo ninja -C _build install
# or from your/path/to/stroked/_build
sudo ninja install
```

### Run after installation
```bash
# from anywhere on the command line or from your launcher
stroked
```

### Uninstall
```bash
# from your/path/to/stroked
sudo ninja -C _build uninstall
# or from your/path/to/stroked/_build
sudo ninja uninstall
```

Files installed:
- `stroked` folder with the python scripts in `/usr/local/share/`
- `space.autre.stroked.desktop` file in `/usr/local/share/applications/`
- `stroked` file script in `usr/local/bin/`


## GLADE

In `glade` preferences, simply add a path to `data/` to load the custom catalog.  
There's no special behavior but at least you wont get errors.


## Licence

Copyright (C) 2020 Nicolas Chesnais

This program is free software: you can redistribute it and/or modify  
it under the terms of the GNU General Public License as published by  
the Free Software Foundation, either version 3 of the License, or  
(at your option) any later version.

This program is distributed in the hope that it will be useful,  
but WITHOUT ANY WARRANTY; without even the implied warranty of  
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the  
GNU General Public License for more details.

You should have received a copy of the GNU General Public License  
along with this program. If not, see [licenses](https://www.gnu.org/licenses/).
