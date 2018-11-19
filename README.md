# watch-out
Camera Picture Upload To Google Drive Program

This program can handle 1 to 8 cameras. Its purpose is to capture pictures from a camera stream and regularly copy them to a local folder meant to be a Google Drive folder so it can be viewed and/or shared online. But you can pick any local folder.

For users on metered connections, there is a data usage cap and margin which can be set at which point the program will stop copying pictures.

The cameras can be configured individually and have two picture upload types:
- snapshot (overwritten each time)
- backup (deleted after a configured expiry)

Each cameras can be configured individually for:
- picture format (YUV types)
- resolution
- greyscale
- snapshot, backup upload interval
- camera master enable based on day time schedule
- camera protocol

# Installation Notes

Requirements:
- Windows or Linux (Tested on both)
- Python 3 (Tested/developed with Python 3.7)
    - Python needs to be in your system's path
- Python 3 PyQt5
- FFMPEG (Tested/developed with ffmpeg-4.0.2-win64-static on Windows, ffmpeg 4.0.2 on Ubuntu 18.04 LTS)
    - FFMPEG needs to be installed in specific folder (look at watch_out_lib/WatchOutSettings.py:self.ffmpeg_binary_path)
- When data cap is reached, a pre-defined picture is copied in the snapshot folder, you need to create that picture and put it in specific folder (look at watch_out_lib/WatchOutSettings.py:self.data_cap_reached_picture_{name|path}

All your cameras don't need to have the same password or any password at all. You still need to provide a password on the command line. If no passwords are necessary, you may enter anything. Each camera's password may be hardcoded through the configuration tool or you may use a tag in the camera's configurator URL which will be replaced by the password specified on the command line.

# Configuring
In the project's root folder, run:
    python3 configurator.py

# Launching picture grabbing
In the project's root folder, run:
    python3 watch-out.py <camera password>
