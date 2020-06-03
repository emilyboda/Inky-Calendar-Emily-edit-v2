#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Locations module for Inky-Calendar software.
Copyright by aceisace
"""
from __future__ import print_function
from configuration import *
try:
    from locationsharinglib import Service
except ModuleNotFoundError:
    raise Exception ('requirement is not installed. Please install with: pip3 install locationsharinglib')
try:
    import reverse_geocoder as rg
except ModuleNotFoundError:
    raise Exception ('requirement is not installed. Please install with: pip3 install reverse_geocoder && sudo apt-get install libatlas-base-dev')

service = Service(cookies_file=location_cookies_file, authenticating_account=location_google_email)


"""Get location info from everyone who has shared their location with you"""
people_found = []
for p in service.get_all_people():
    found = {}
    found['full_name'] = p.full_name
    # this also returns your location, but your name is your email address, so I've reformatted this
    if p.full_name == location_google_email:
        found['nickname'] = location_my_name
    else:
        found['nickname'] = p.nickname
    
    """Get city/state name from coordinates"""
    search = rg.search((p.latitude, p.longitude))
    display_text = found['nickname']+": "
    """Use the format set in the settings file"""
    for option in range(len(location_options)):
        if option == 0:
            display_text = display_text + search[0][location_options[option]]
        else:
            display_text = display_text+", "+ search[0][location_options[option]]
    found['display text'] = display_text
    print(found['display text'])
    
    people_found.append(found)

"""Add a border to increase readability"""
border_top = int(bottom_section_height * 0.05)
border_left = int(bottom_section_width * 0.02)

"""Choose font optimised for the weather section"""
font = ImageFont.truetype(NotoSans+'.ttf', rss_fontsize)
space_between_lines = 1
line_height = font.getsize('hg')[1] + space_between_lines
line_width = bottom_section_width - (border_left*2)

"""Find out how many lines can fit at max in the bottom section"""
# max_lines = (bottom_section_height - (border_top*2)) // (font.getsize('hg')[1]
  # + space_between_lines)
max_lines = 7
"""Calculate the height padding so the lines look centralised"""
y_padding = int( (bottom_section_height % line_height) / 2 )

"""Create a list containing positions of each line"""
line_positions = [(border_left, bottom_section_offset +
  border_top + y_padding + _*line_height ) for _ in range(max_lines)]

def generate_image():
  if bottom_section == "inkycal_locations" and people_found != [] and internet_available() == True:
    try:
      clear_image('bottom_section')
      print('Locations module: Connectivity check passed. Generating image...',
            end = '')

      """Check the lenght of each feed. Wrap the text if it doesn't fit on one line"""
      flatten = lambda z: [x for y in z for x in y]
      filtered_feeds = []
      #filtered_feeds.append(text_wrap(location_title, font = font, line_width = line_width))
      for person in people_found:
        wrapped = text_wrap(person['display text'], font = font, line_width = line_width)
        filtered_feeds.append(wrapped)
      filtered_feeds.insert(0,text_wrap('SHARED LOCATIONS', font = font, line_width = line_width))
      filtered_feeds = flatten(filtered_feeds)
      
      #print(filtered_feeds)
      
      """Write the correctly formatted text on the display"""
      for _ in range(len(filtered_feeds)):
        write_text(line_width, line_height, filtered_feeds[_],
          line_positions[_], font = font, alignment= 'left')

      location_image = crop_image(image, 'bottom_section')
      location_image.save(image_path+'inkycal_locations.png')
      
      if three_colour_support == True:
        location_image_col = crop_image(image_col, 'bottom_section')
        location_image_col.save(image_path+'inkycal_locations_col.png')

      print('Done')

    except Exception as e:
      """If something went wrong, print a Error message on the Terminal"""
      print('Failed!')
      print('Error in Locations module!')
      print('Reason: ',e)
      clear_image('bottom_section')
      write_text(bottom_section_width, bottom_section_height, str(e),
                 (0, bottom_section_offset), font = font)
      location = crop_image(image, 'bottom_section')
      location.save(image_path+'inkycal_locations.png')
      pass


def main():
  generate_image()

main()
