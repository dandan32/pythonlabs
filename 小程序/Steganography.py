#!/usr/bin/env python
# coding=utf-8
# author:dandan<pipidingdingting@163.com>
from PIL import Image

"""
功能：
1. 存储文本到图像中
    原理
    1. 将文本转化为二进制表示
    2. 将图片每个像素字节的最后一位变为0，(r,g,b) 颜色附近的颜色相差不大
    3. 按序将二进制表示的文本写入到图片像素的最后一位中
2. 提取图像中的文字
    原理
    1. 提取图像中每个字节最后一位的组成二进制表示的序列。
    2. 删掉尾部多余数据
    3. 翻译二进制文本



现在支持的mode有:
    1.RGB
    2.RGBA

注意:
    不能用jpg保存图片
    jpg是有损压缩存储方式
    要用png等无损方式存储（png是无损压缩）
"""
def string2binary(data):
    """
    make string to binary code
    :param string:
    :return:
    """
    binary = ''.join(map(constLenBin, bytearray(data, 'utf-8')))
    return binary


def constLenBin(ibyte):
    """
    make the byte to binary string form
    :param ibyte:
    :return: binary_str
    """
    # 输入的是byte字节
    # 去掉 bin() 返回的二进制字符串中的 '0b'
    # 并在左边补足 '0' 直到字符串长度为 8
    binary_str = "0" * (8 - (len(bin(ibyte)) - 2)) + bin(ibyte).replace('0b', '')
    return binary_str


def makeImageEven(image):
    """
    make every last bit of pixels to 0
    :param image:
    :return evenImage
    """
    # 图片像素值：[(r,g,b,t),(r,g,b,t)...] 或 [(r,g,b),(r,g,b)...]
    pixels = list(image.getdata());evenPixels = []
    # 更改所有值为偶数，即最后一位更改为0（移位操作）
    for pixel in pixels:
        p = list()
        for each in pixel:
            p.append(each >> 1 << 1)
        evenPixels.append(tuple(p))
    # 创建一个相同大小的图片副本
    evenImage = Image.new(image.mode, image.size)
    # 把上面的像素放入到图片副本
    evenImage.putdata(evenPixels)
    return evenImage


def encode2RGBA(evenImage, binary_str):
    encodedPixels = [
        (r + int(binary_str[index * 4 + 0]), g + int(binary_str[index * 4 + 1]), b + int(binary_str[index * 4 + 2]),
         t + int(binary_str[index * 4 + 3])) if index * 4 < len(binary_str) else (r, g, b, t) for
        index, (r, g, b, t) in enumerate(list(evenImage.getdata()))]
    return encodedPixels


def encode2RGB(evenImage,binary_str):
    encodedPixels = [
        (r + int(binary_str[index * 3 + 0]), g + int(binary_str[index * 3 + 1]), b + int(binary_str[index * 3 + 2]))
        if index * 3 < len(binary_str) else (r, g, b) for
        index, (r, g, b) in enumerate(list(evenImage.getdata()))]
    return encodedPixels


def decode2RGBA(image):
    pixels = list(image.getdata())
    binary_str = ''.join([str(int(r >> 1 << 1 != r)) + str(int(g >> 1 << 1 != g)) + str(int(b >> 1 << 1 != b)) + str(
        int(t >> 1 << 1 != t)) for (r, g, b, t) in pixels])  # 提取图片中所有最低有效位中的数据
    return binary_str


def decode2RGB(image):
    pixels = list(image.getdata())
    binary_str = ''.join([str(int(r >> 1 << 1 != r)) + str(int(g >> 1 << 1 != g)) + str(int(b >> 1 << 1 != b))
                      for (r, g, b) in pixels])  # 提取图片中所有最低有效位中的数据
    return binary_str



# 将字符转换成二进制后编进图像中

# 将数据编码进图片中
def encodeDataInImage(image, data, filename = None):
    """

    :param image:
    :param data:
    :param filename
    :return:
    """
    if not isinstance(image, Image.Image):
        image = Image.open(image)
    evenImage = makeImageEven(image)  # 获得最低有效位为 0 的图片副本
    binary_str = string2binary(data) # 将需要被隐藏的字符串转换成二进制字符串
    if len(binary_str) > len(image.tobytes()):  # 如果不可能编码全部数据， 抛出异常
        raise Exception("Error: Can't encode more than " + len(image.tobytes()) + " bits in this image. ")
    # 将 binary_str 中的二进制字符串信息编码进像素里
    if evenImage.mode == 'RGBA':
        encodedPixels = encode2RGBA(evenImage, binary_str)
    else:
        encodedPixels = encode2RGB(evenImage, binary_str)
    # 创建新图片以存放编码后的像素
    encodedImage = Image.new(evenImage.mode, evenImage.size)
    # 添加编码后的数据
    encodedImage.putdata(encodedPixels)

    if filename:
        encodedImage.save(filename)
    else:
        pass





# 从图片解码出数据
def decodeDataInImage(image):
    if not isinstance(image, Image.Image):
        image = Image.open(image)
    print(image.format)
    if image.mode =='RGBA':
        binary_str = decode2RGBA(image)
    else:
        binary_str = decode2RGB(image)
    # 找到数据截止处的索引
    locationDoubleNull = binary_str.find('0000000000000000')
    endIndex = locationDoubleNull + (
    8 - (locationDoubleNull % 8)) if locationDoubleNull % 8 != 0 else locationDoubleNull
    print(binary_str)
    data = binaryToString(binary_str[0:endIndex])
    print('abc',data)
    return data


def binaryToString(binary):
    index = 0
    string = []
    # 翻译 utf-8 变长字节编码形式
    ############################################################################
    rec = lambda x, i: x[2:8] + (rec(x[8:], i - 1) if i > 1 else '') if x else ''
    # rec = lambda x, i: x and (x[2:8] + (i > 1 and rec(x[8:], i-1) or '')) or ''
    fun = lambda x, i: x[i + 1:8] + rec(x[8:], i - 1)
    # 以上两句看起来有些难懂，将utf-8变长码的转换成二进制字符串
    ############################################################################
    while index + 1 < len(binary):
        chartype = binary[index:].index('0')
        length = chartype * 8 if chartype else 8
        string.append(chr(int(fun(binary[index:index + length], chartype), 2)))
        index += length
    return ''.join(string)




if __name__ == '__main__':
    encodeImage = encodeDataInImage(Image.open("3.jpeg"), '你好世界，Hello world!','3_e.png')
    r = decodeDataInImage(Image.open("3_e.png"))

