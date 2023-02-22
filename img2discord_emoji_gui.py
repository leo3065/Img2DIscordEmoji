from fractions import Fraction
from pathlib import Path
import os
import tkinter as tk

from PIL import Image

from typing import Tuple


def as_interger_ratio(val: float, max_min_term: int = None) -> Tuple[int]:
    if val > 1:
        frac = Fraction(val)
    else:
        frac = Fraction(1/val)
    if max_min_term is not None:
        frac = frac.limit_denominator(max_min_term)
    if val > 1:
        return frac.as_integer_ratio()
    else:
        return (1/frac).as_integer_ratio()


def main(
        in_filename: str, out_filename: str,
        keep_boarder: bool = False, max_tile_size: int = 1):
    img = Image.open(in_filename)
    img = img.convert('RGBA')

    if not keep_boarder:
        img = img.crop(img.getbbox())
    aspect_ratio = img.size[0]/img.size[1]

    # print(img.size)
    # print(aspect_ratio)

    ## get tile count
    tile_unit = 128
    width_tile, height_tile = as_interger_ratio(
        aspect_ratio, max_tile_size)
    print('tile dimension:', width_tile, height_tile)
    print('tile count:', width_tile*height_tile)

    ## fitting to tiles
    img.thumbnail((width_tile*tile_unit, height_tile*tile_unit))
    img_final = Image.new('RGBA', (width_tile*tile_unit, height_tile*tile_unit))
    
    ## tile alligning
    left = (img_final.size[0] - img.size[0])//2
    top = (img_final.size[1] - img.size[1])//2
    img_final.paste(img, (left, top))

    ## tile cropping
    base_name = out_filename
    filenames = []
    empty_count = 0
    for j in range(height_tile):
        for i in range(width_tile):
            tile = img_final.crop((
                i*tile_unit, j*tile_unit, 
                (i+1)*tile_unit, (j+1)*tile_unit))
            
            # detemine if the tile is empty
            is_empty = tile.getbbox() is None
            if not is_empty:
                filename = ''.join([
                    base_name, 
                    f'_{j+1}' if height_tile>1 else '', 
                    f'_{i+1}' if width_tile>1 else '', 
                    '.png'])
            else: 
                # if the tile is empty, change the tile name
                filename = f'{base_name}_empty.png'
                empty_count += 1
            if not is_empty or empty_count<=1:
                with open(filename, 'wb') as f:
                    tile.save(f, format='png')
                filenames.append(filename)
    print('non-empty tile count:', width_tile*height_tile - empty_count)
    print('empty tile count:', empty_count)
    #print(filenames)


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.setup_widgets()
        self.title('Img2DiscordEmoji')
        self.resizable(False, False)
        self.image = None
    
    def setup_widgets(self):
        app_frame = tk.Frame(self)
        app_frame.grid(row=0, column=0, padx=5, pady=5)
        
        ## Row 0
        button_select_image = self.button_select_image = tk.Button(
            app_frame, text='Select image:')
        button_select_image.grid(
            row=0, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        label_in_path = app_frame.label_in_path = tk.Label(
            app_frame, text='', relief=tk.SUNKEN, width=50, anchor=tk.NW)
        label_in_path.grid(
            row=0, column=1, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ## Row 1
        button_select_out_path = self.button_select_out_path = tk.Button(
            app_frame, text='Select output folder:')
        button_select_out_path.grid(
            row=1, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        label_out_path = app_frame.label_out_path = tk.Label(
            app_frame, text='', relief=tk.SUNKEN, width=50, anchor=tk.NW)
        label_out_path.grid(
            row=1, column=1, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ## Row 2
        tk.Label(
            app_frame, text='Output size (0=auto):'
        ).grid(row=2, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        spinbox_width = app_frame.spinbox_width = tk.Spinbox(
            app_frame, from_=0, to_=10, increment=1, justify=tk.CENTER, state='readonly')
        spinbox_width.grid(
            row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        spinbox_height = app_frame.spinbox_height = tk.Spinbox(
            app_frame, from_=0, to_=10, increment=1, justify=tk.CENTER, state='readonly')
        spinbox_height.grid(
            row=2, column=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ## Row 3
        label_img_info = self.label_img_info = tk.Label(
            app_frame, text='No image loaded', height=4, relief=tk.GROOVE, anchor=tk.NW)
        label_img_info.grid(row=3, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)



if __name__ == '__main__':
    app = App()
    app.mainloop()