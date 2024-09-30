from customtkinter import *

import requests
import threading
import Wattpad2epub as wattpad



## Consts
VERSION = "v0.2.0"

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
root.title(f"BookNow - Wattpad Downloader [{VERSION}]")
set_appearance_mode("Dark")

CTkLabel(root, text="BookNow", font=TITLE).place(x=20, y=20)
CTkLabel(root, text="Wattpad Downloader", font=SUBTITLE).place(x=20, y=75)

CTkLabel(root, text="Story URL: ", font=SUBTITLE).place(x=20, y=170)
story_url = StringVar()
tk_story_url = CTkEntry(root, textvariable=story_url, font=SUBTITLE, width=400)
tk_story_url.place(x=145, y=170)


def download_book():
    if "wattpad.com" not in story_url.get():
        return

    tk_story_url.configure(state=DISABLED)
    tk_download.configure(state=DISABLED)
    tk_status.place_forget()
    story_id = wattpad.get_chapter_id(story_url.get())

    story_info_url = wattpad.base_apiV3_url + f"stories/{story_id}?drafts=0&mature=1&include_deleted=1&fields=id,title,createDate,modifyDate,description,url,firstPublishedPart,cover,language,user(name,username,avatar,location,numStoriesPublished,numFollowing,numFollowers,twitter),completed,numParts,lastPublishedPart,parts(id,title,length,url,deleted,draft,createDate),tags,storyLanguage,copyright"
    json_data  = requests.get(story_info_url, headers={'User-Agent': 'Mozilla/5.0'}).json()
    summary, tags, chapters, story_name, author, cover = wattpad.extract_useful_data(json_data)
    
    html_file_name = f"{story_name}.html"
    
    tk_process.place(x=20, y=330)
    tk_process.start()
    wattpad.save_html_file(html_file_name, story_name, author, cover, tags, summary, chapters)
    tk_process.stop()
    tk_process.place_forget()


    tk_story_url.configure(state=NORMAL)
    tk_download.configure(state=NORMAL)
    tk_status.configure(text=f"{story_name} downloaded as {html_file_name}")
    tk_status.place(x=20, y=300)



def start_download():
    download_thread = threading.Thread(target=download_book)
    download_thread.start()

tk_download = CTkButton(root, font=PARA, text="Download", command=start_download, width=530)
tk_download.place(x=20, y=240)


tk_status = CTkLabel(root, text="Default Message", font=PARA)


tk_process = CTkProgressBar(root, orientation="horizontal", width=540, mode="indeterminate", indeterminate_speed=1)
tk_process.set(0)


root.mainloop()