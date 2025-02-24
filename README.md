# Google Photos Album Downloader

A Python script to batch download all photos and videos from your Google Photos albums. This tool allows you to:
- List all your Google Photos albums
- Select an album to download
- Download all media items from the selected album with automatic retries
- Track downloaded files to resume interrupted downloads
- Process large albums in batches to handle rate limits

## Prerequisites

- Python 3.7 or higher
- A Google Cloud Project with the Photos Library API enabled
- OAuth 2.0 credentials from Google Cloud Console

## Setup

1. Clone this repository:
```bash
git clone https://github.com/muniu/google-photos-downloader.git
cd google-photos-downloader
```

2. Install required dependencies:
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
```

3. Set up Google Cloud Console:
   1. Go to [Google Cloud Console](https://console.cloud.google.com/)
   2. Create a new project or select an existing one
   3. Enable the Photos Library API:
      - Navigate to "APIs & Services" > "Library"
      - Search for "Photos Library API"
      - Click "Enable"
   4. Configure OAuth consent screen:
      - Go to "APIs & Services" > "OAuth consent screen"
      - Select "External" user type
      - Fill in the required fields (app name, user support email, developer contact)
      - Add the email addresses that will use the application under "Test users"
   5. Create OAuth credentials:
      - Go to "APIs & Services" > "Credentials"
      - Click "Create Credentials" > "OAuth client ID"
      - Select "Desktop application" as the application type
      - Name your client
      - Click "Create"
   6. Download the credentials:
      - Find your newly created OAuth 2.0 Client ID
      - Click the download icon (⬇️)
      - Save the file as `credentials.json` in the same directory as the script

## Usage

1. Place the `credentials.json` file in the same directory as the script.

2. Run the script:
```bash
python google-photos-downloader-final.py
```

3. Follow the interactive prompts:
   - Enter your Google email address
   - Authenticate through your browser when prompted
   - Select an album from the displayed list
   - Specify an output directory (defaults to ./downloads)

## Features

- **Batch Processing**: Downloads files in batches of 500 to handle rate limits
- **Resume Support**: Tracks downloaded files to resume interrupted downloads
- **Automatic Retries**: Retries failed downloads up to 3 times
- **Progress Tracking**: Shows real-time download progress
- **Error Handling**: Comprehensive error handling and logging

## File Structure

- `google-photos-downloader-final.py`: Main script
- `credentials.json`: OAuth 2.0 credentials from Google Cloud Console
- `token_{email}.pickle`: Stored authentication tokens (created automatically)
- `downloaded_files.json`: Tracks successfully downloaded files
- `downloads/`: Default directory for downloaded media (created automatically)

## Troubleshooting

If you encounter errors:

1. **Authentication Errors**:
   - Ensure `credentials.json` is in the correct location
   - Verify you've enabled the Photos Library API
   - Check that your email is added as a test user in the OAuth consent screen

2. **Permission Errors**:
   - Make sure you've granted all required permissions during the OAuth flow
   - Check if the output directory is writable

3. **Rate Limit Errors**:
   - The script automatically handles rate limits with retries
   - If persistent, try reducing the `BATCH_SIZE` in the code

4. **Download Errors**:
   - Check your internet connection
   - Verify you have enough disk space
   - The script will automatically retry failed downloads

## Notes

- The first run will open your browser for authentication
- Subsequent runs will use stored credentials unless they expire
- Downloads are tracked and can be resumed if interrupted
- Large albums are processed in batches with breaks between batches
- The script creates a separate token file for each Google account

## Contributing

Feel free to open issues or submit pull requests on the [GitHub repository](https://github.com/muniu/google-photos-downloader).

## License

This project is open source and available under the MIT License.
