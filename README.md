# watch-out
Camera Picture Upload To Google Drive Program

This program can handle 1 to 8 cameras. Its purpose is to capture pictures from a camera stream and regularly copy them to a local folder meant to be a Google Drive folder so it can be viewed and/or shared online. But you can pick any local folder.

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
