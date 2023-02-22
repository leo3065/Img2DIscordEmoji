from fractions import Fraction
from pathlib import Path
import os
import tkinter as tk
import tkinter.filedialog as tkFileDialog

from PIL import Image

from typing import Tuple


def get_tile_size(aspect_ratio: float, tile_size: Tuple[int, int]) -> Tuple[int, int]:
    if tile_size == (0, 0):
        if aspect_ratio > 1:
            return (round(aspect_ratio), 1)
        else:
            return (1, round(1/aspect_ratio))
    elif tile_size[0] == 0:
        return (round(aspect_ratio*tile_size[1]), tile_size[1])
    elif tile_size[1] == 0:
        return (tile_size[0], round(aspect_ratio*tile_size[0]))
    else:
        return tile_size


def main(
        in_filename: str, out_filename: str,
        keep_boarder: bool = False, max_tile_size: int = 1):
    

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
        app_frame = self.app_frame = tk.Frame(self)
        app_frame.grid(row=0, column=0, padx=5, pady=5)
        
        ## Row 0
        button_select_image = app_frame.button_select_image = tk.Button(
            app_frame, text='Select image', command=self.load_image)
        button_select_image.grid(
            row=0, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        
        var_keep_boarder = app_frame.var_keep_boarder = tk.IntVar()
        checkbutton_keep_boarder = app_frame.checkbutton_keep_boarder = tk.Checkbutton(
            app_frame, text='Keep transparent border', variable=var_keep_boarder, anchor=tk.NW)
        checkbutton_keep_boarder.grid(
            row=0, column=1, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ## Row 1
        tk.Label(
            app_frame, text='Output size (0=auto):'
        ).grid(row=1, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        
        spinbox_width = app_frame.spinbox_width = tk.Spinbox(
            app_frame, from_=0, to_=10, increment=1, 
            justify=tk.CENTER, state='readonly', width=5)
        spinbox_width.grid(
            row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        spinbox_height = app_frame.spinbox_height = tk.Spinbox(
            app_frame, from_=0, to_=10, increment=1, 
            justify=tk.CENTER, state='readonly', width=5)
        spinbox_height.grid(
            row=1, column=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ## Row 2
        label_img_info = app_frame.label_img_info = tk.Label(
            app_frame, text='No image loaded', height=6, relief=tk.GROOVE, anchor=tk.NW, justify=tk.LEFT)
        label_img_info.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ## Row 3
        button_convert = app_frame.button_convert = tk.Button(
            app_frame, text='Convert', state=tk.DISABLED)
        button_convert.grid(
            row=3, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
    
    def load_image(self):
        in_filename = tkFileDialog.askopenfilename(
            initialdir=os.getcwd(),
            filetypes=[('Image', '.png .jpg .jpeg .gif')])
        if not in_filename:
            return
        
        app_frame = self.app_frame
        
        image = self.image = Image.open(in_filename).convert('RGBA')
        self.update_image_info()
        
        app_frame.button_convert.config(state=tk.ACTIVE)
    
    def update_image_info(self):
        if not self.image:
            return
        app_frame = self.app_frame
        
        info_lines = []
        
        image = self.image
        info_lines.append(f'Image dimension: {image.size[0]} x {image.size[1]}')
        if not app_frame.var_keep_boarder.get():
            if bbox := image.getbbox():
                image = image.crop(bbox)
                info_lines.append(f'After removing border: {image.size[0]} x {image.size[1]}')
        
        aspect_ratio = image.size[0]/image.size[1]
        info_lines.append(f'Aspect ratio: {aspect_ratio:.4f} (1/{1/aspect_ratio:.4f})')
        
        tile_width = int(app_frame.spinbox_width.get())
        tile_height = int(app_frame.spinbox_height.get())
        tile_width, tile_height = get_tile_size(aspect_ratio, (tile_width, tile_height))
        info_lines.append(f'Output size: {tile_width} x {tile_height} = {tile_width*tile_height}')
        
        app_frame.label_img_info.config(text='\n'.join(info_lines))


if __name__ == '__main__':
    app = App()
    app.mainloop()