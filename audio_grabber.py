import os

import ffmpeg
import requests
from bs4 import BeautifulSoup


def get_audio_url(german_word):
    url = f"https://en.wiktionary.org/wiki/File:De-{german_word}.ogg"

    response = requests.get(url)

    if response.status_code == 200:
        # Parse the HTML content of the response using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the <div> element with class 'mw-content-ltr fullMedia' which contains the audio link
        div = soup.find("div", class_="mw-content-ltr fullMedia")

        # If such a <div> element is found
        if div:
            # Find the <a> element within the <div> which contains the audio link
            audio_link = div.find("a")["href"]
            # Return the URL of the audio file
            return audio_link

    # If the URL or audio link is not found, return None
    return None


def convert_ogg_to_mp3(input_file, output_file):
    (ffmpeg.input(input_file).output(output_file).run())


# Function to download audio file
def download_audio(url, filename, convert=False):
    # Add the 'https://' scheme to the URL.
    url = "https:" + url

    # Define headers for the HTTP request to mimic a web browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.78 Safari/537.36",
    }

    # Send an HTTP GET request to the provided URL with specified headers
    response = requests.get(url, headers=headers)

    # Check if the response status code is 200 (successful)
    if response.status_code == 200:
        folder_path = "Media"

        # Check to see if folder_path exists. If it doesn't, create it.
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Create the target file path for the .ogg file.
        file_path_ogg = os.path.join(folder_path, filename + ".ogg")

        # Write the contents of the response (in this case a .ogg audio file) into file_path_ogg
        with open(file_path_ogg, "wb") as f:
            f.write(response.content)

        # Convert the file from .ogg to .mp3 using ffmpeg if convert=True
        if convert:
            # Create the target file path for the .mp3 file.
            file_path_mp3 = os.path.join(folder_path, filename + ".mp3")
            convert_ogg_to_mp3(file_path_ogg, file_path_mp3)
            os.remove(file_path_ogg)  # Remove the original .ogg file
            print(f"Downloaded and converted {filename}")
        else:
            print(f"Downloaded {filename}")

    else:
        print(f"Failed to download {filename}. Status code: {response.status_code}")
        print(response.text)  # Print response content for debugging purposes
