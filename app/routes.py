from flask import Blueprint, request, jsonify
from app.models import Contact, ProjectInquiry, Portfolio, Subscriber
from app.utils import validate_email, validate_phone
from app.email_service import send_email_notification
from app.cloudinary_service import upload_media
import json

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return jsonify({"message": "Flask Backend is Running!", "status": "success"})

@main.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        if not validate_email(data['email']):
            return jsonify({"error": "Invalid email address"}), 400
        
        contact_id = Contact.create(data)
        
        # --- ENHANCED ADMIN NOTIFICATION ---
        email_subject = f"📬 New Contact Form Submission from {data['name']}"
        email_message = f"""
        You have a new contact form submission:

        --- Contact Details ---
        Name: {data.get('name')}
        Email: {data.get('email')}

        --- Message ---
        {data.get('message')}

        ---
        You can view this contact in your admin dashboard.
        """
        send_email_notification(
            subject=email_subject,
            message=email_message
        )
        
        return jsonify({
            "message": "Contact form submitted successfully",
            "id": contact_id,
            "status": "success"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/api/project-inquiry', methods=['POST'])
def project_inquiry():
    try:
        data = request.form.to_dict()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ['name', 'email', 'phone', 'country', 'clientType', 'domain', 'projectType', 'timeline', 'budget', 'message']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        if not validate_email(data['email']):
            return jsonify({"error": "Invalid email address"}), 400
        
        if not validate_phone(data['phone']):
            return jsonify({"error": "Invalid phone number"}), 400
        
        uploaded_files_urls = []
        files = request.files.getlist('files')
        
        if files:
            for file in files:
                if file and file.filename:
                    upload_result = upload_media(file, folder="project_inquiries")
                    if upload_result and "secure_url" in upload_result:
                        uploaded_files_urls.append(upload_result["secure_url"])
        
        data['attached_files'] = uploaded_files_urls
        
        inquiry_id = ProjectInquiry.create(data)
        
        # --- COMPREHENSIVE ADMIN NOTIFICATION WITH FILE LINKS ---
        email_subject = f"🚀 New Project Inquiry: {data.get('projectType')} from {data.get('name')}"
        
        # Build the list of file links for the email body
        file_links = ""
        if uploaded_files_urls:
            for i, url in enumerate(uploaded_files_urls):
                file_links += f"  - File {i+1}: {url}\n"
        else:
            file_links = "No files were attached."

        email_message = f"""
        You've received a new project inquiry!

        --- Personal & Company Details ---
        Name: {data.get('name')}
        Email: {data.get('email')}
        Phone: {data.get('phone')}
        Location: {data.get('city', 'N/A')}, {data.get('state', 'N/A')}, {data.get('country')}
        Company: {data.get('company', 'N/A')}

        --- Project Details ---
        Client Type: {data.get('clientType')}
        Final Year Project: {data.get('isFinalYearProject', 'N/A')}
        Domain: {data.get('domain')}
        Project Type: {data.get('projectType')}

        --- Timeline & Budget ---
        Expected Start Date: {data.get('startDate', 'Not Specified')}
        Timeline: {data.get('timeline')}
        Budget: {data.get('budget')}

        --- Project Description ---
        {data.get('message')}

        --- Attached Files ---
        {file_links}
        ---

        You can view the full details of this inquiry in your admin dashboard.
        """

        send_email_notification(
            subject=email_subject,
            message=email_message
        )
        
        return jsonify({
            "message": "Project inquiry submitted successfully",
            "id": inquiry_id,
            "status": "success"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    try:
        portfolio_items = Portfolio.get_all()
        return jsonify({
            "data": portfolio_items,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/api/portfolio/<portfolio_id>', methods=['GET'])
def get_portfolio_item(portfolio_id):
    try:
        portfolio_item = Portfolio.get_by_id(portfolio_id)
        if not portfolio_item:
            return jsonify({"error": "Portfolio item not found"}), 404
        
        return jsonify({
            "data": portfolio_item,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/api/subscribe', methods=['POST'])
def subscribe_newsletter():
    try:
        data = request.get_json()
        if not data or not data.get('email'):
            return jsonify({"error": "Email is required"}), 400

        email = data['email']
        if not validate_email(email):
            return jsonify({"error": "Invalid email address"}), 400

        subscriber_id = Subscriber.create(email)

        if subscriber_id is None:
            return jsonify({"message": "You are already subscribed!", "status": "exists"}), 200

        # Send a welcome email to the new subscriber
        send_email_notification(
            subject="🎉 Thanks for Subscribing to Corexify!",
            message="Welcome to our newsletter! You'll now be the first to know about our latest projects, services, and offers.",
            recipient=email
        )
        
        # --- ENHANCED ADMIN NOTIFICATION ---
        admin_email_subject = "📬 New Newsletter Subscriber"
        admin_email_message = f"""
        A new user has subscribed to your newsletter.

        --- Subscriber Details ---
        Email: {email}
        
        You can manage all subscribers from your admin dashboard.
        """
        send_email_notification(
            subject=admin_email_subject,
            message=admin_email_message
        )

        return jsonify({
            "message": "Successfully subscribed to the newsletter!",
            "id": subscriber_id,
            "status": "success"
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
