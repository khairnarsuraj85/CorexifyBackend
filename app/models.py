from datetime import datetime
from app.firebase import get_db

db = get_db()

class Contact:
    @staticmethod
    def create(contact_data):
        contact_ref = db.collection('contacts').document()
        contact_data['created_at'] = datetime.now()
        contact_data['read'] = False
        contact_ref.set(contact_data)
        return contact_ref.id

    @staticmethod
    def get_all(limit=100):
        contacts_ref = db.collection('contacts').order_by('created_at', direction='DESCENDING').limit(limit)
        return [{'id': doc.id, **doc.to_dict()} for doc in contacts_ref.stream()]

    @staticmethod
    def get_by_id(contact_id):
        contact_ref = db.collection('contacts').document(contact_id)
        contact = contact_ref.get()
        if contact.exists:
            return {'id': contact.id, **contact.to_dict()}
        return None

    @staticmethod
    def mark_as_read(contact_id):
        contact_ref = db.collection('contacts').document(contact_id)
        contact_ref.update({'read': True})

    @staticmethod
    def delete(contact_id):
        db.collection('contacts').document(contact_id).delete()

class ProjectInquiry:
    @staticmethod
    def create(inquiry_data):
        inquiry_ref = db.collection('project_inquiries').document()
        inquiry_data['created_at'] = datetime.now()
        inquiry_data['status'] = 'new'
        inquiry_ref.set(inquiry_data)
        return inquiry_ref.id

    @staticmethod
    def get_all(limit=100):
        inquiries_ref = db.collection('project_inquiries').order_by('created_at', direction='DESCENDING').limit(limit)
        return [{'id': doc.id, **doc.to_dict()} for doc in inquiries_ref.stream()]

    @staticmethod
    def get_by_id(inquiry_id):
        inquiry_ref = db.collection('project_inquiries').document(inquiry_id)
        inquiry = inquiry_ref.get()
        if inquiry.exists:
            return {'id': inquiry.id, **inquiry.to_dict()}
        return None

    @staticmethod
    def update_status(inquiry_id, status):
        inquiry_ref = db.collection('project_inquiries').document(inquiry_id)
        inquiry_ref.update({'status': status})

    @staticmethod
    def delete(inquiry_id):
        db.collection('project_inquiries').document(inquiry_id).delete()

class Portfolio:
    @staticmethod
    def get_all():
        portfolio_ref = db.collection('portfolio').order_by('created_at', direction='DESCENDING')
        return [{'id': doc.id, **doc.to_dict()} for doc in portfolio_ref.stream()]

    @staticmethod
    def get_by_id(portfolio_id):
        portfolio_ref = db.collection('portfolio').document(portfolio_id)
        portfolio = portfolio_ref.get()
        if portfolio.exists:
            return {'id': portfolio.id, **portfolio.to_dict()}
        return None

    @staticmethod
    def create(portfolio_data):
        portfolio_ref = db.collection('portfolio').document()
        portfolio_data['created_at'] = datetime.now()
        portfolio_data['updated_at'] = datetime.now()
        portfolio_ref.set(portfolio_data)
        return portfolio_ref.id

    @staticmethod
    def update(portfolio_id, updates):
        portfolio_ref = db.collection('portfolio').document(portfolio_id)
        updates['updated_at'] = datetime.now()
        portfolio_ref.update(updates)

    @staticmethod
    def delete(portfolio_id):
        db.collection('portfolio').document(portfolio_id).delete()

class AdminUser:
    @staticmethod
    def create(admin_data):
        admin_ref = db.collection('admin_users').document()
        admin_data['created_at'] = datetime.now()
        admin_ref.set(admin_data)
        return admin_ref.id

    @staticmethod
    def get_all():
        admin_ref = db.collection('admin_users')
        admins = []
        for doc in admin_ref.stream():
            admin_data = doc.to_dict()
            admin_data['id'] = doc.id
            admin_data.pop('password_hash', None)
            admins.append(admin_data)
        return admins

    @staticmethod
    def get_by_email(email):
        admin_ref = db.collection('admin_users').where('email', '==', email.lower()).limit(1)
        admins = [{'id': doc.id, **doc.to_dict()} for doc in admin_ref.stream()]
        return admins[0] if admins else None

    @staticmethod
    def get_by_id(admin_id):
        admin_ref = db.collection('admin_users').document(admin_id)
        admin = admin_ref.get()
        if admin.exists:
            admin_data = admin.to_dict()
            admin_data['id'] = admin.id
            return admin_data
        return None
    
    @staticmethod
    def delete(admin_id):
        db.collection('admin_users').document(admin_id).delete()

class Subscriber:
    @staticmethod
    def create(email):
        existing = db.collection('subscribers').where('email', '==', email.lower()).limit(1).get()
        if len(list(existing)) > 0:
            return None

        subscriber_ref = db.collection('subscribers').document()
        subscriber_data = {
            'email': email.lower(),
            'subscribed_at': datetime.now()
        }
        subscriber_ref.set(subscriber_data)
        return subscriber_ref.id
        
    @staticmethod
    def get_all(limit=500):
        subscribers_ref = db.collection('subscribers').order_by('subscribed_at', direction='DESCENDING').limit(limit)
        return [{'id': doc.id, **doc.to_dict()} for doc in subscribers_ref.stream()]

    # --- THIS METHOD WAS MISSING ---
    @staticmethod
    def get_by_id(subscriber_id):
        """Retrieves a single subscriber by their document ID."""
        subscriber_ref = db.collection('subscribers').document(subscriber_id)
        subscriber = subscriber_ref.get()
        if subscriber.exists:
            return {'id': subscriber.id, **subscriber.to_dict()}
        return None

    @staticmethod
    def delete(subscriber_id):
        db.collection('subscribers').document(subscriber_id).delete()