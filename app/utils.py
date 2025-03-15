import os

def get_uploaded_images(upload_folder):
    images = []
    for subdir, dirs, files in os.walk(upload_folder):
        for file in files:
            images.append(file)
    return images