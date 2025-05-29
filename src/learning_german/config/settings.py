"""Configuration settings for the Learning German tools."""

import os
import platform

# Determine the OS
IS_MAC = platform.system() == "Darwin"
IS_WINDOWS = platform.system() == "Windows"

# Base paths that differ between OS
if IS_MAC:
    BASE_PATH = "/Users/abbas/Library/CloudStorage/Dropbox/Obsidian-Vaults/German"
else:
    BASE_PATH = r"C:\Users\aenda\Dropbox\Obsidian-Vaults\German"

# Media paths using os.path.join for cross-platform compatibility
OBSIDIAN_MEDIA_PATHS = [os.path.join(BASE_PATH, "Sicher B2", "Media")]

# File paths
INPUT_FILE = "data_files/input/input.md"
OUTPUT_FILE = "data_files/output/output.md"
MEDIA_FOLDER = "Media"
OUTPUT_DIR = "data_files/output"

# Audio search paths with cross-platform compatibility
AUDIO_SEARCH_PATHS = [
    MEDIA_FOLDER,  # Project media folder
    os.path.join(BASE_PATH, "Sicher B2", "Media"),  # Obsidian vault media path
]

# File operations
READ_MODE = "r"
APPEND_MODE = "a"
ENCODING = "utf-8"

# Processing settings
MIN_WORD_LENGTH = 2
