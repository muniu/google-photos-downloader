from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import os
import requests
from pathlib import Path
import json
import logging
from google.auth.transport.requests import Request
import pickle
import getpass
import time
from datetime import datetime
import sys

class GooglePhotosDownloader:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
        self.credentials = None
        self.service = None
        self.user_email = None
        self.BATCH_SIZE = 500  # Process 500 photos at a time
        self.RETRY_COUNT = 3
        self.download_log_file = 'downloaded_files.json'
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_token_path(self):
        """Generate token path based on user email"""
        if not self.user_email:
            return 'token.pickle'
        return f'token_{self.user_email.replace("@", "_at_")}.pickle'
    
    def authenticate(self, credentials_path='credentials.json'):
        """Authenticate with Google Photos API"""
        try:
            # Get user email
            self.user_email = input("Enter your Google email address: ").strip()
            token_path = self.get_token_path()
            
            # First try to load existing token
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    self.credentials = pickle.load(token)

            # If there are no valid credentials available, authenticate
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if not os.path.exists(credentials_path):
                        raise FileNotFoundError(
                            f"credentials.json not found in {credentials_path}. "
                            "Please download it from Google Cloud Console."
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                    self.credentials = flow.run_local_server(port=0)
                
                # Save the credentials for future use
                with open(token_path, 'wb') as token:
                    pickle.dump(self.credentials, token)

            # Build the service
            self.service = build('photoslibrary', 'v1', 
                               credentials=self.credentials,
                               static_discovery=False)
            
            self.logger.info(f"Successfully authenticated for user: {self.user_email}")
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise

    def get_albums(self):
        """List all available albums"""
        if not self.service:
            raise ValueError("Service not initialized. Please authenticate first.")
            
        try:
            albums = []
            page_token = None
            
            while True:
                # Get a page of albums
                request = self.service.albums().list(
                    pageSize=50,
                    pageToken=page_token
                )
                response = request.execute()
                
                # Debug logging
                self.logger.debug(f"API Response: {json.dumps(response, indent=2)}")
                
                # Get albums from response
                if 'albums' in response:
                    for album in response.get('albums', []):
                        if 'title' in album and 'id' in album:
                            albums.append({
                                'title': album['title'],
                                'id': album['id']
                            })
                
                # Check if there are more pages
                if 'nextPageToken' not in response:
                    break
                page_token = response['nextPageToken']
            
            if not albums:
                self.logger.warning("No albums found or accessible")
                
            return albums
            
        except HttpError as e:
            self.logger.error(f"Failed to fetch albums: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching albums: {str(e)}")
            raise

    def load_downloaded_files(self, album_id):
        """Load list of already downloaded files"""
        try:
            if os.path.exists(self.download_log_file):
                with open(self.download_log_file, 'r') as f:
                    download_log = json.load(f)
                    return set(download_log.get(album_id, []))
            return set()
        except Exception as e:
            self.logger.error(f"Error loading download log: {e}")
            return set()

    def save_downloaded_file(self, album_id, filename):
        """Save downloaded file to log"""
        try:
            download_log = {}
            if os.path.exists(self.download_log_file):
                with open(self.download_log_file, 'r') as f:
                    download_log = json.load(f)
            
            if album_id not in download_log:
                download_log[album_id] = []
            
            if filename not in download_log[album_id]:
                download_log[album_id].append(filename)
            
            with open(self.download_log_file, 'w') as f:
                json.dump(download_log, f)
        except Exception as e:
            self.logger.error(f"Error saving to download log: {e}")

    def get_fresh_download_url(self, media_item_id):
        """Get a fresh download URL for a media item"""
        try:
            media_item = self.service.mediaItems().get(mediaItemId=media_item_id).execute()
            return media_item.get('baseUrl') + '=d'
        except Exception as e:
            self.logger.error(f"Error getting fresh URL: {e}")
            return None

    def download_album(self, album_id, output_dir):
        """Download all photos from a specific album in batches"""
        if not self.service:
            raise ValueError("Service not initialized. Please authenticate first.")
            
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Load already downloaded files
            downloaded_files = self.load_downloaded_files(album_id)
            self.logger.info(f"Found {len(downloaded_files)} previously downloaded files")

            # Get album details
            album = self.service.albums().get(albumId=album_id).execute()
            album_title = album.get('title', 'Unnamed Album')
            self.logger.info(f"Processing album: {album_title}")
            
            # Get all media items
            media_items = []
            page_token = None
            
            print("Fetching media items list...")
            while True:
                request_body = {
                    'albumId': album_id,
                    'pageSize': 100
                }
                if page_token:
                    request_body['pageToken'] = page_token
                
                response = self.service.mediaItems().search(body=request_body).execute()
                current_items = response.get('mediaItems', [])
                media_items.extend(current_items)
                
                print(f"\rFound {len(media_items)} items...", end='')
                sys.stdout.flush()
                
                if 'nextPageToken' not in response:
                    break
                page_token = response['nextPageToken']
            
            print(f"\nTotal media items found: {len(media_items)}")
            
            # Process in batches
            total_items = len(media_items)
            for batch_start in range(0, total_items, self.BATCH_SIZE):
                batch_end = min(batch_start + self.BATCH_SIZE, total_items)
                batch = media_items[batch_start:batch_end]
                
                print(f"\nProcessing batch {batch_start//self.BATCH_SIZE + 1} "
                      f"(items {batch_start + 1} to {batch_end} of {total_items})")
                
                # Process each item in the batch
                for i, item in enumerate(batch, 1):
                    filename = item.get('filename')
                    if not filename:
                        continue
                    
                    # Skip if already downloaded
                    if filename in downloaded_files:
                        print(f"\rSkipping {filename} (already downloaded)", end='')
                        continue
                    
                    # Get fresh download URL and try downloading
                    for retry in range(self.RETRY_COUNT):
                        try:
                            download_url = self.get_fresh_download_url(item['id'])
                            if not download_url:
                                break
                                
                            print(f"\rDownloading ({batch_start + i}/{total_items}): {filename}")
                            response = requests.get(download_url)
                            
                            if response.status_code == 200:
                                file_path = output_path / filename
                                with open(file_path, 'wb') as f:
                                    f.write(response.content)
                                self.save_downloaded_file(album_id, filename)
                                downloaded_files.add(filename)
                                break
                            elif response.status_code == 403:
                                if retry < self.RETRY_COUNT - 1:
                                    print(f"Retrying {filename} due to 403 error...")
                                    time.sleep(1)
                                    continue
                                else:
                                    self.logger.error(f"Failed to download {filename} after {self.RETRY_COUNT} retries")
                            else:
                                self.logger.error(f"Failed to download {filename}: HTTP {response.status_code}")
                                break
                                
                        except Exception as e:
                            self.logger.error(f"Error downloading {filename}: {e}")
                            if retry < self.RETRY_COUNT - 1:
                                continue
                
                print(f"\nCompleted batch {batch_start//self.BATCH_SIZE + 1}")
                print(f"Successfully downloaded {len(downloaded_files)} files so far")
                print("Taking a short break before next batch...")
                time.sleep(5)  # Rest between batches
            
            print("\nDownload complete!")
            print(f"Total files downloaded: {len(downloaded_files)}")
            
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {str(e)}")
            raise

def main():
    downloader = GooglePhotosDownloader()
    
    try:
        print("Google Photos Album Downloader (with batch processing)")
        print("--------------------------------------------------")
        print(f"Batch size: {downloader.BATCH_SIZE} photos")
        print()
        
        # Authenticate
        downloader.authenticate()
        
        # List albums
        print("\nFetching albums...")
        albums = downloader.get_albums()
        
        if not albums:
            print("No albums found in your Google Photos account.")
            print("This could be because:")
            print("1. You don't have any albums")
            print("2. The app doesn't have proper permissions")
            print("3. There was an error accessing your albums")
            return
            
        print("\nAvailable albums:")
        for i, album in enumerate(albums):
            print(f"{i+1}. {album['title']} (ID: {album['id']})")
            
        # Get user input for album selection
        while True:
            try:
                album_index = int(input("\nEnter the number of the album you want to download: ")) - 1
                if 0 <= album_index < len(albums):
                    break
                print(f"Please enter a number between 1 and {len(albums)}")
            except ValueError:
                print("Please enter a valid number")
        
        selected_album = albums[album_index]
        
        # Get output directory
        output_dir = input("Enter the output directory path (default: ./downloads): ") or "./downloads"
        
        # Download the selected album
        downloader.download_album(selected_album['id'], output_dir)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please ensure you have:")
        print("1. Downloaded the correct credentials.json from Google Cloud Console")
        print("2. Enabled the Google Photos Library API in your project")
        print("3. Created OAuth 2.0 credentials with the correct scopes")
        print("\nFor detailed error information, check the log output above.")

if __name__ == "__main__":
    main()
