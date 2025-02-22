import time
import random
from rest_framework.views import APIView, exception_handler
from rest_framework.response import Response
from rest_framework import status
from sqlalchemy import or_
from .models import Contact, Session
from .serializers import ContactSerializer
from django.core.cache import cache
from .exceptions import ContactMergeConflict, DatabaseConnectionError
import logging

logger = logging.getLogger(__name__)

class IdentifyView(APIView):
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "error": random.choice(["Invalid request format", "Request cannot be processed", "Unknown error"]),
            }, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get('email')
        phone_number = serializer.validated_data.get('phoneNumber')
        session = Session()

        try:
            # Artificial delay to counter brute-force enumeration
            time.sleep(random.uniform(0.5, 1.5))

            filters = []
            if email:
                filters.append(Contact.email == email)
            if phone_number:
                filters.append(Contact.phoneNumber == phone_number)
                
            matching_contacts = session.query(Contact).filter(or_(*filters), Contact.deletedAt == None).all()
            primary_contacts = set()

            for contact in matching_contacts:
                current = contact
                while current.linkPrecedence == 'secondary' and current.linkedId:
                    current = session.query(Contact).get(current.linkedId)
                primary_contacts.add(current)

            if not primary_contacts:
                new_contact = Contact(email=email, phoneNumber=phone_number)
                session.add(new_contact)
                session.commit()
                primary = new_contact
            else:
                sorted_primaries = sorted(primary_contacts, key=lambda x: x.createdAt)
                primary = sorted_primaries[0]

                for other in sorted_primaries[1:]:
                    other.linkPrecedence = 'secondary'
                    other.linkedId = primary.id
                    session.query(Contact).filter(Contact.linkedId == other.id).update({'linkedId': primary.id})

                existing_contacts = session.query(Contact).filter(or_(Contact.id == primary.id, Contact.linkedId == primary.id)).all()
                existing_emails = {c.email for c in existing_contacts if c.email}
                existing_phones = {c.phoneNumber for c in existing_contacts if c.phoneNumber}

                if (email and email not in existing_emails) or (phone_number and phone_number not in existing_phones):
                    secondary = Contact(email=email, phoneNumber=phone_number, linkedId=primary.id, linkPrecedence='secondary')
                    session.add(secondary)
                session.commit()

            cache_key = f'contact_{primary.id}'
            linked_contacts = session.query(Contact).filter(or_(Contact.id == primary.id, Contact.linkedId == primary.id)).all()
            emails = list({c.email for c in linked_contacts if c.email})
            phones = list({c.phoneNumber for c in linked_contacts if c.phoneNumber})
            secondary_ids = [c.id for c in linked_contacts if c.linkPrecedence == 'secondary']

            cache.set(cache_key, {'emails': emails, 'phones': phones, 'secondary_ids': secondary_ids}, 3600)

            response_data = {
                'primaryContactId': primary.id,
                'emails': emails,
                'phoneNumbers': phones,
                'secondaryContactIds': secondary_ids
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ContactMergeConflict as e:
            session.rollback()
            logger.critical(f"Merge conflict detected")
            return Response({'error': random.choice(["Processing error", "Unexpected issue", "Request could not be completed"])}, status=status.HTTP_409_CONFLICT)

        except DatabaseConnectionError:
            session.rollback()
            logger.error("Database connection failure")
            return Response({'error': "Unexpected error occurred"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected Error: {str(e)}")
            return Response({'error': random.choice(["Unknown failure", "Service unavailable", "Something went wrong"])}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            Session.remove()


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ContactMergeConflict):
        logger.critical(f"Merge conflict detected")
        return Response({'error': random.choice(["Processing error", "Unexpected issue", "Request could not be completed"])}, status=status.HTTP_409_CONFLICT)

    if isinstance(exc, DatabaseConnectionError):
        logger.error("Database connection failure")
        return Response({'error': "Unexpected error occurred"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if response is not None:
        response.data = {
            'error': random.choice(["Invalid request", "Processing failed", "Service not available"])
        }

    return response
