# Stroked

An attempt to make a font drawing software with GTK.
This software will be designed to draw stroke font (single-line font) and based on a restrictive pixel grid only.
It will be possible to generate font files by providing the desired line thickness and I will try to find a solution to generate fonts that can be used by CNC/plotters.

For now it can only be used as a python module.

## Setup

```bash
# from the root of this repo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# from 'stroked/data/'
glib-compile-resources stroked.gresource.xml
```

## Run

```bash
# from the root of this repo
source venv/bin/activate
python3 -m stroked
```

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
