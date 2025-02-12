import csv
import logging
import os
import time
import random
from tqdm import tqdm
import yt_dlp
import requests
from PIL import Image
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory to save thumbnails
THUMBNAIL_DIR = "images"
ABS_THUMBNAIL_DIR = f"/path/to/{THUMBNAIL_DIR}"
os.makedirs(ABS_THUMBNAIL_DIR, exist_ok=True)

def download_thumbnail(video_url, title):
    """
    Downloads and processes the thumbnail for the given video URL.
    """
    ydl_opts = {'quiet': True}
    thumbnail_path = None

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            logging.info(f"Extracting information for URL: {video_url}")
            info_dict = ydl.extract_info(video_url, download=False)
            thumbnail_url = info_dict.get('thumbnail')
            if thumbnail_url:
                logging.info(f"Downloading and processing thumbnail for {title}")
                
                sanitized_title = ''.join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip()
                thumbnail_filename = f"{sanitized_title}.webp"
                thumbnail_path = os.path.join(THUMBNAIL_DIR, thumbnail_filename)
                
                response = requests.get(thumbnail_url, stream=True)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    img = img.convert("RGB")
                    img.thumbnail((200, 200), Image.LANCZOS)
                    img.save(os.path.join(ABS_THUMBNAIL_DIR, thumbnail_filename), "WEBP", quality=85)
                else:
                    logging.error(f"Failed to download thumbnail for {title}")
            else:
                logging.warning(f"No thumbnail found for {title}")
        except Exception as e:
            logging.error(f"Error processing {video_url}: {str(e)}")
    return thumbnail_path

# Input and output file paths
# In case you are taking from the previous descriptions file
input_file = '/path/to/descriptions.csv'
output_file = '/media/abhiram/Expansion/toyrepo/allvideos_with_thumbnails.csv'

try:
    # Read the input CSV and process rows
    with open(input_file, newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = list(csv.DictReader(infile))  # Read all rows
        if not reader:
            logging.error("The input CSV file is empty.")
            exit(1)

        total_videos = len(reader)  # Total videos
        fieldnames = list(reader[0].keys()) + ['Thumbnail Path']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        # Initialize progress bar
        with tqdm(total=total_videos, desc="Processing Videos", unit="video") as progress_bar:
            for idx, row in enumerate(reader, start=1):
                url = row.get('URL', '').strip()
                title = row.get('YouTube Title', 'Unknown Title').strip()

                if not url:
                    logging.warning(f"Skipping row {idx} due to missing URL.")
                    continue
                
                logging.info(f"Processing video {idx}/{total_videos}: {url}")
                
                # Download and process the thumbnail
                thumbnail_path = download_thumbnail(url, title)
                row['Thumbnail Path'] = os.path.join(THUMBNAIL_DIR, os.path.basename(thumbnail_path)) if thumbnail_path else "Not Available"

                writer.writerow(row)  # Write the updated row
                progress_bar.update(1)  # Update the progress bar
                
                # Add a random delay
                delay = random.uniform(1, 5)
                logging.info(f"Sleeping for {delay:.2f} seconds...")
                time.sleep(delay)

except FileNotFoundError as e:
    logging.error(f"File not found: {e.filename}")
except ValueError as e:
    logging.error(f"ValueError: {str(e)}")
except Exception as e:
    logging.error(f"Unexpected error: {str(e)}")

logging.info("Script finished successfully.")
