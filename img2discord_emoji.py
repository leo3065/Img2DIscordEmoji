import argparse

from fractions import Fraction
from pathlib import Path
import os

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'in_file',
        help='the image to be converted')
    parser.add_argument(
        'out_file',
        help='the base name of the output files')
    parser.add_argument(
        '-b', '--keep_boarder', action='store_true',
        help='keep the transperent boarder')
    parser.add_argument(
        '-t', '--tile_count', type=int, default=1, 
        help='the max amount of tiles on the shorter side, default to 1')
    args = parser.parse_args()
    
    #print(args)
    main(args.in_file, args.out_file, args.keep_boarder, args.tile_count)