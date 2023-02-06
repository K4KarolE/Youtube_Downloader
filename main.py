'''
ffmpeg

- will be able to download higher than 720p + merge video-audio
- https://windowsloop.com/install-ffmpeg-windows-10/#add-ffmpeg-to-Windows-path
'''
# test link: https://youtu.be/7AwWEU5nsBA
 
import sys
import os
import webbrowser
import pyperclip

from pathlib import Path

from tkinter import *
from tkinter import filedialog      # for browse window (adding path)
import tkinter.messagebox           # for pop-up windows
from PIL import Image,ImageTk       # PILLOW import has to be after the tkinter impoert (Image.open will not work: 'Image has no attributesm open')

from functions import settings
settings_data = settings.open_settings()        # access to the saved/default settings (settings_db.json)

# COLORS - FONT STYLE
# original tkinter grey: #F0F0F0 - FYI
background_color = settings_data['background_color'] 
field_background_color = settings_data['field_background_color'] 
font_style = settings_data['font_style']
font_color = settings_data['font_color']


# WINDOW
window = Tk()
window.title(settings_data['window_title'])
width = 500
length = 400
window.geometry(f'{width}x{length}')
window.resizable(0,0)   # locks the main window
window.configure(background=settings_data['background_color'])
# ICON
window.iconbitmap('./skin/icon.ico')
# RECTANGLES
canvas_color = settings_data['background_color']
canvas_frame_color = settings_data['canvas_frame_color']
canvas = Canvas(window, width=width, height=length, background = background_color)
canvas.create_rectangle(10, 10, 490, 370, outline=canvas_frame_color, fill=canvas_color) 
# canvas.create_rectangle(10, 150, 340, 390, outline=canvas_frame_color, fill=canvas_color)          # INFO
# canvas.create_rectangle(10, 150, 340, 190, outline=canvas_frame_color, fill=canvas_color)          # THUMBNAIL
canvas.create_rectangle(10, 150, 490, 390, outline=canvas_frame_color, fill=canvas_color)         # INFO - THUMBNAIL - BUTTONS
canvas.pack()

path_yt_dlp = settings_data['path_yt_dlp']      # will come from UI - browse window



### WIDGETS
## VIDEO TITLE AND DURATION - FIELD
title_field_length = 58
video_title_field = Text(window, height = 1, width = title_field_length, foreground=font_color, background="white")
video_title_field.place(x=15, y=170)


## GET URL - BUTTON
# REMOVE PREVIOUS VALUES - THUMBNAIL
def remove_pre_info():
    try:
        settings_data['video_ID'] = ""
        settings_data['video_title'] = ""
        settings_data['video_duration'] = ""
        settings.save_settings(settings_data)
        os.remove('./thumbnail/thumbnail.png')
    except:
        pass

# GET URL
def get_url():
    settings_data['video_url'] = pyperclip.paste()
    settings.save_settings(settings_data)


# # GET INFORMATION > INFO.TXT
def save_info():
    link = settings_data['video_url']
    info_path = './temp/info.txt'
    parameter = f'--get-id --get-title --get-duration --restrict-filenames --quiet'
    executable =  f'{path_yt_dlp} {parameter} {link} > {info_path}'     # writes the available formats into the txt file
    os.system(executable)

# SAVE BASIC VIDEO INFORMATION
def extract_info():
    try:
        file = open('./temp/info.txt','r+')
        listFile = list(file)
        video_ID = listFile[1].strip('\n')
        video_title = listFile[0].strip('\n')      
        video_duration = listFile[2].strip('\n')
        if ':' not in video_duration:
            video_duration = video_duration + 's'
        settings_data['video_ID'] = video_ID
        settings_data['video_title'] = video_title
        settings_data['video_duration'] = video_duration
        settings.save_settings(settings_data)
    except:
        print('ERROR - WRONG LINK')

# SAVE THUMBNAIL
def save_thumbnail():
     # FFMPEG PATH      -  settings_data['path_ffmpeg'] = "--ffmpeg-location PATH"   
    # if settings_data['path_ffmpeg'] != "":          # if ffmpeg not added to the windows path - ffmpeg path browse field is used
    #     path_ffmpeg = settings_data['path_ffmpeg']
    #     add_path_ffmpeg = f'--ffmpeg-location {path_ffmpeg}'
    # else:
    #     add_path_ffmpeg = None
    if settings_data['video_title'] != "":
        link = settings_data['video_url']
        path = 'thumbnail'
        parameter = f'--skip-download -o %(NAME)s --write-thumbnail --convert-thumbnails png --paths {path} --quiet' % {'NAME': "thumbnail"}
        executable =  f'{path_yt_dlp} {parameter} {link}'     # writes the available formats into the txt file
        os.system(executable)
    
# DISPLAY THUMBNAIL
my_img = Image.open(f"./thumbnail/thumbnail_default.png")
global img  # otherwise it will not be displayed - Garbage Collection - https://stackoverflow.com/questions/16424091/why-does-tkinter-image-not-show-up-if-created-in-a-function
img = ImageTk.PhotoImage(my_img)
Label(window, image=img, background=canvas_color).place(x=15, y=200)

