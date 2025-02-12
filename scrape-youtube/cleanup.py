import csv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Input and output file paths
input_file = 'allvideos.csv'
output_file = 'allvideos_cleaned.csv'

try:
    # Open the input and output CSV files
    with open(input_file, newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        
        # Write header to the output file
        writer.writeheader()

        # Track the number of rows processed and removed
        total_rows = 0
        removed_rows = 0

        # Iterate through each row
        for row in reader:
            total_rows += 1
            description = row.get('Description', '')  # Ensure the description column exists
            
            # Check for "Error: [0" in the description
            if "Error: [0" in description:
                removed_rows += 1
                continue  # Skip rows with the error message
            
            # Write valid rows to the output file
            writer.writerow(row)

    # Logging the result
    logging.info(f"Total rows processed: {total_rows}")
    logging.info(f"Rows removed: {removed_rows}")
    logging.info(f"Cleaned data saved to: {output_file}")

except FileNotFoundError as e:
    logging.error(f"File not found: {e.filename}")
except Exception as e:
    logging.error(f"Unexpected error: {str(e)}")
