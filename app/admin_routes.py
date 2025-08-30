from flask import Blueprint, request, jsonify, current_app
from app.models import Contact, ProjectInquiry, Portfolio, AdminUser, Subscriber
from app.auth import token_required
from app.email_service import send_email_notification
from app.cloudinary_service import upload_media, delete_media

admin_bp = Blueprint('admin', __name__)

# ==================================================
# Dashboard Statistics Endpoint
# ==================================================
@admin_bp.route('/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats(current_admin):
    """Provides summary statistics for the dashboard homepage."""
    try:
        contacts_count = len(Contact.get_all())
        inquiries_count = len(ProjectInquiry.get_all())
        portfolio_count = len(Portfolio.get_all())
        subscribers_count = len(Subscriber.get_all()) # Added subscriber count
        
        admins_count = 0
        if current_admin.get('is_super_admin', False):
            admins_count = len(AdminUser.get_all())

        stats = {
            "contactsCount": contacts_count,
            "inquiriesCount": inquiries_count,
            "portfolioCount": portfolio_count,
            "subscribersCount": subscribers_count, # Added to response
            "adminsCount": admins_count
        }
        return jsonify({"data": stats, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================================================
# Contacts Management
# ==================================================
@admin_bp.route('/contacts', methods=['GET'])
@token_required
def get_contacts(current_admin):
    try:
        contacts = Contact.get_all()
        return jsonify({"data": contacts, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/contacts/<contact_id>/read', methods=['PUT'])
@token_required
def mark_contact_read(current_admin, contact_id):
    try:
        if not Contact.get_by_id(contact_id):
            return jsonify({"error": "Contact not found"}), 404
        Contact.mark_as_read(contact_id)
        return jsonify({"message": "Contact marked as read", "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/contacts/<contact_id>', methods=['DELETE'])
@token_required
def delete_contact(current_admin, contact_id):
    try:
        if not Contact.get_by_id(contact_id):
            return jsonify({"error": "Contact not found"}), 404
        Contact.delete(contact_id)
        return jsonify({"message": "Contact deleted successfully", "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================================================
# Project Inquiries Management
# ==================================================
@admin_bp.route('/inquiries', methods=['GET'])
@token_required
def get_inquiries(current_admin):
    try:
        inquiries = ProjectInquiry.get_all()
        return jsonify({"data": inquiries, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/inquiries/<inquiry_id>/status', methods=['PUT'])
@token_required
def update_inquiry_status(current_admin, inquiry_id):
    try:
        inquiry = ProjectInquiry.get_by_id(inquiry_id)
        if not inquiry:
            return jsonify({"error": "Inquiry not found"}), 404
        
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({"error": "Status is required"}), 400
        
        ProjectInquiry.update_status(inquiry_id, data['status'])
        
        if data['status'] in ['contacted', 'in_progress', 'completed']:
            send_email_notification(
                subject=f"Update on your project inquiry with Corexify",
                message=f"Hello {inquiry['name']},\n\nThis is an update regarding your project inquiry. The status has been updated to: {data['status']}.\n\nWe will be in touch shortly if any action is needed.\n\nBest regards,\nThe Corexify Team",
                recipient=inquiry['email']
            )
        
        return jsonify({"message": "Inquiry status updated successfully", "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/inquiries/<inquiry_id>', methods=['DELETE'])
@token_required
def delete_inquiry(current_admin, inquiry_id):
    try:
        if not ProjectInquiry.get_by_id(inquiry_id):
            return jsonify({"error": "Inquiry not found"}), 404
        ProjectInquiry.delete(inquiry_id)
        return jsonify({"message": "Inquiry deleted successfully", "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================================================
# Portfolio Management
# ==================================================
@admin_bp.route('/portfolio', methods=['GET'])
@token_required
def get_admin_portfolio(current_admin):
    try:
        portfolio_items = Portfolio.get_all()
        return jsonify({"data": portfolio_items, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/portfolio', methods=['POST'])
@token_required
def create_portfolio_item(current_admin):
    try:
        data = request.form.to_dict()
        required_fields = ['title', 'description', 'technologies', 'category', 'status']
        if not all(k in data for k in required_fields):
            return jsonify({"error": "All text fields are required"}), 400
        
        thumbnail = request.files.get('thumbnailFile')
        video = request.files.get('videoFile')
        
        if not thumbnail or not video:
            return jsonify({"error": "A thumbnail and video file are required"}), 400

        thumb_upload = upload_media(thumbnail, folder="portfolio_thumbnails")
        if not thumb_upload: return jsonify({"error": "Failed to upload thumbnail"}), 500

        video_upload = upload_media(video, folder="portfolio_videos")
        if not video_upload: return jsonify({"error": "Failed to upload video"}), 500

        final_data = {**data}
        final_data['thumbnailUrl'] = thumb_upload.get('secure_url')
        final_data['thumbnail_public_id'] = thumb_upload.get('public_id')
        final_data['videoUrl'] = video_upload.get('secure_url')
        final_data['video_public_id'] = video_upload.get('public_id')
        final_data['technologies'] = [tech.strip() for tech in data.get('technologies', '').split(',')]

        portfolio_id = Portfolio.create(final_data)
        return jsonify({"message": "Portfolio item created", "id": portfolio_id, "status": "success"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/portfolio/<portfolio_id>', methods=['PUT'])
@token_required
def update_portfolio_item(current_admin, portfolio_id):
    try:
        portfolio_item = Portfolio.get_by_id(portfolio_id)
        if not portfolio_item:
            return jsonify({"error": "Portfolio item not found"}), 404
        
        data = request.form.to_dict()
        thumbnail = request.files.get('thumbnailFile')
        video = request.files.get('videoFile')

        if thumbnail:
            if portfolio_item.get('thumbnail_public_id'):
                delete_media(portfolio_item['thumbnail_public_id'], resource_type="image")
            thumb_upload = upload_media(thumbnail, folder="portfolio_thumbnails")
            if not thumb_upload: return jsonify({"error": "Failed to upload new thumbnail"}), 500
            data['thumbnailUrl'] = thumb_upload.get('secure_url')
            data['thumbnail_public_id'] = thumb_upload.get('public_id')

        if video:
            if portfolio_item.get('video_public_id'):
                delete_media(portfolio_item['video_public_id'], resource_type="video")
            video_upload = upload_media(video, folder="portfolio_videos")
            if not video_upload: return jsonify({"error": "Failed to upload new video"}), 500
            data['videoUrl'] = video_upload.get('secure_url')
            data['video_public_id'] = video_upload.get('public_id')

        if 'technologies' in data:
            data['technologies'] = [tech.strip() for tech in data.get('technologies', '').split(',')]

        Portfolio.update(portfolio_id, data)
        return jsonify({"message": "Portfolio item updated", "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/portfolio/<portfolio_id>', methods=['DELETE'])
@token_required
def delete_portfolio_item(current_admin, portfolio_id):
    try:
        portfolio_item = Portfolio.get_by_id(portfolio_id)
        if not portfolio_item:
            return jsonify({"error": "Portfolio item not found"}), 404
        
        if portfolio_item.get('thumbnail_public_id'):
            delete_media(public_id=portfolio_item['thumbnail_public_id'], resource_type="image")

        if portfolio_item.get('video_public_id'):
            delete_media(public_id=portfolio_item['video_public_id'], resource_type="video")

        Portfolio.delete(portfolio_id)
        return jsonify({"message": "Portfolio item deleted", "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================================================
# Admin Users Management
# ==================================================
@admin_bp.route('/admins', methods=['GET'])
@token_required
def get_admins(current_admin):
    try:
        if not current_admin.get('is_super_admin', False):
            return jsonify({"error": "Only super admins can view admin users"}), 403
        
        admins = AdminUser.get_all()
        return jsonify({"data": admins, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admins/<admin_id>', methods=['DELETE'])
@token_required
def delete_admin(current_admin, admin_id):
    try:
        if not current_admin.get('is_super_admin', False):
            return jsonify({"error": "Authorization failed: Only super admins can delete users"}), 403
        
        if str(current_admin.get('id')) == str(admin_id):
            return jsonify({"error": "You cannot delete your own account"}), 400
        
        admin_to_delete = AdminUser.get_by_id(admin_id)
        if not admin_to_delete:
            return jsonify({"error": "Admin not found"}), 404
        
        if admin_to_delete.get('email') == current_app.config['SUPER_ADMIN_EMAIL']:
            return jsonify({"error": "The primary super admin account cannot be deleted"}), 403

        AdminUser.delete(admin_id)
        return jsonify({"message": "Admin user deleted successfully", "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================================================
# Subscribers Management (NEW SECTION)
# ==================================================
@admin_bp.route('/subscribers', methods=['GET'])
@token_required
def get_subscribers(current_admin):
    """Fetches all newsletter subscribers."""
    try:
        subscribers = Subscriber.get_all()
        return jsonify({"data": subscribers, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/subscribers/<subscriber_id>', methods=['DELETE'])
@token_required
def delete_subscriber(current_admin, subscriber_id):
    """Deletes a specific subscriber."""
    try:
        # Check if the subscriber exists before attempting deletion
        subscriber = Subscriber.get_by_id(subscriber_id) # Assumes get_by_id exists
        if not subscriber:
            return jsonify({"error": "Subscriber not found"}), 404
            
        Subscriber.delete(subscriber_id)
        return jsonify({"message": "Subscriber deleted successfully", "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

