import csv
import logging
import os
import yt_dlp
import time
import random
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory where videos were downloaded
DOWNLOAD_DIR = "downloads"
ABS_DOWNLOAD_DIR = f"/path/to/{DOWNLOAD_DIR}"

# Input and output file paths
input_file = '/path/to/descriptions.csv'
output_file = '/path/to/allvideos.csv'

def get_video_title_and_path(video_url, download_dir):
    """
    Extract the actual video title and determine the video path.
    """
    ydl_opts = {
        'quiet': True,
        'force_generic_extractor': True,
        'skip_download': True,  # Don't re-download the video
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract video information
            logging.info(f"Fetching title for URL: {video_url}")
            info_dict = ydl.extract_info(video_url, download=False)
            
            # Extract title and construct video path
            video_title = info_dict.get('title', 'Unknown Title')
            video_ext = info_dict.get('ext', 'mp4')  # Default to .mp4 if no extension is provided
            video_filename = f"{video_title}.{video_ext}"
            video_path = os.path.join(download_dir, video_filename)  # Relative path
            
            return video_title, video_path
        except Exception as e:
            logging.error(f"Error fetching title for {video_url}: {str(e)}")
            return "Error: Title not found", "Error: Path not found"

try:
    # Open input CSV and process rows
    with open(input_file, newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = list(csv.DictReader(infile))  # Load all rows into memory at once
        if not reader:
            logging.error("The input CSV file is empty.")
            exit(1)  # Exit if the CSV is empty

        total_videos = len(reader)  # Get the total number of videos

        # Add new fields for YouTube title and video path
        fieldnames = list(reader[0].keys()) + ['YouTube Title', 'Video Path']  # Ensure keys exist
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        # Initialize progress tracking
        progress_bar = tqdm(total=total_videos, desc=f"Processed 0/{total_videos} videos", unit="video")
        
        for idx, row in enumerate(reader, start=1):
            url = row.get('URL', '').strip()  # Ensure URL key exists
            if not url:
                logging.warning(f"Skipping row {idx} due to missing or empty URL.")
                continue  # Skip rows with empty URLs
            
            logging.info(f"Processing video {idx}/{total_videos}: {url}")
            
            # Get YouTube title and video path
            youtube_title, video_path = get_video_title_and_path(url, DOWNLOAD_DIR)
            
            # Add the new fields to the row
            row['YouTube Title'] = youtube_title
            row['Video Path'] = video_path
            
            # Write the updated row to the output file
            writer.writerow(row)
            
            # Update progress bar and its description
            progress_bar.set_description(f"Processed {idx}/{total_videos} videos")
            progress_bar.update(1)
            
            # Add a random time delay between 1 and 5 seconds
            delay = random.uniform(1, 5)
            logging.info(f"Sleeping for {delay:.2f} seconds before processing the next video...")
            time.sleep(delay)
        
        progress_bar.close()

except FileNotFoundError as e:
    logging.error(f"File not found: {e.filename}")
except ValueError as e:
    logging.error(f"ValueError: {str(e)}")
except Exception as e:
    logging.error(f"Unexpected error: {str(e)}")

logging.info("Script finished successfully.")
