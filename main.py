
import glob
import sys
import subprocess
import os
import pyperclip

from tkinter import *
from tkinter import filedialog      # for browse window (adding path)

from PIL import Image               # PILLOW import has to be after the tkinter import (Image.open will not work: 'Image has no attribute open')
from PIL import ImageTk

from pathlib import Path

from functions import messages
from functions import settings
settings_data = settings.open_settings()        # access to the saved/default settings (settings_db.json)
from functions import pop_up_window


# COLORS - FONT STYLE
# original tkinter grey: #F0F0F0 - FYI
background_color = settings_data['background_color'] 
field_background_color = settings_data['field_background_color'] 
font_style = settings_data['font_style']
font_size = settings_data['font_size']
font_color = settings_data['font_color']
working_directory = os.path.dirname(__file__)
os_linux: bool = sys.platform == 'linux'
valid_url: bool = False


# WINDOW
window = Tk()
window.title(settings_data['window_title'])
window_width = 447
window_length = 290
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.geometry(f'{window_width}x{window_length}+%d+%d' % (screen_width/2-275, screen_height/2-125))    #   position to the middle of the screen
window.resizable(0,0)   # locks the main window
window.configure(background=settings_data['background_color'])
# ICON
if not os_linux:
    path_icon = Path(working_directory, "skin", "icon.ico") 
    window.iconbitmap(path_icon)
# RECTANGLE
canvas_color = settings_data['background_color']
canvas_frame_color = settings_data['canvas_frame_color']
canvas = Canvas(window, width=window_width, height=window_length, background = background_color)
canvas.create_rectangle(5-1, 5+2, window_width-5, window_length-5, outline=canvas_frame_color, fill=canvas_color)
canvas.pack()
# BUTTON SIZE
button_height = 1
if os_linux:
    button_width = 7
else:
    button_width = 10
# SEARCH FIELD LENGTH
search_field_length = 40


class Buttons:
    def __init__(self, text, command):
        self.text = text
        self.command = command
    
    def create(self):
        return Button(window,
                      height=button_height,
                      width=button_width, text = self.text, 
                      command = self.command, 
                      foreground=font_color, 
                      background=background_color, 
                      activeforeground=background_color, 
                      activebackground=font_color)


class Fields:  
    def __init__(self, width, background):
        self.width = width
        self.background = background
    
    def create(self):
        return Text(window, 
                    height = 1, 
                    width = self.width, 
                    foreground=font_color, 
                    background=self.background, 
                    font=(font_style, font_size))


def get_path_yt_dlp():
    settings_data = settings.open_settings()
    path_yt_dlp = settings_data['path_yt_dlp']
    return path_yt_dlp



## WIDGETS
## SETTINGS BUTTON - POP UP WINDOW
settings_button_instance = Buttons('Settings', lambda: [pop_up_window.launch(window)])
settings_button = settings_button_instance.create()


## DESTINATION - FIELD + BROWSE BUTTON
destination_field_instance = Fields(search_field_length, "white")
destination_field = destination_field_instance.create()
destination_field.insert(END,settings_data['path_target_location'])     # loading the previously used destination folder

def browse_destination():
    dir_name = filedialog.askdirectory()
    destination_field.delete('1.0', END)       # once a button is clicked, removes the previous value
    destination_field.insert(END,dir_name)     # adding the path and the name of the selected file

destination_button_instance = Buttons("Destination", lambda : [browse_destination()])
destination_button = destination_button_instance.create()


## VIDEO TITLE AND DURATION - FIELD
title_field_length = 51
video_title_field_instance = Fields(title_field_length,background_color)
video_title_field = video_title_field_instance.create()

## GET URL - BUTTON
# REMOVE PREVIOUS VALUES - THUMBNAIL
# DISPLAY THUMBNAIL
path_thumbnail_default = Path(working_directory, "thumbnail", "thumbnail_default.png") 
my_img = Image.open(path_thumbnail_default)
img = ImageTk.PhotoImage(my_img)
thumbnail = Label(window, image=img, background=canvas_color)
thumbnail_x = settings_data['thumbnail_location_x']
thumbnail_y = settings_data['thumbnail_location_y']


