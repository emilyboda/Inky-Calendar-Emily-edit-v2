#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Simple weather module for Inky-Calendar software.

The lunar phase calculation is from Sean B. Palmer, inamidst.com.
Thank You Palmer for the awesome code!

Copyright by aceisace
"""
from __future__ import print_function
import pyowm
from configuration import *
import math, decimal
dec = decimal.Decimal

"""Set the optional parameters"""
decimal_places_temperature = None

print('Initialising simple weather...', end=' ')
owm = pyowm.OWM(api_key, language=language)
print('Done')

"""Icon-code to unicode dictionary for weather-font"""
weathericons = {
  '01d': '\uf00d', '02d': '\uf002', '03d': '\uf013',
  '04d': '\uf012', '09d': '\uf01a', '10d': '\uf019',
  '11d': '\uf01e', '13d': '\uf01b', '50d': '\uf014',
  '01n': '\uf02e', '02n': '\uf013', '03n': '\uf013',
  '04n': '\uf013', '09n': '\uf037', '10n': '\uf036',
  '11n': '\uf03b', '13n': '\uf038', '50n': '\uf023'
  }

"""Add a border to increase readability"""
border_top = int(top_section_height * 0.05)
border_left = int(top_section_width * 0.02)

"""Calculate size for each weather sub-section"""
row_height = (top_section_height-(border_top*2)) // 2
coloumn_width = (top_section_width-(border_left*2)) // 3
side_section_width = (top_section_width-(border_left*2)) // 4
middle_section_width = (top_section_width-(border_left*2)) // 2

"""Calculate paddings"""
x_padding = int( (top_section_width % coloumn_width) / 2 )
y_padding = int( (top_section_height % row_height) / 2 )

"""Allocate sizes for weather icons"""
icon_small = int(row_height*0.8)
icon_medium = row_height * 2
icon_medium_corr = -10
icon_medium_left_corr = int((side_section_width-icon_medium)/2)

"""Calculate the x-axis position of each coloumn"""
coloumn1 = x_padding
coloumn2 = coloumn1 + side_section_width
coloumn3 = coloumn2 + middle_section_width

"""Calculate the y-axis position of each row"""
row1 = y_padding
row2 = row1 + row_height

"""Allocate positions for current weather details"""
weather_icon_now_pos = (coloumn1+icon_medium_left_corr, row1+icon_medium_corr)
temperature_now_pos = (coloumn2, row1)
temperature_now_line1_pos = (coloumn2, row1)

sunrise_icon_now_pos = (coloumn3, row1)
sunrise_time_now_pos = (coloumn3+icon_small, row1)
sunset_icon_now_pos = (coloumn3, row2)
sunset_time_now_pos = (coloumn3+icon_small, row2)

def to_units(kelvin):
  """Function to convert tempertures from kelvin to celcius or fahrenheit"""
  degrees_celsius = round(kelvin - 273.15, ndigits = decimal_places_temperature)
  fahrenheit = round((kelvin - 273.15) * 9/5 + 32,
                     ndigits = decimal_places_temperature)
  if units == 'metric':
    conversion = str(degrees_celsius) + '°C'

  if units == 'imperial':
    conversion = str(fahrenheit) + '°F'

  return conversion

def red_temp(negative_temperature):
  if three_colour_support == True and negative_temperature[0] == '-' and units == 'metric':
    colour = 'red'
  else:
    colour = 'black'
  return colour

"""Function to convert time objects to specified format 12/24 hours"""
"""Simple means just the hour and if 12 hours, am/pm as well"""
def to_hours(datetime_object, simple = False):
  if hours == '24':
    if simple == True:
      converted_time = datetime_object.format('H') + '.00'
    else:
      converted_time = datetime_object.format('HH:mm')
  else:
    if simple == True:
      converted_time = datetime_object.format('h a')
    else:
      converted_time = datetime_object.format('h:mm a')
  return str(converted_time)

"""Choose font optimised for the weather section"""
fontsize = 7
font = ImageFont.truetype(NotoSans+'Medium.ttf', fontsize)
fill_height = 0.8
fill_width = 0.9

temp_font = ImageFont.truetype(NotoSans+'Medium.ttf', fontsize)
while temp_font.getsize("Right now it's 100ff")[0] <= (middle_section_width * fill_width):
  fontsize += 1
  temp_font = ImageFont.truetype(NotoSans+'.ttf', fontsize)
  

def generate_image():
  """Connect to Openweathermap API and fetch weather data"""
  if top_section == "inkycal_simpleweather" and api_key != "" and owm.is_API_online() is True:
    try:
      clear_image('top_section')
      print('Simple weather module: Connectivity check passed, Generating image...',
        end = '')
      current_weather_setup = owm.weather_at_place(location)
      weather = current_weather_setup.get_weather()
      
      """Get temperatures and icons"""
      temperature_now = "Right now it's "+to_units(weather.get_temperature()['temp'])
      weather_icon_now = weather.get_weather_icon_name()
      sunrise_time_now = arrow.get(weather.get_sunrise_time()).to(get_tz())
      sunset_time_now = arrow.get(weather.get_sunset_time()).to(get_tz())
      
      """WRITE"""
      write_text(icon_medium, icon_medium, weathericons[weather_icon_now],      # weather icon
        weather_icon_now_pos, font = w_font, fill_width = 0.9)
      write_text(middle_section_width, row_height*2, temperature_now,           # temp line
        temperature_now_pos, font = temp_font, colour= red_temp(temperature_now))
      write_text(icon_small, icon_small, '\uf051', sunrise_icon_now_pos,        # sunrise icon
        font = w_font, fill_height = 0.9)
      write_text(icon_small, icon_small, '\uf052', sunset_icon_now_pos,         # sunset icon
        font = w_font, fill_height = 0.9)
      write_text(side_section_width-icon_small, row_height,                     # sunrise number
        to_hours(sunrise_time_now), sunrise_time_now_pos, font = font,
                 fill_width = 0.9)
      write_text(side_section_width-icon_small, row_height,                     # sunset number
        to_hours(sunset_time_now), sunset_time_now_pos, font = font,
                 fill_width = 0.9)

      """Add vertical lines between forecast sections"""
      draw = ImageDraw.Draw(image)
      
      # line_start_y = int(top_section_height*0.1)
      # line_end_y = int(top_section_height*0.9)
      # draw.line((coloumn2, line_start_y, coloumn2, line_end_y), fill='black')
      # draw.line((coloumn3, line_start_y, coloumn3, line_end_y), fill='black')

      if three_colour_support == True:
        draw_col.line((0, top_section_height-border_top, top_section_width-
        border_left, top_section_height-border_top), fill='black', width=3)
      else:
        draw.line((0, top_section_height-border_top, top_section_width-
        border_left, top_section_height-border_top), fill='black', width=3)

      weather_image = crop_image(image, 'top_section')  
      weather_image.save(image_path+'inkycal_simpleweather.png')
      
      if three_colour_support == True:
        weather_image_col = crop_image(image_col, 'top_section')  
        weather_image_col.save(image_path+'inkycal_simpleweather_col.png')
      print('Done')

    except Exception as e:
      """If something went wrong, print a Error message on the Terminal"""
      print('Failed!')
      print('Error in simple weather module!')
      print('Reason: ',e)
      clear_image('top_section')
      write_text(top_section_width, top_section_height, str(e),
                 (0, 0), font = font)
      weather_image = crop_image(image, 'top_section')
      weather_image.save(image_path+'inkycal_simpleweather.png')
      pass

def main():
  generate_image()

main()
