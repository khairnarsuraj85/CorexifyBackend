# app/cloudinary_service.py
import cloudinary
import cloudinary.uploader
import cloudinary.api

def upload_media(file_to_upload, folder):
    """
    Uploads a file to Cloudinary.
    Determines resource_type (image/video) automatically.
    """
    try:
        # The uploader can automatically detect the resource type
        upload_result = cloudinary.uploader.upload(
            file_to_upload,
            folder=folder,
            resource_type="auto"
        )
        return upload_result
    except Exception as e:
        print(f"Cloudinary Upload Error: {e}")
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
        print(f"Cloudinary Deletion Error: {e}")
        return None