#!/usr/bin/env python3
from PIL import Image
import argparse

def process_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='檔案名稱')
    parser.add_argument('-y', '--width', type=int, help='寬度', default=13)
    parser.add_argument('-x', '--height', type=int, help='高度', default=13)
    parser.add_argument('-u', '--offsetX', type=str, help='x位移', default='')
    parser.add_argument('-l', '--offsetY', type=str, help='y位移', default='')
    parser.add_argument('-o', action='store_true', dest='optimized')
    return parser.parse_args()

def alpha_to_color(image, color=(255, 255, 255)):
    """Alpha composite an RGBA Image with a specified color.

    Simpler, faster version than the solutions above.

    Source: http://stackoverflow.com/a/9459208/284318

    Keyword Arguments:
    image -- PIL RGBA Image object
    color -- Tuple r, g, b (default 255, 255, 255)

    """
    image.load()  # needed for split()
    background = Image.new('RGB', image.size, color)
    background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
    return background

def main():
    arg = process_argument()
    if arg.offsetX != '':
        arg.offsetX += '+'
    if arg.offsetY != '':
        arg.offsetY += '+'
    img = Image.open(arg.filename)
    width, height = img.size
    img = img.convert('RGBA')
    img = alpha_to_color(img)
    img = img.convert('1')
    img = img.resize((arg.width, arg.height), Image.ANTIALIAS)
    img.save('_'+arg.filename)

    p = []
    for x in range(arg.height):
        p.append([])
        for y in range(arg.width):
            pixel = img.getpixel((y, x))
            p[x].append(1 if pixel == 0 else 0)
            if pixel == 0 and not arg.optimized:
                print(f'do Screen.drawPixel({arg.offsetY}{y}, {arg.offsetX}{x});')
    if arg.optimized:
        for x in range(arg.height):
            for y in range(arg.width):
                if p[x][y] == 0 or p[x][y] == -1:
                    continue
                mx, my = x, y
                for ny in range(y, arg.width):
                    if p[x][ny] == 0:
                        break
                    elif p[x][ny] == 1:
                        my = ny
                    ny += 1
                for nx in range(x, arg.height):
                    valid = True
                    has1 = False
                    for yy in range(y, my + 1):
                        if p[nx][yy] == 0:
                            valid = False
                            break
                        elif p[nx][yy] == 1:
                            has1 = True
                    if not valid:
                        break
                    if has1:
                        mx = nx
                for xx in range(x, mx+1):
                    for yy in range(y, my+1):
                        p[xx][yy] = -1
                if x == mx and y == my:
                    print(f'do Screen.drawPixel({arg.offsetY}{y}, {arg.offsetX}{x});')
                elif x == mx or y == my:
                    print(f'do Screen.drawLine({arg.offsetY}{y}, {arg.offsetX}{x}, {arg.offsetY}{my}, {arg.offsetX}{mx});')
                else:
                    print(f'do Screen.drawRectangle({arg.offsetY}{y}, {arg.offsetX}{x}, {arg.offsetY}{my}, {arg.offsetX}{mx});')

if __name__ == '__main__':
    main()
