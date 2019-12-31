#!/usr/bin/env python3
from PIL import Image
from PIL import ImageFilter
import random
import argparse

def process_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='檔案名稱')
    parser.add_argument('-y', '--width', type=int, help='寬度', default=13)
    parser.add_argument('-x', '--height', type=int, help='高度', default=13)
    parser.add_argument('-u', '--offsetX', type=str, help='x位移', default='0')
    parser.add_argument('-l', '--offsetY', type=str, help='y位移', default='0')
    parser.add_argument('-t', '--threshold', type=int, help='黑白參數', default=-1)
    parser.add_argument('-s', action='store_true', dest='smooth', help='是否平滑化圖片')
    parser.add_argument('-o', action='store_true', dest='optimized', help='是否優化輸出函數數')
    parser.add_argument('-n', action='store_true', dest='noice', help='是否增加隨機噪音')
    parser.add_argument('-D', action='store_true', dest='debug', help='是否開啟偵錯模式')
    return parser.parse_args()

def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def alpha_to_color(image, color=(255, 255, 255)):
    """Alpha composite an RGBA Image with a specified color.

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

    if isInt(arg.offsetX):
        arg.offsetX = int(arg.offsetX)
    else:
        arg.offsetX += '+'

    if isInt(arg.offsetY):
        arg.offsetY = int(arg.offsetY)
    else:
        arg.offsetY += '+'

    fx, fy = type(arg.offsetX), type(arg.offsetY)

    img = Image.open(arg.filename)
    width, height = img.size

    # remove alpha layer
    img = img.convert('RGBA')
    img = alpha_to_color(img)
    if arg.smooth:
        # smoothify image
        img = img.filter(ImageFilter.SMOOTH_MORE)
    
    # resize image
    img = img.resize((arg.width, arg.height), Image.ANTIALIAS)
    if arg.debug:
        img.save('_resized_' + arg.filename)

    if arg.threshold < 0:
        # default binarize
        img = img.convert('1')
    else:
        # custom binarize
        img = img.convert('L')
        for x in range(arg.height):
            for y in range(arg.width):
                if img.getpixel((y, x)) > arg.threshold:
                    img.putpixel((y, x), 255)
                else:
                    img.putpixel((y, x), 0)
    if arg.debug:
        img.save('_binarized_'+arg.filename)

    p_, p = [], []
    for x in range(arg.height):
        p_.append([])
        for y in range(arg.width):
            pixel = img.getpixel((y, x))
            p_[x].append(1 if pixel == 0 else 0)
        p.append(p_[-1])


    if arg.noice:
        # add random noice
        for x in range(arg.height):
            for y in range(arg.width):
                if p_[x][y] == 0:
                    continue
                
                rchoice = random.randint(0, 3)
                if rchoice == 0 and x - 1 >= 0:
                    p[x - 1][y] = 1
                elif rchoice == 1 and x + 1 < arg.height:
                    p[x + 1][y] = 1
                elif rchoice == 2 and y - 1 >= 0:
                    p[x][y - 1] = 1
                elif rchoice == 3 and y + 1 < arg.width:
                    p[x][y + 1] = 1
        
        for x in range(arg.height):
            for y in range(arg.width):
                img.putpixel((y, x), 255 - p_[x][y] * 255)
        if arg.debug:
            img.save('_noiced_'+arg.filename)


    if not arg.optimized:
        # simply drawPixel
        for x in range(arg.height):
            for y in range(arg.width):
                if p[x][y] == 1:
                    print(f'do Screen.drawPixel({arg.offsetY}{y}, {arg.offsetX}{x});')
    else:
        # try finding maximal rectangle greedily
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
                # mark visited
                for xx in range(x, mx+1):
                    for yy in range(y, my+1):
                        p[xx][yy] = -1

                # output string
                if x == mx and y == my:
                    print(f'do Screen.drawPixel({arg.offsetY + fy(y)}, {arg.offsetX + fx(x)});')
                elif x == mx or y == my:
                    print(f'do Screen.drawLine({arg.offsetY + fy(y)}, {arg.offsetX + fx(x)}, {arg.offsetY + fy(my)}, {arg.offsetX + fx(mx)});')
                else:
                    print(f'do Screen.drawRectangle({arg.offsetY + fy(y)}, {arg.offsetX + fx(x)}, {arg.offsetY + fy(my)}, {arg.offsetX + fx(mx)});')

if __name__ == '__main__':
    main()