def display_thumbnail():
    try:
        if settings_data['video_title'] != "":
            file_name = "thumbnail.png"
        else:
            file_name = "thumbnail_error.png"
        my_img = Image.open(f"./thumbnail/{file_name}")
        n = 4
        width = int(1280 / n)
        height = int(720 / n)
        resized_image = my_img.resize((width, height))
        global img  # otherwise it will not be displayed - Garbage Collection - https://stackoverflow.com/questions/16424091/why-does-tkinter-image-not-show-up-if-created-in-a-function
        img = ImageTk.PhotoImage(resized_image)
        Label(window, image=img, background=canvas_color).place(x=15, y=200)
    except:
        print("ERROR - Thumbnail")


# DISPLAY INFO - TITLE - DURATION
def display_info():
    def text_position(field):
        field.tag_configure("tag_name", justify='center')
        field.tag_add("tag_name", "1.0", "end")

    if settings_data['video_title'] != "":
        title_length = len(settings_data['video_title'])
        duration_length = len(settings_data['video_duration'])

        if title_length + duration_length + 7 >= 56:
            cut = 56 - duration_length - 7
            title = settings_data['video_title'][:cut] + '..  -  ' + settings_data['video_duration']
        else:
            title = settings_data['video_title'] + ' - ' + settings_data['video_duration']
       
        video_title_field.delete('1.0', END)       # once a button is clicked, removes the previous value
        video_title_field.insert(END, title)       # adding the path and the name of the selected file
        text_position(video_title_field)
       
    else:
        video_title_field.delete('1.0', END)      
        video_title_field.insert(END, "- - Sorry, something went wrong - -")
        text_position(video_title_field)


button_get_url = Button(window, text = "Get URL", command = lambda: [
    remove_pre_info(),
    get_url(),
    save_info(),
    extract_info(),
    save_thumbnail(),
    display_thumbnail(),
    display_info()
 ],foreground=font_color, background=background_color, activeforeground=background_color, activebackground=font_color)        
# no () in command = your_function() otherwise will execute it automatically before clicking the button
# binding multiple commands to the same button: command = lambda: [save_settings(), engine.start_engine()]


## SAVE AS - AUDIO / VIDEO OPTIONS + ROLL DOWN BUTTON
av_options = {
    "Audio Only": "audio only",
    "360p": "360",
    "480p": "480",
    "720p": "720",
    "1080p": "1080",
    "1440p": "1440",
    "2160p": "2160",
}

av_options_list=[]
for item in av_options.keys():
    av_options_list += [item]       # Audio Only - 2160p

av_options_roll_down_clicked = StringVar()
av_options_roll_down_clicked.set("Save as")    
av_options_roll_down = OptionMenu( window, av_options_roll_down_clicked, *av_options_list, command=None)     
av_options_roll_down.configure(foreground=font_color, background=background_color, activeforeground = font_color, activebackground=background_color, highlightbackground=background_color)
av_options_roll_down['menu'].configure(foreground=font_color, background=background_color, activebackground=background_color)

## START - BUTTON
def start():
    # AUDIO-VIDEO SELECTION CHECK
    if av_options_roll_down_clicked.get() not in av_options_list: 
        print('Select the Audio/Video option')
        return

    settings_data['av_selected'] = av_options_roll_down_clicked.get()

    settings.save_settings(settings_data)
    av_selected = av_options_roll_down_clicked.get()
    link = settings_data['video_url']
    selected_resolution = av_options[av_selected]       #av_options['720p']
    
    path = settings_data['path_target_location']
    if selected_resolution.isdecimal():                 # 360 - 2160
        parameter = f'-S "res:{selected_resolution}" --paths {path} -q --progress'   # Download the best video available with the largest resolution but no better than {selected_resolution},
    else:                                               # or the best video with the smallest resolution if there is no video under {selected_resolution}
        parameter = f'-x --audio-format mp3 --paths {path} -q --progress'             # Audio Only

    executable =  f'{path_yt_dlp} {parameter} {link}'
    os.system(executable)

button_start = Button(window, text = "START", command = start, foreground=font_color, background=background_color, activeforeground=background_color, activebackground=font_color)



### DISPLAY WIDGETS
def display_widgets():
    # BASE VALUES
    # X
    x = 350
    x_button_gap = 170
    x_gap_for_path_objects = 5
    # Y
    y_base = 130
    y_gap = 30

    
    def y_location(gap_by_number):
        display_y = y_base + y_gap * gap_by_number
        return display_y


    # GET URL - BUTTON
    button_get_url.place(x=x, y=y_location(3))

    # AUDIO / VIDEO OPTIONS - ROLL DOWN BUTTON
    av_options_roll_down.place(x=x, y=y_location(4.5))



    # START - BUTTON
    button_start.place(x=x, y=y_location(7))


display_widgets()

window.mainloop()


# SAVE AVAILABLE FORMATS
def available_formats(link):
    parameter = '-F'
    executable =  f'{path_yt_dlp} {parameter} {link} > formats.txt'     # writes the available formats into the txt file
    os.system(executable)
    print('\n')

# # UPDATE YT-DLP
# def update_yt_dlp():
#     parameter = '-U'
#     executable =  f'{path_yt_dlp} {parameter}'
#     os.system(executable)

# # OPEN YT-DLP GITHUB SITE
# def launch_yt_dlp_github():
#     link = 'https://github.com/yt-dlp/yt-dlp'

#     webbrowser.open(link)

# # SAVE AVAILABLE FORMATS > FORMATS.TXT
# def save_available_formats():
#     link = settings_data['video_url']
#     parameter = '--print formats_table'
#     executable =  f'{path_yt_dlp} {parameter} {link} > formats.txt'     # writes the available formats into the txt file
#     os.system(executable)
#     print('\n')