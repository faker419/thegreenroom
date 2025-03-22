import os
import shutil

# Define the path to the text file containing source file paths
source_file_list = r"C:\wamp64\www\thegreenroom\image_urls.txt"

# Define the destination directory
destination_dir = r"C:\wamp64\www\thegreenroom\jekyll-gitbook\assets\proposal_images"

# Read the list of source files from the text file
try:
    with open(source_file_list, "r") as file:
        source_files = file.read().splitlines()  # Read lines and remove newline characters
except FileNotFoundError:
    print(f"Error: The file '{source_file_list}' does not exist.")
    exit(1)

# Create the destination directory if it doesn't exist
if not os.path.exists(destination_dir):
    print("no file")
    os.makedirs(destination_dir)

# Copy each file to the destination directory
if  os.path.exists(destination_dir):
    for source_file in source_files:
        if os.path.exists(source_file):  # Check if the source file exists
            file_name = os.path.basename(source_file)  # Get the file name
            destination_file = os.path.join(destination_dir, file_name)  # Create the destination path
            shutil.copy2(source_file, destination_file)  # Copy the file
            print(f"Copied: {source_file} -> {destination_file}")
        else:
            print(f"File not found: {source_file}")

    print("All files copied successfully!")