import os
import requests
import aiohttp
import asyncio
import aiofiles
from bs4 import BeautifulSoup
from learning_german.config.settings import AUDIO_SEARCH_PATHS, MEDIA_FOLDER


def check_audio_exists(filename):
    """
    Check if audio file already exists in any of the search paths.
    
    Args:
        filename (str): Base filename without extension
        
    Returns:
        str or None: Path to existing audio file if found, None otherwise
    """
    for folder in AUDIO_SEARCH_PATHS:
        file_path = os.path.join(folder, f"{filename}.wav")
        if os.path.exists(file_path):
            return file_path
    return None


def get_audio_url(german_word):
    url = f"https://dic.b-amooz.com/de/dictionary/w?word={german_word.lower()}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.78 Safari/537.36",
    }
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return parse_audio_url(response.text)
    return None


def parse_audio_url(html):
    """Parse HTML to extract audio URL"""
    soup = BeautifulSoup(html, "html.parser")
    
    # Try the original method first
    div = soup.find("h1", class_="mdc-typography--headline4 ltr d-inline position-relative")
    
    if div and div.find("small") and "data-url" in div.find("small").attrs:
        audio_link = div.find("small")["data-url"]
        return audio_link
        
    # Alternative method - look for any audio element
    audio_elements = soup.find_all("audio")
    for audio in audio_elements:
        if audio.has_attr("src"):
            return audio["src"]
            
    # Try to find any element with data-url attribute
    elements_with_data_url = soup.find_all(attrs={"data-url": True})
    if elements_with_data_url:
        audio_link = elements_with_data_url[0]["data-url"]
        return audio_link
    
    return None


# Function to download audio file
def download_audio(url, filename):
    # First check if the audio file already exists
    existing_file = check_audio_exists(filename)
    if existing_file:
        print(f"Audio file for '{filename}' already exists at {existing_file}")
        return existing_file
        
    # Define headers for the HTTP request to mimic a web browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.78 Safari/537.36",
    }

    # Send an HTTP GET request to the provided URL with specified headers
    response = requests.get(url, headers=headers)

    # Check if the response status code is 200 (successful)
    if response.status_code == 200:
        folder_path = MEDIA_FOLDER

        # Check to see if folder_path exists. If it doesn't, create it.
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Create the target file path for the .wav file.
        file_path_wav = os.path.join(folder_path, filename + ".wav")

        # Write the contents of the response (in this case a .wav audio file) into file_path
        with open(file_path_wav, "wb") as f:
            f.write(response.content)
        
        return file_path_wav
    else:
        print(f"Failed to download {filename}. Status code: {response.status_code}")
        return None


# Async versions of the functions
async def get_audio_url_async(german_word):
    """Async version of get_audio_url"""
    url = f"https://dic.b-amooz.com/de/dictionary/w?word={german_word.lower()}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.78 Safari/537.36",
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                # Use run_in_executor for BeautifulSoup parsing as it's CPU-bound
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, parse_audio_url, html)
    return None


async def download_audio_async(url, filename):
    """Async version of download_audio"""
    # First check if the audio file already exists
    existing_file = check_audio_exists(filename)
    if existing_file:
        print(f"Audio file for '{filename}' already exists at {existing_file}")
        return existing_file
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.78 Safari/537.36",
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                folder_path = MEDIA_FOLDER
                
                # Check to see if folder_path exists. If it doesn't, create it.
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                
                # Create the target file path for the .wav file.
                file_path_wav = os.path.join(folder_path, filename + ".wav")
                
                # Write the contents of the response
                content = await response.read()
                async with aiofiles.open(file_path_wav, "wb") as f:
                    await f.write(content)
                
                return file_path_wav
            else:
                print(f"Failed to download {filename}. Status code: {response.status}")
                return None