import requests
from bs4 import BeautifulSoup
import re
import json


def get_soup(playlist_link: str) -> BeautifulSoup:
    """ Parse the HTML content of the given playlist. """

    headers = {"Accept-Language": "en"}
    response = requests.get(playlist_link, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


def extract_json(soup: BeautifulSoup) -> list:
    """ Extract JSON-like data from html with desired properties (it's in the script tag ytInitialData). """

    script_tag = soup.find('script', string=re.compile(r'var ytInitialData = {'))
    json_data = re.search(r'var ytInitialData = ({.*?});', script_tag.text, re.DOTALL)
    data = json.loads(json_data.group(1))

    # Access the desired properties
    video_data = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"][
        "content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]

    return video_data


def parse_json(video_data: list) -> list[dict]:
    """ Extract and parse the JSON data from the script tag. """

    playlist_info = []
    for video in video_data:
        video_renderer = video["playlistVideoListRenderer"]["contents"]
        for renderer in video_renderer:
            playlist_info.append(get_video_info(renderer))

    return playlist_info


def get_video_info(renderer: json) -> dict:
    """ Extract desired values from json and make dictionary out of them. """

    video_id = renderer['playlistVideoRenderer']['videoId']
    title = renderer['playlistVideoRenderer']['title']['runs'][0].get("text")
    title_label = renderer['playlistVideoRenderer']['title']['accessibility']['accessibilityData'].get("label")
    video_index = renderer['playlistVideoRenderer']['index'].get("simpleText")
    views = renderer['playlistVideoRenderer']['videoInfo']['runs'][0].get("text")
    thumbnail_url = renderer['playlistVideoRenderer']['thumbnail']['thumbnails'][0].get("url")
    video_url = renderer[
        'playlistVideoRenderer']['navigationEndpoint']['commandMetadata']['webCommandMetadata'].get("url")
    length_seconds = renderer['playlistVideoRenderer']['lengthSeconds']

    return {
        "Video ID": video_id,
        "Title": title,
        "Title label": title_label,
        "Video Index": video_index,
        "Views": views,
        "Thumbnail URL": thumbnail_url,
        "Video URL": video_url,
        "Length": length_seconds,
    }