def button_get_url_actions():

    settings_data = settings.open_settings()

    def remove_pre_info():
        try:
            settings_data['video_ID'] = ""
            settings_data['video_title'] = ""
            settings_data['video_duration'] = ""
            settings.save_settings(settings_data)
            path_thumbnail = Path(working_directory, "thumbnail", "thumbnail.png")
            if path_thumbnail.is_file():
                os.remove(path_thumbnail)
        except:
            print('Removing previous information failed')

    def get_url():
        clipboard_content = pyperclip.paste()
        if 'http' in clipboard_content:
            valid_url = True
            settings_data['video_url'] = clipboard_content
            settings.save_settings(settings_data)
        else:
            messages.error_pop_up('Warning', 'invalid_url_in_clipboard')
            valid_url = False
        return valid_url

    # GET INFORMATION > INFO.TXT
    def save_info():
        text_frame = "-"*20
        print(f'\n {text_frame} NEW VIDEO {text_frame}')
        print('-- Extracting information(id, title, duration) --')
        path_yt_dlp = get_path_yt_dlp()
        link = settings_data['video_url']
        info_path = Path(working_directory, "info", "info.txt") 
        parameter = "--print id --get-title --get-duration --restrict-filenames"
        executable =  f'{path_yt_dlp} {parameter} {link} > {info_path}'     # writes the available formats into the txt file
        os.system(executable)
        print("-- Extraction completed --")
    
    # SAVE INFORMATION > SETTINGS DB
    def extract_info():
        try:
            info_path = Path(working_directory, "info", "info.txt")
            file = open(info_path,'r+')
            listFile = list(file)
            video_ID = listFile[0].strip('\n')
            video_title = listFile[1].strip('\n')      
            video_duration = listFile[2].strip('\n')
            if ':' not in video_duration:
                video_duration = video_duration + 's'
            settings_data['video_ID'] = video_ID
            settings_data['video_title'] = video_title
            settings_data['video_duration'] = video_duration
            settings.save_settings(settings_data)
        except:
            pass

    def save_thumbnail():
        if settings_data['video_title'] != "":
            print("-- Saving thumbnail --")
            path_yt_dlp = get_path_yt_dlp()
            link = settings_data['video_url']
            path = Path(working_directory, "thumbnail")
            parameter = f'--skip-download -o %(NAME)s --write-thumbnail --convert-thumbnails png --paths "{path}" --quiet' % {'NAME': "thumbnail"}
            executable =  f'{path_yt_dlp} {parameter} {link}'     # writes the available formats into the txt file
            os.system(executable)
            print("-- Thumbnail saved --")
        
    def display_thumbnail():
        try:
            print("-- Displaying thumbnail --")
            if settings_data['video_title'] != "":
                file_name = "thumbnail.png"
            else:
                file_name = "thumbnail_error.png"
            my_img_path = Path(working_directory, "thumbnail", file_name) 
            my_img = Image.open(my_img_path)
            n = 4
            width = int(1280 / n)
            height = int(720 / n)
            resized_image = my_img.resize((width, height))
            global img  # otherwise it will not be displayed - Garbage Collection - https://stackoverflow.com/questions/16424091/why-does-tkinter-image-not-show-up-if-created-in-a-function
            img = ImageTk.PhotoImage(resized_image)
            Label(window, image=img, background=canvas_color).place(x=thumbnail_x, y=thumbnail_y)
        except:
            pass

    # DISPLAY INFO - TITLE - DURATION
    def display_info():
        print("-- Displaying information --")
        def text_position(field):
            field.tag_configure("tag_name", justify='center')
            field.tag_add("tag_name", "1.0", "end")

        if settings_data['video_title'] != "":
            title_length = len(settings_data['video_title'])
            duration_length = len(settings_data['video_duration'])

            if title_length + duration_length + 5 >= title_field_length:
                insert = '.. - '
                font_style_dependent_correction = -6
                cut = title_field_length - duration_length - len(insert) - font_style_dependent_correction         
                title = settings_data['video_title'][:cut] + insert + settings_data['video_duration']
            else:
                title = settings_data['video_title'] + ' - ' + settings_data['video_duration']
        
            video_title_field.delete('1.0', END)       # once a button is clicked, removes the previous value
            video_title_field.insert(END, title)       # adding the path and the name of the selected file
            text_position(video_title_field)
        
        else:
            video_title_field.delete('1.0', END)      
            video_title_field.insert(END, "- - Sorry, something went wrong - -")
            text_position(video_title_field)

    def yt_dlp_path_valuation():
        if os.path.isfile(settings_data['path_yt_dlp']):
            return True
        else:
            messages.error_pop_up('Error','no_yt_dlp')
            return False

    if yt_dlp_path_valuation():
        if get_url():
            remove_pre_info(),
            save_info(),
            extract_info(),
            save_thumbnail(),
            display_thumbnail(),
            display_info()

button_get_url_instance = Buttons("Get URL", lambda: [button_get_url_actions()])
button_get_url = button_get_url_instance.create()


## SAVE AS - AUDIO / VIDEO OPTIONS + ROLL DOWN BUTTON
av_options = {
    "MP3": "audio only",
    "360p": "360",
    "480p": "480",
    "720p": "720",
    "1080p": "1080",
    "1440p": "1440",
    "2160p": "2160",
}

av_options_list=[]
for item in av_options:
    av_options_list += [item]   # MP3 - 2160p

av_options_roll_down_clicked = StringVar()
av_options_roll_down_clicked.set("Save as")    
av_options_roll_down = OptionMenu( window, av_options_roll_down_clicked, *av_options_list, command=None)     
av_options_roll_down.configure(
    foreground=font_color,
    background=background_color,
    activeforeground = font_color,
    activebackground=background_color,
    highlightbackground=background_color)
