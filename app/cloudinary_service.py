import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import current_app

def upload_media(file_to_upload, folder):
    """
    Uploads a file to Cloudinary.
    Determines resource_type (image/video/raw) based on the file's content type.
    """
    try:
        # --- ADDED: Logic to determine the correct resource type ---
        content_type = file_to_upload.content_type
        
        if 'image' in content_type:
            resource_type = 'image'
        elif 'video' in content_type:
            resource_type = 'video'
        else:
            # Default to 'raw' for documents like PDF, DOCX, etc.
            resource_type = 'raw'

        current_app.logger.info(f"Uploading {file_to_upload.filename} as resource_type: {resource_type}")

        # The uploader now uses the explicitly determined resource type
        upload_result = cloudinary.uploader.upload(
            file_to_upload,
            folder=folder,
            resource_type=resource_type
        )
        return upload_result
    except Exception as e:
        current_app.logger.error(f"Cloudinary Upload Error: {e}")
        return None

def delete_media(public_id, resource_type="image"):
    """
    Deletes a file from Cloudinary using its public ID.
    """
    try:
        result = cloudinary.uploader.destroy(
            public_id,
            resource_type=resource_type
        )
        return result
    except Exception as e:
        current_app.logger.error(f"Cloudinary Deletion Error: {e}")
        return None