from customtkinter import *
import random
import requests

import Wattpad2epub as wattpad

## Consts
VERSION = "v0.1.0"

## Styles
MAIN_FONT = "Times New Roman"
SECOND_FONT = "Arial"
TITLE = (MAIN_FONT, 50)
SUBTITLE = (MAIN_FONT, 25)
PARA = (SECOND_FONT, 15)

## App
root = CTk()
root.geometry("600x600")
root.resizable(False, False)
root.title(f"BookNow - wattpad downloader [{VERSION}]")
set_appearance_mode("System")

CTkLabel(root, text="BookNow", font=TITLE).place(x=20, y=20)
CTkLabel(root, text="wattpad downloader", font=SUBTITLE).place(x=20, y=75)

def change_theme():
    if get_appearance_mode() == "Light":
        set_appearance_mode("Dark")
    elif get_appearance_mode() == "Dark":
        set_appearance_mode("Light")
    else:
        set_appearance_mode("Light")

CTkButton(root, command=change_theme, text="Change Theme", width=130, height=50, font=PARA).place(x=450, y=30)

CTkLabel(root, text="Story URL: ", font=SUBTITLE).place(x=20, y=170)
story_url = StringVar()
tk_story_url = CTkEntry(root, textvariable=story_url, font=SUBTITLE, width=400)
tk_story_url.place(x=145, y=170)


def download_book():
    if "wattpad.com" not in story_url.get():
        return

    story_id = wattpad.get_chapter_id(story_url.get())

    story_info_url = wattpad.base_apiV3_url + f"stories/{story_id}?drafts=0&mature=1&include_deleted=1&fields=id,title,createDate,modifyDate,description,url,firstPublishedPart,cover,language,user(name,username,avatar,location,numStoriesPublished,numFollowing,numFollowers,twitter),completed,numParts,lastPublishedPart,parts(id,title,length,url,deleted,draft,createDate),tags,storyLanguage,copyright"
    json_data  = requests.get(story_info_url, headers={'User-Agent': 'Mozilla/5.0'}).json()
    summary, tags, chapters, story_name, author, cover = wattpad.extract_useful_data(json_data)

    print(f"""
        ---- BOOK INFO ----
        STORY URL: {story_url.get()}
        STORY ID: {story_id}
        -------------------
        """)
    

    tk_process.configure(state=NORMAL)
    tk_process.insert("1.0", f"Downloading {story_name}...")
    tk_process.configure(state=DISABLED)
    
    html_file_name = f"WATTPAD_{random.randint(1000,9999)}.html"
    wattpad.save_html_file(html_file_name, story_name, author, cover, tags, summary, chapters)
    
    tk_process.configure(state=NORMAL)
    tk_process.insert("2.0", f"\n{story_name} downloaded as: '{html_file_name}'")
    tk_process.configure(state=DISABLED)
    

tk_download = CTkButton(root, font=PARA, text="Download", command=download_book, width=530)
tk_download.place(x=20, y=240)

tk_process = CTkTextbox(root, font=PARA, width=540)
tk_process.configure(state=DISABLED)
tk_process.place(x=20, y=330)

root.mainloop()