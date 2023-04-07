import os
import tarfile
from multiprocessing import Pool
import argparse
import requests

def download_and_extract(args):
    file_name, url, raw_dir, images_dir, masks_dir = args
    
    # Check if the file already exists
    if not os.path.exists(f'{raw_dir}/{file_name}'):
        # Download the file
        print(f'Downloading {file_name} from {url}...')
        response = requests.get(url, stream=True)
        with open(f'{raw_dir}/{file_name}', 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        print(f'{file_name} already exists in {raw_dir}. Skipping download.')

    # Extract the file
    print(f'Extracting {file_name}...')
    with tarfile.open(f'{raw_dir}/{file_name}') as tar:
        for member in tar.getmembers():
            if member.name.endswith(".jpg"):
                tar.extract(member, path=images_dir)
            elif member.name.endswith(".json"):
                tar.extract(member, path=masks_dir)
        
    print(f'{file_name} extracted!')

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Download and extract files.')
parser.add_argument('--processes', type=int, default=4, help='Number of processes to use for downloading and extracting files.')
parser.add_argument('--input_file', type=str, default='sa1b_links.txt', help='Path to the input file containing file names and URLs.')
parser.add_argument('--raw_dir', type=str, default='raw', help='Directory to store downloaded files.')
parser.add_argument('--images_dir', type=str, default='images', help='Directory to store extracted image files.')
parser.add_argument('--masks_dir', type=str, default='annotations', help='Directory to store extracted JSON mask files.')
args = parser.parse_args()

# Read the file names and URLs
with open(args.input_file, 'r') as f:
    lines = f.readlines()[1:]

# Create the directories if they do not exist
os.makedirs(args.raw_dir, exist_ok=True)
os.makedirs(args.images_dir, exist_ok=True)
os.makedirs(args.masks_dir, exist_ok=True)

# Download and extract the files in parallel
with Pool(processes=args.processes) as pool:
    pool.map(download_and_extract, [line.strip().split('\t') + [args.raw_dir, args.images_dir, args.masks_dir] for line in lines])

print('All files extracted successfully!')