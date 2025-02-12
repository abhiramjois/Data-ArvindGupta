import csv
import logging
from tqdm import tqdm
import yt_dlp
import time
import random
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory to save downloaded videos
DOWNLOAD_DIR = "path/to/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Function to extract YouTube video description and download video
def process_video(url, download_dir):
    ydl_opts = {
        'quiet': True,
        'force_generic_extractor': True,
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),  # File naming format
        'format': 'best',  # Download the best quality video
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            logging.info(f"Processing URL: {url}")
            
            # Extract video information and download the video
            info_dict = ydl.extract_info(url, download=True)
            
            # Add a random delay between 10 and 45 seconds
            delay = random.uniform(1, 5)
            logging.info(f"Sleeping for {delay:.2f} seconds before processing the next URL...")
            time.sleep(delay)
            
            # Return video description
            return info_dict.get('description', 'Description not available')
        
        except Exception as e:
            logging.error(f"Error processing {url}: {str(e)}")
            return f"Error: {str(e)}"

# Input and output file paths
input_file = 'films.csv'
output_file = '/path/to/descriptions.csv'

try:
    # Read the input CSV and process rows
    with open(input_file, newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        
        # Clean up column names by stripping spaces
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        fieldnames = ['Title', 'URL', 'Duration', 'Description']
        
        # Validate input columns
        required_columns = {'Title', 'URL', 'Duration'}
        if not required_columns.issubset(reader.fieldnames):
            raise ValueError(f"The file must contain the columns: {required_columns}")
        
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        # Process each row with a progress bar
        for row in tqdm(reader, desc="Processing URLs"):
            url = row['URL'].strip()
            
            # Process video (download and extract description)
            description = process_video(url, DOWNLOAD_DIR)
            row['Description'] = description
            
            # Write the updated row to the output CSV
            writer.writerow({field: row.get(field, '').strip() for field in fieldnames})

except FileNotFoundError as e:
    logging.error(f"File not found: {e.filename}")
except ValueError as e:
    logging.error(f"ValueError: {str(e)}")
except Exception as e:
    logging.error(f"Unexpected error: {str(e)}")

logging.info("Script finished successfully.")
