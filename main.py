import streamlit as st
import pandas as pd
from moviepy.editor import VideoFileClip
import moviepy.editor
from pyunpack import Archive
import requests
import PIL

import re
import glob
import shutil, time
import os
from tqdm import tqdm as tbar
from PIL import Image, ImageFont, ImageOps, ImageDraw
import easygui
from tkinter import Tk
import tkinter as tk
from shutil import copyfile
import streamlit as st
import streamlit.components.v1 as stc

global directory_path
global images_save_type
global file_padding
global FIXED_NEW_WIDTH
FIXED_NEW_WIDTH = 200
global target_directory
global current_list
directory_path = os.path.dirname(os.path.realpath(__file__))
st.write("Running in", directory_path)
st.title("Ascii Video Tools")
menu = ["Single Image","Video To Ascii Video"]
mode = st.sidebar.selectbox("Menu",menu)

def create_check(target):
    if not target in os.listdir():
        os.mkdir(target)
def string_image(string, font_path=None):

    lines = string.split('\n')

    # Choosing font
    large_font = 100  # get better resolution with larger size
    font_path = font_path or 'fonts/Courier.dfont'
    try:
        font = ImageFont.truetype(font_path, size=large_font)
    except IOError:
        font = ImageFont.load_default()
        print('Chosen font could not bed used. Using default font.')

    # make the background image based on the combination of font and lines
    # convert points to pixels
    def pt2px(pt): return int(round(pt * 96.0 / 72))
    max_width_line = max(lines, key=lambda s: font.getsize(s)[0])
    # max height is adjusted down because it's too large visually for spacing
    test_string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    max_height = pt2px(font.getsize(test_string)[1])
    max_width = pt2px(font.getsize(max_width_line)[0])
    height = max_height * len(lines)  # perfect or a little oversized
    width = int(round(max_width + 40))  # a little oversized
    image = Image.new(GRAYSCALE, (width, height), color=PIXEL_OFF)
    draw = ImageDraw.Draw(image)

    # draw each line of text
    vertical_position = 5
    horizontal_position = 5
    # reduced spacing seems better
    line_spacing = int(round(max_height * 0.65))
    for line in lines:
        draw.text((horizontal_position, vertical_position),
                  line, fill=PIXEL_ON, font=font)
        vertical_position += line_spacing

    # crop the text
    c_box = ImageOps.invert(image).getbbox()
    image = image.crop(c_box)
    return image


#delete_check_list_file = ["clip_audio.mp3","output.mp4","ffmpeg_compile_log.txt","output_with_audio.mp4","ffmpeg.7z"]
#delete_check_list_path = ["\\output","\\data","\\ffmpeg","\\ffmpeg_initial","\\fonts","\\iteration","\\Input"]


    # gets up to date list of files in directory
def delete_images_in_folder(target):
    delete_list = []
    current_list = os.listdir(directory_path + "\\" +target)
    for i in current_list:  # for each file in current_list it checks to see if the file is .jpg and if it is it adds it to new_list
        if i.endswith((".jpg", ".png")):
            delete_list.append(i)
    if not delete_list == []:
        for i in delete_list:
            os.remove(directory_path + "\\"+ target + "\\" + i)



def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    def convert(text): return int(text) if text.isdigit() else text
    def alphanum_key(key): return [convert(c)
                                   for c in re.split('([0-9]+)', key)]
    l.sort(key=alphanum_key)


def pixels_to_image_array(ascii_pixels, width):
    ''' Unflattening the array
    * range(0, len(pixels), width)
        - Create a sequence of numbers from 0 to length of pixels
        - but increment by the width instead of 1.
    * pixels[i:i+width]
        - This creates the row of the matrix
    '''
    return [ascii_pixels[i: i + width] for i in range(0, len(ascii_pixels), width)]


def image_array_to_string(image):
    return '\n'.join(image)


def asciify_pixels(image, groups=25):
    pixels = list(image.getdata())
    ascii_pixels = [ASCII_CHARS[pixel_intensity//groups]
                    for pixel_intensity in pixels]
    return ''.join(ascii_pixels)


def convert_to_grayscale(image):
    return image.convert(GRAYSCALE)


def resize(image, new_width):
    initial_width, initial_height = image.size
    aspect_ratio = float(initial_height)/float(initial_width)
    new_height = int(aspect_ratio * new_width)
    return image.resize((new_width, new_height))


def apply_magic(image,FIXED_NEW_WIDTH):
    resized_image = resize(image,FIXED_NEW_WIDTH)
    grayscale_image = convert_to_grayscale(resized_image)
    ascii_pixels = asciify_pixels(grayscale_image)
    final_image = pixels_to_image_array(ascii_pixels, resized_image.width)
    return image_array_to_string(final_image)

def font_get():
    if not os.path.exists(directory_path + "\\fonts") or os.stat(directory_path + "\\fonts").st_size == 0:
        if not os.path.exists(directory_path + "\\fonts"):
            os.mkdir(directory_path + "\\fonts")  # creates directory
    response = requests.get(
        "https://github.com/KhorSL/ASCII-ART/raw/master/fonts/Courier%20New.ttf")
    font_file = open("fonts\\Courier New.ttf", "wb")
    font_file.write(response.content)
    font_file.close()

def load_image(image_file):
    img = Image.open(image_file)
    return img

if mode == "Single Image":
    PIL.Image.MAX_IMAGE_PIXELS = ((FIXED_NEW_WIDTH * FIXED_NEW_WIDTH) * (FIXED_NEW_WIDTH * FIXED_NEW_WIDTH)) * ((FIXED_NEW_WIDTH * FIXED_NEW_WIDTH) * (FIXED_NEW_WIDTH * FIXED_NEW_WIDTH))
    
    ASCII_CHARS = ['@', '#', '8', '&', 'o', ':', '*', '+', ',', '.', ' ']
    IMAGE_PATH = 1
    GRAYSCALE = 'L'
    PIXEL_ON = 0
    PIXEL_OFF = 255
    DEFAULT_FONT_PATH = 'fonts/Courier New.ttf'
    font_get()
    create_check("input")
    uploaded_file= st.file_uploader("Upload Image To Be Converted", type=["png","jpg","jpeg"])
    if not uploaded_file == None:
        st.image(load_image(uploaded_file))
        with open(os.path.join("input",uploaded_file.name),"wb") as f:
            f.write(uploaded_file.getbuffer())
        image = Image.open(directory_path + ("\\input\\"+ os.listdir("input")[0]))
        FIXED_NEW_WIDTH = int(st.slider("Definition of Image: The bigger the number the more detailed the image will be, It will also take longer to calculate.",min_value=100,max_value=1000,step=50))
        if st.button("Submit"):
            final_image = apply_magic(image,FIXED_NEW_WIDTH)
            image = string_image(final_image, DEFAULT_FONT_PATH)
            create_check("output")
            image.save(directory_path + "\\output\\" + os.listdir("input")[0])
            if os.stat(directory_path + "\\output").st_size == 0:
                st.image(load_image(directory_path + "\\output\\"+ os.listdir("output")[0]))
                with open((directory_path + "\\output\\"+ os.listdir("output")[0]), "rb") as file:
                    btn = st.download_button(
                    label="Download image",
                    data=file,
                    file_name= os.listdir("output")[0],
                    mime="image/png"
                )