av_options_roll_down['menu'].configure(
    foreground=font_color,
    background=background_color,
    activebackground='grey')


## START - BUTTON
def start():

    ## VALUE CHECKS - MESSAGES
    # DESTINATION FOLDER ADDED
    if not os.path.isdir(destination_field.get("1.0", "end-1c")):
        messages.error_pop_up('Error','destination_folder')
        return
    
    # TITLE FIELD - GET URL USED
    if video_title_field.get("1.0", "end-1c") == "":
        messages.error_pop_up('Error', 'no_URL')
        return

    # RESOLUTION - MP3 - SELECTION
    if av_options_roll_down_clicked.get() not in av_options_list:       # SAVE AS - DEFAULT
        messages.error_pop_up('Error', 'no_resolution')
        return
    
    # YT-DLP    - already checked with the "Get URL", why checking here too: unique scenario, YT-DLP added, rest of the req.es added(destination, URL) and YT-DLP removed before click START
    settings_data = settings.open_settings()    # otherwise it will use the value pulled from DB at the start of the program

    if not os.path.isfile(settings_data['path_yt_dlp']):
        messages.error_pop_up('Error', 'no_yt_dlp')
        return

    
    ## SAVE DATA
    # DESTINATION
    if settings_data['path_target_location'] != destination_field.get("1.0", "end-1c"):
        settings_data['path_target_location'] = destination_field.get("1.0", "end-1c")
        settings.save_settings(settings_data)

    ## DOWNLOAD
    av_selected = av_options_roll_down_clicked.get()
    link = settings_data['video_url']
    selected_resolution = av_options[av_selected]       #av_options['720p']
    path = destination_field.get("1.0", "end-1c")
    path_yt_dlp = get_path_yt_dlp()
    
    # FFMPEG PATH 
    if os.path.isfile(settings_data['path_ffmpeg']):          # if ffmpeg not added to the windows path - ffmpeg path browse field is used
        path_ffmpeg = settings_data['path_ffmpeg']
        add_path_ffmpeg = f'--ffmpeg-location "{path_ffmpeg}"'
    else:
        add_path_ffmpeg = ""
    
    # PARAMETER COMPILING
    # https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#format-selection-examples
    """
        Download the best video available with the largest resolution but no better than 480p,
        or the best video with the smallest resolution if there is no video under 480p
        Resolution is determined by using the smallest dimension.
        So this works correctly for vertical videos as well
        yt-dlp -S "res:480"
    """
    """
        Download the best video with the best extension
        (For video, mp4 > mov > webm > flv. For audio, m4a > aac > mp3 ...)
        yt-dlp -S "ext"
    """
    if selected_resolution.isdecimal(): # 360-2160
        parameter = f'-S "ext,res:{selected_resolution}" --paths "{path}" --progress {add_path_ffmpeg}'
    else:
        parameter = f'-x --audio-format mp3 --paths "{path}" --progress {add_path_ffmpeg}'  # Best-Audio Only-Convert to MP3
    
    executable =  f'{path_yt_dlp} {parameter} {link}'

    os.system(executable)

    # UPDATE THE FILE`S MODIFIED DATE ATTRIBUTE TO THE CURRENT DATE
    def change_modified_date():
        video_ID = settings_data['video_ID']
        if os_linux:
            file_path = glob.glob(f'{path}/*{video_ID}*')[0]
            subprocess.Popen(f'touch "{file_path}"', shell=True)
        else:
            os.chdir(path)
            update_date = f'copy /b *"{video_ID}"* +,,'
            os.system(update_date)
    
    change_modified_date()

button_start_instance = Buttons("START", lambda: [start()])
button_start = button_start_instance.create()


### DISPLAY WIDGETS
def display_widgets():
    # BASE VALUES
    # FIELD
    x_field = 17
    y_field = 20
    # BUTTON
    x_button = 350
    y_button_base = 15
    y_diff_from_start = 15

    def y_button(gap):
        location = y_button_base + 23 * gap
        return location
        
    # DESTINATION - FIELD + BROWSE BUTTON
    destination_field.place(x=x_field, y=y_field)
    destination_button.place(x=x_button, y=y_button(0)+2)

    # VIDEO TITLE AND DURATION - FIELD
    video_title_field.place(x=x_field, y=y_field + 35)

    # GET URL - BUTTON
    button_get_url.place(x=x_button, y=y_button(4) - y_diff_from_start)

    # SAVE AS - AUDIO / VIDEO OPTIONS - ROLL DOWN BUTTON
    av_options_roll_down.place(x=x_button-1, y=y_button(6) - y_diff_from_start-5)

    # SETTINGS BUTTON
    settings_button.place(x=x_button, y=y_button(8) - y_diff_from_start-4)

    # START - BUTTON
    button_start.place(x=x_button, y=y_button(10)+1)

    # THUMBNAIL
    thumbnail.place(x=thumbnail_x, y=thumbnail_y)


display_widgets()

window.mainloop()
