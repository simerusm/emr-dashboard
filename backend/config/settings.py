import os

# Define allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif'}

# Define the temporary upload folder
# You can set this to a specific path or use a relative path
TEMP_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

# Ensure the upload folder exists
if not os.path.exists(TEMP_UPLOAD_FOLDER):
    os.makedirs(TEMP_UPLOAD_FOLDER)