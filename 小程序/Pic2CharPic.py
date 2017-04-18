#!/usr/bin/env python
#-*- coding:utf-8 -*-
from PIL import Image

"""
功能：
将图片转换为字符画

rgb 转灰度值公式：
gray = 0.2126 * r + 0.7152 * g + 0.0722 * b
"""


ascii_char = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")


def get_char(r,g,b,alpha = 256):
    """
    将rgb映射到字符
    """
    if alpha == 0:
        return ' '
    length = len(ascii_char)
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
    unit = (256.0 + 1)/length
    
    return ascii_char[int(gray/unit)]


def parseimg(img, width, height, file):
    """
    将图片转换为字符画
    """
    im = Image.open(img)
    im = im.resize((width,height), Image.NEAREST)
    txt = ""

    for i in range(height):
        for j in range(width):
            txt += get_char(*im.getpixel((j,i)))
        txt += '\n'
    
    with open(file,'w') as f:
        f.write(txt)



