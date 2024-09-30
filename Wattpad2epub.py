#! /usr/bin/python3
"""
### Python Script to Scrape Wattpad Story and convert to Epub and html file.
#### By Architrixs, Created Nov 5, 2020.
#### Modified by cub16.
"""
import bs4
import requests
import re
import base64
import minify_html


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
        sanitized_res = res.text.replace('style="text-align:center;"', "")
        return sanitized_res
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
    global download_status
    """Saves the HTML file with the given data."""

    file = open(file_name, 'w', encoding='utf-8')

    with open("./pico.min.css") as pico_file:
        global PicoCSS
        PicoCSS = pico_file.read()

    with open("./custom.css") as custom_file:
        global customCSS
        customCSS = custom_file.read()

    file_content = ""

    file_content += f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="title" content="{story_name}">
    <meta name="author" content="{author['name']}">
    <meta name="description" content="{summary}">
    <title>{story_name}</title>
    <style>
        {PicoCSS}
    </style>
    <style>{customCSS}</style>
</head>
<body class="container">
    <header style="text-align: center">
        <div>
            <img src="data:image/png;base64,{cover}" alt="{story_name} [Cover]">
        </div>
        <h1>{story_name}</h1>
        <h4>
            <a href="https://www.wattpad.com/user/{author['username']}">
                {author['username']}
            </a>
        </h4>
    </header>

    <section>
        <p class="tags">Tags: {", ".join(tags)}</p>
        <p>{summary}</p>
    </section>
        
    """
    for i, chapter in enumerate(chapters):
        chapter_url = base_apiV2_url + f"storytext?id={chapter['id']}"
        chapter_content = download_webpage(chapter_url)
        if chapter_content:
            soup_res = bs4.BeautifulSoup(chapter_content, 'html.parser')
            file_content += f"""
                <br><br>
                <div>
                    <h2>{chapter['title']}</h2>
                    <br><br>
                    {convert_images_in_html(soup_res.prettify())}
                </div>
            """

    file_content += "</body></html>"


    file_content_minified = minify_html.minify(file_content)
    file.write(file_content_minified)
    file.close()

    print(f"Saved {file_name}")
    return True


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