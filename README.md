# PNG Fixer

This project has been made to learn about the PNG Format. It is by no mean robust, and the code is complete garbage.

However, it may be used to help and assist in forensics CTF challenges. Currently, it automatically fixes the PNG magic bytes, chunk length and CRC. When a typo is encountered in a chunk type field, it prompts the user to enter the correct value.

## New Feature: Save and Exit Functionality

In addition to its core functionality of fixing PNG magic bytes, chunk length, and CRC, the tool now includes a "Save and Exit" feature. If the user enters 0 during any interactive prompt (e.g., when correcting a chunk type), the tool will immediately save the current progress of the PNG file repair to the specified output file and exit. This feature allows users to save their work at any point and resume later or terminate early without losing their progress.

## Usage

The project runs in python 3. It can be run as follows :

    python3 png_fixer.py corrupted.png output.png
