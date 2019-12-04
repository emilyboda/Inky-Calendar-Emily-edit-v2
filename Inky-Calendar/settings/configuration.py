#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Advanced configuration options for Inky-Calendar software.
Contains some useful functions for correctly rendering text,
calibrating (E-Paper display), checking internet connectivity

Copyright by aceisace
"""
from PIL import Image, ImageDraw, ImageFont, ImageColor
import numpy
from urllib.request import urlopen
from settings import language
from pytz import timezone
import os
from glob import glob

"""Set the image background colour and text colour"""
background_colour = 'white'
text_colour = 'black'

"""Set the display height and width (in pixels)"""
display_height, display_width = 640, 384

"""Create 3 sections of the display, based on percentage"""
top_section_width = middle_section_width = bottom_section_width = display_width

top_section_height = int(display_height*0.11)
middle_section_height = int(display_height*0.65)
bottom_section_height = int(display_height - middle_section_height -
                            top_section_height)

"""Find out the y-axis position of each section"""
top_section_offset = 0
middle_section_offset = top_section_height
bottom_section_offset = display_height - bottom_section_height

"""Get the relative path of the Inky-Calendar folder"""
path = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
if path != "" and path[-1] != "/":
  path += "/"
while not path.endswith('/Inky-Calendar/'):
  path = ''.join(list(path)[:-1])

"""Select path for saving temporary image files"""
image_path = path + 'images/'

"""Fonts handling"""
fontpath = path+'fonts/'
NotoSansCJK = fontpath+'NotoSansCJK/NotoSansCJKsc-'
NotoSans = fontpath+'NotoSans/NotoSans-SemiCondensed'
weatherfont = fontpath+'WeatherFont/weathericons-regular-webfont.ttf'

"""Automatically select correct fonts to support set language"""
if language in ['ja','zh','zh_tw','ko']:
  default = ImageFont.truetype(NotoSansCJK+'Light.otf', 18)
  semi = ImageFont.truetype(NotoSansCJK+'DemiLight.otf', 18)
  bold = ImageFont.truetype(NotoSansCJK+'Regular.otf', 18)
  month_font = ImageFont.truetype(NotoSansCJK+'DemiLight.otf', 40)
else:
  default = ImageFont.truetype(NotoSans+'Light.ttf', 18)
  semi = ImageFont.truetype(NotoSans+'.ttf', 18)
  bold = ImageFont.truetype(NotoSans+'Medium.ttf', 18)
  month_font = ImageFont.truetype(NotoSans+'Light.ttf', 40)

w_font = ImageFont.truetype(weatherfont, 10)

"""Create image with given parameters"""
image = Image.new('RGB', (display_width, display_height), background_colour)
draw = ImageDraw.Draw(image)

"""Custom function to add text on an image"""
def write_text(space_width, space_height, text, tuple,
  font=default, alignment='middle', autofit = False, fill_width = 1.0,
  fill_height = 0.8, text_colour = text_colour, rotation = None):

  if autofit == True or fill_width != 1.0 or fill_height != 0.8:
    size = 8
    font = ImageFont.truetype(font.path, size)
    text_width, text_height = font.getsize(text)
    while text_width < int(space_width * fill_width) and text_height < int(space_height * fill_height):
      size += 1
      font = ImageFont.truetype(font.path, size)
      text_width, text_height = font.getsize(text)

  text_width, text_height = font.getsize(text)

  while (text_width, text_height) > (space_width, space_height):
    text=text[0:-1]
    text_width, text_height = font.getsize(text)
  if alignment is "" or "middle" or None:
    x = int((space_width / 2) - (text_width / 2))
  if alignment is 'left':
    x = 0
  if font != w_font:
    y = int((space_height / 2) - (text_height / 1.7))
  else:
    y = y = int((space_height / 2) - (text_height / 2))

  space = Image.new('RGBA', (space_width, space_height))
  ImageDraw.Draw(space).text((x, y), text, fill=text_colour, font=font)
  if rotation != None:
    space.rotate(rotation, expand = True)
  image.paste(space, tuple, space)



def text_wrap(text, font=default, line_width = display_width):
  """Split long text into smaller lists"""
  counter, padding = 0, 40
  lines = []
  if font.getsize(text)[0] < line_width:
    lines.append(text)
  else:
    for i in range(1, len(text.split())+1):
      line = ' '.join(text.split()[counter:i])
      if not font.getsize(line)[0] < line_width - padding:
        lines.append(line)
        line, counter = '', i
      if i == len(text.split()) and line != '':
        lines.append(line)
  return lines


def draw_square(tuple, radius, width, height, colour=text_colour, line_width=1):
  """Draws a square with round corners at position (x,y) from tuple"""
  x, y, diameter = tuple[0], tuple[1],  radius*2
  line_length = width - diameter
  
  p1, p2 = (x+radius, y), (x+radius+line_length, y)  
  p3, p4 = (x+width, y+radius), (x+width, y+radius+line_length)
  p5, p6 = (p2[0], y+height), (p1[0], y+height)
  p7, p8  = (x, p4[1]), (x,p3[1])
  c1, c2 = (x,y), (x+diameter, y+diameter)
  c3, c4 = ((x+width)-diameter, y), (x+width, y+diameter)
  c5, c6 = ((x+width)-diameter, (y+height)-diameter), (x+width, y+height)
  c7, c8 = (x, (y+height)-diameter), (x+diameter, y+height)
  
  draw.line( (p1, p2) , fill=colour, width = line_width)
  draw.line( (p3, p4) , fill=colour, width = line_width)
  draw.line( (p5, p6) , fill=colour, width = line_width)
  draw.line( (p7, p8) , fill=colour, width = line_width)
  draw.arc(  (c1, c2) , 180, 270, fill=colour, width=line_width)
  draw.arc(  (c3, c4) , 270, 360, fill=colour, width=line_width)
  draw.arc(  (c5, c6) , 0, 90, fill=colour, width=line_width)
  draw.arc(  (c7, c8) , 90, 180, fill=colour, width=line_width)

def internet_available():
  """check if the internet is available"""
  try:
    urlopen('https://google.com',timeout=5)
    return True
  except URLError as err:
    return False


def get_tz():
  """Get the system timezone"""
  with open('/etc/timezone','r') as file:
    lines = file.readlines()
    system_tz = lines[0].rstrip()
    local_tz = timezone(system_tz)
  return local_tz

def fix_ical(ical_url):
  """Use iCalendars in compatability mode (without alarms)"""
  ical = str(urlopen(ical_url).read().decode())
  beginAlarmIndex = 0
  while beginAlarmIndex >= 0:
    beginAlarmIndex = ical.find('BEGIN:VALARM')
    if beginAlarmIndex >= 0:
      endAlarmIndex = ical.find('END:VALARM')
      ical = ical[:beginAlarmIndex] + ical[endAlarmIndex+12:]
  return ical

def image_cleanup():
  """Delete all files in the image folder"""
  print('Cleanup of previous images...', end = '')
  for temp_files in glob(image_path+'*'):
      os.remove(temp_files)
  print('Done')
