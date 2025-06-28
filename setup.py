from setuptools import find_packages, setup

setup(
    name="learning_german",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "genanki>=0.13.0",
        "deep-translator>=1.10.1",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
    ],
    entry_points={
        "console_scripts": [
            "german-translate=learning_german.markdown_note_generator:main_async_wrapper",
            "german-to-anki=learning_german.anki_deck_generator:main",
            "extract-examples=learning_german.obsidian_words_and_examples_extractor:main",
        ],
    },
    python_requires=">=3.6",
    author="Abbas Endari",
    description="Tools for learning German with automated translation and flashcard generation",
    keywords="german, language-learning, anki, translation",
)
