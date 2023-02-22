from pathlib import Path
import os
import tkinter as tk
import tkinter.filedialog as tkFileDialog

from PIL import Image

from typing import Tuple


def get_tile_size(aspect_ratio: float, tile_size: Tuple[int, int]) -> Tuple[int, int]:
    if tile_size == (0, 0):
        if aspect_ratio > 1:
            return (max(1, round(aspect_ratio)), 1)
        else:
            return (1, max(1, round(1/aspect_ratio)))
    elif tile_size[0] == 0:
        return (max(1, round(tile_size[1]*aspect_ratio)), tile_size[1])
    elif tile_size[1] == 0:
        return (tile_size[0], max(1, round(tile_size[0]/aspect_ratio)))
    else:
        return tile_size


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
            app_frame, text='Keep transparent border', anchor=tk.NW,
            variable=var_keep_boarder, command=self.update_image_info)
        checkbutton_keep_boarder.grid(
            row=0, column=1, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ## Row 1
        tk.Label(
            app_frame, text='Output size (0=auto):'
        ).grid(row=1, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        
        spinbox_width = app_frame.spinbox_width = tk.Spinbox(
            app_frame, from_=0, to_=10, increment=1, 
            justify=tk.CENTER, state='readonly', width=5, 
            command=self.update_image_info)
        spinbox_width.grid(
            row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        spinbox_height = app_frame.spinbox_height = tk.Spinbox(
            app_frame, from_=0, to_=10, increment=1, 
            justify=tk.CENTER, state='readonly', width=5, 
            command=self.update_image_info)
        spinbox_height.grid(
            row=1, column=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ## Row 2
        tk.Label(app_frame, text='Output name:').grid(
            row=2, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        entry_output_name = app_frame.entry_output_name = tk.Entry(
            app_frame)
        entry_output_name.grid(
            row=2, column=1, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ## Row 3
        label_img_info = app_frame.label_img_info = tk.Label(
            app_frame, text='No image loaded', height=8, relief=tk.GROOVE, anchor=tk.NW, justify=tk.LEFT)
        label_img_info.grid(row=3, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ## Row 4
        button_convert = app_frame.button_convert = tk.Button(
            app_frame, text='Convert', state=tk.DISABLED, command=self.covert_image)
        button_convert.grid(
            row=4, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
    
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
    
    def covert_image(self):
        if not self.image:
            return
        app_frame = self.app_frame
        
        out_dir = tkFileDialog.askdirectory(
            initialdir=os.getcwd())
        if not out_dir:
            return
        out_dir = Path(out_dir)
        
        info_lines = app_frame.label_img_info.cget('text').split('\n')
        
        image = self.image
        if not app_frame.var_keep_boarder.get():
            if bbox := image.getbbox():
                image = image.crop(bbox)
        
        aspect_ratio = image.size[0]/image.size[1]
        tile_width = int(app_frame.spinbox_width.get())
        tile_height = int(app_frame.spinbox_height.get())
        tile_width, tile_height = get_tile_size(aspect_ratio, (tile_width, tile_height))
        
        ## fitting to tiles
        tile_unit = 128
        image.thumbnail((tile_width*tile_unit, tile_height*tile_unit))
        image_final = Image.new('RGBA', (tile_width*tile_unit, tile_height*tile_unit))
        
        ## aligning to center
        left = (image_final.size[0] - image.size[0])//2
        top = (image_final.size[1] - image.size[1])//2
        image_final.paste(image, (left, top))
        
        ## tile cropping
        base_name = app_frame.entry_output_name.get()
        filenames = []
        empty_count = 0
        for j in range(tile_height):
            for i in range(tile_width):
                tile = image_final.crop((
                    i*tile_unit, j*tile_unit, 
                    (i+1)*tile_unit, (j+1)*tile_unit))
                
                filename_parts = []
                if base_name:
                    filename_parts.append(base_name)
                
                # detemine if the tile is empty
                is_empty = tile.getbbox() is None
                if not is_empty:
                    if tile_height>1:
                        filename_parts.append(f'{j+1}')
                    if tile_width>1:
                        filename_parts.append(f'{i+1}')
                else: 
                    # if the tile is empty, change the tile name
                    filename_parts.append('empty')
                    empty_count += 1
                if not filename_parts:
                    filename_parts.append('output')
                
                if not is_empty or empty_count<=1:
                    filename = '_'.join(filename_parts) + '.png'
                    with open(out_dir / filename, 'wb') as f:
                        tile.save(f, format='png')
                    filenames.append(filename)
        
        info_lines.append(f'Complete! Tile count: {tile_width*tile_height}')
        info_lines.append(f'Non-empty tile count: {tile_width*tile_height - empty_count}')
        info_lines.append(f'Empty tile count: {empty_count}')
        app_frame.label_img_info.config(text='\n'.join(info_lines))


if __name__ == '__main__':
    app = App()
    app.mainloop()