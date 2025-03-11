# Google Photos Album Downloader

A robust Python utility for downloading all your Google Photos albums and media with batch processing capability to efficiently handle large collections.

## Features

- Download options for flexibility:
  - Download all albums at once
  - Download multiple selected albums at once
  - Download a single specific album
- Batch processing to handle large collections efficiently
- Resume capability (skips previously downloaded files)
- Maintains a download log to track progress
- Retry mechanism for failed downloads
- Support for multiple Google accounts (token-based authentication)

## Prerequisites

- Python 3.6+
- Google Cloud Platform account with Google Photos Library API enabled
- OAuth 2.0 credentials

## Installation

1. Clone this repository or download the script.

2. Install required dependencies:

```bash
pip install google-auth-oauthlib google-api-python-client requests
```

3. Set up Google Cloud Platform:

   a. Go to [Google Cloud Console](https://console.cloud.google.com/)
   
   b. Create a new project
   
   c. Enable the "Google Photos Library API"
   
   d. Create OAuth 2.0 credentials:
      - Go to "APIs & Services" > "Credentials"
      - Click "Create Credentials" > "OAuth client ID"
      - Set Application type to "Desktop application"
      - Download the JSON file and save it as `credentials.json` in the same directory as the script

## Usage

Run the script:

```bash
python google_photos_downloader.py
```

### Authentication

1. Enter your Google email address when prompted
2. A browser window will open for you to sign in to your Google account and grant permissions
3. After successful authentication, a token will be saved locally for future use

### Downloading Albums

The script offers three options:

1. Download all albums:
   - Enter 'a' when prompted
   - All albums will be downloaded to separate folders inside the output directory

2. Download multiple albums:
   - Enter 'm' when prompted
   - Enter the numbers of the albums you want to download, separated by commas (e.g., "1,3,5")
   - The selected albums will be downloaded to separate folders inside the output directory

3. Download a specific album:
   - Enter 's' when prompted
   - Select an album from the displayed list by entering its number
   - The selected album will be downloaded to a folder inside the output directory

### Output Directory

By default, files are downloaded to a `./downloads` directory. You can specify a custom path when prompted.

## How It Works

1. **Authentication**: Uses OAuth 2.0 to securely access your Google Photos account
2. **Album Discovery**: Fetches the list of all available albums
3. **Album Selection**: Provides options to download all albums, multiple specific albums, or a single album
4. **Media Processing**: Downloads media items in batches (default 500 items per batch)
5. **Download Tracking**: Maintains a log of downloaded files to support resuming interrupted downloads
6. **Error Handling**: Implements retries for failed downloads and handles API errors gracefully

## Batch Processing

The script processes media in batches of 500 items by default. This helps:
- Reduce memory usage for large albums
- Provide progress updates
- Allow interrupting and resuming downloads later
- Prevent timeouts for very large collections

## Troubleshooting

If you encounter issues:

- Ensure `credentials.json` is correctly downloaded from Google Cloud Console
- Verify the Google Photos Library API is enabled in your GCP project
- Check that your OAuth 2.0 credentials have the correct scopes
- Look for detailed error information in the console output
- Delete the token file (e.g., `token_your_email_at_gmail_com.pickle`) to force re-authentication

## Limitations

- Video files might be downloaded in a reduced quality format due to Google Photos API limitations
- Some shared albums might not be accessible depending on permissions
- The script honors Google's API quota limits, which may affect download speed

## Security Note

The `credentials.json` file and generated token files contain sensitive information. Keep them secure and do not share them.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests if you have suggestions for improvements.

## License

[MIT License](LICENSE)