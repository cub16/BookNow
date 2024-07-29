#! /usr/bin/python3
"""
# Python Script to Scrape Wattpad Story and convert to Epub and html file.
# By Architrixs, Created Nov 5, 2020.
# Modified by cub16.
# This program will create:
# 1. A html file of the entire Wattpad Book AND (You can directly Use this one to read, Images are preserved in this format.)
"""
import argparse
import bs4
import requests
import pyperclip
import re
import base64

base_apiV2_url = "https://www.wattpad.com/apiv2/"
base_apiV3_url = "https://www.wattpad.com/api/v3/"
dev_error_msg = "ERR"
"""
https://www.wattpad.com/api/v3/stories/{{story_id}}?drafts=0&mature=1&include_deleted=1&fields=id,title,createDate,modifyDate,voteCount,readCount,commentCount,description,url,firstPublishedPart,cover,language,isAdExempt,user(name,username,avatar,location,highlight_colour,backgroundUrl,numLists,numStoriesPublished,numFollowing,numFollowers,twitter),completed,isPaywalled,paidModel,numParts,lastPublishedPart,parts(id,title,length,url,deleted,draft,createDate),tags,categories,rating,rankings,tagRankings,language,storyLanguage,copyright,sourceLink,firstPartId,deleted,draft,hasBannedCover,length
"""

def get_chapter_id(url):
    """Extracts the chapter ID from the given URL."""
    search_id = re.compile(r'\d{5,}')
    id_match = search_id.search(url)
    if id_match:
        return id_match.group()
    return None


def download_webpage(url):
    """Downloads the webpage content from the given URL."""
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        res.raise_for_status()
        return res.text
    except requests.exceptions.RequestException as exc:
        print("There was a problem: %s" % (exc))
        return None

def img_to_base64(url):
    return base64.b64encode(requests.get(url).content).decode('utf-8')

def convert_images_in_html(html_content):
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    for img_tag in soup.find_all('img'):
        img_url = img_tag.get('src')
        if img_url and img_url.startswith(('http://', 'https://')):
            base64_image = img_to_base64(img_url)
            if base64_image:
                img_tag['src'] = f"data:image/{img_url.split('.')[-1]};base64,{base64_image}"
    return str(soup)

def extract_useful_data(json_data):
    """Extracts useful data from the JSON response."""
    summary = json_data.get('description', '')
    tags = json_data.get('tags', '')
    chapters = json_data.get('parts', '')
    storyName = json_data.get('title', '')
    author = json_data.get('user', '')
    cover = img_to_base64(json_data.get('cover', ''))
    return summary, tags, chapters, storyName, author, cover



def save_html_file(file_name, story_name, author, cover, tags, summary, chapters):
    """Saves the HTML file with the given data."""

    file = open(file_name, 'w', encoding='utf-8')

    custom_css = requests.get("https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css")

    file.write(f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name='title' content='{story_name}'>
            <meta name='author' content='{author["name"]}'>
            <style>
            {custom_css.text}
            </style>
        </head>
        <body>
        <div style="text-align: center;">
            <img src="data:image/png;base64,{cover}" alt="cover_image">
        </div>
        <br>
        <h1 align="center">{story_name}</h1>
        <h4 align="center"><a href="https://www.wattpad.com/user/{author["username"]}">{author["username"]}</a></h4>

        <div align="center">Tags: {tags} </div>
        <br><br>
        <div align="center">{summary}</div>
        
    """)
    for i, chapter in enumerate(chapters):
        print(f"Getting Chapter {i + 1}....")
        chapter_url = base_apiV2_url + f"storytext?id={chapter['id']}"
        chapter_content = download_webpage(chapter_url)
        if chapter_content:
            soup_res = bs4.BeautifulSoup(chapter_content, 'html.parser')
            file.write(f"""
                <br><br>
                <div class='container'>
                    <h2>{chapter['title']}</h2>
                    <br><br>
                    {convert_images_in_html(soup_res.prettify())}
                </div>
            """)

    file.write("</body></html>")
    file.close()
    print(f"Saved {file_name}")


def main(url):
    story_id = get_chapter_id(url)
    if not story_id:
        print(dev_error_msg)
        return

    # Getting JSON data from Wattpad API.
    story_info_url = base_apiV3_url + f"stories/{story_id}?drafts=0&mature=1&include_deleted=1&fields=id,title,createDate,modifyDate,description,url,firstPublishedPart,cover,language,user(name,username,avatar,location,numStoriesPublished,numFollowing,numFollowers,twitter),completed,numParts,lastPublishedPart,parts(id,title,length,url,deleted,draft,createDate),tags,storyLanguage,copyright"
    json_data  = requests.get(story_info_url, headers={'User-Agent': 'Mozilla/5.0'}).json()
    try:
        if json_data.get('result') == 'ERROR':
            error_message = json_data.get('message', 'Unknown error')
            print(f"Error: {error_message}")
            print(dev_error_msg)
            return
        
        if json_data.get('error_type') :
            error_message = json_data.get('message', 'Unknown error')
            print(f"Error: {error_message}")
            print(dev_error_msg)
            return
        
    
        if json_data.get('result') == 'ERROR':
            error_message = json_data.get('message', 'Unknown error')
            print(f"API Error: {error_message}")
            return
    except Exception as exc:
        print(f"Error retrieving JSON data from the API: {exc}")
        return

    # Extracting useful data from JSON.
    summary, tags, chapters, story_name, author, cover = extract_useful_data(json_data)

    # Saving HTML file.
    html_file_name = f"{story_name}.html"
    html_file_name = html_file_name.replace('/', ' ')
    save_html_file(html_file_name, story_name, author, cover, tags, summary, chapters)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Wattpad2epub: Convert Wattpad stories to EPUB format.')
    parser.add_argument('url', nargs='?', help='URL of the Wattpad Story')
    args = parser.parse_args()

    if args.url:
        main(args.url)
    else:
        # Getting address from clipboard.
        url = pyperclip.paste()
        main(url)
