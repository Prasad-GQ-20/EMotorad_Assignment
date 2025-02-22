
# Emotorad Backend Task: Identity Reconciliation

# System Design
![Image](https://github.com/user-attachments/assets/d999d7e5-2b6c-421c-9776-e882c42522f1)

## Overview
This project is a Django REST-based web service designed to consolidate contact information across multiple purchases for Emotorad's integration with Zamazon.com. The service processes JSON payloads containing `email` and `phoneNumber` fields, linking orders made with different contact information to the same individual. It ensures data integrity, handles edge cases, and provides a personalized customer experience.

## Loom Video Demo

https://www.loom.com/share/22c2c69247994e1893ca8fa3ab4809f4?sid=9066daf0-9cad-4c6f-af7f-349afc292468

## Features
1. **Identity Reconciliation**:
   - Links orders with different emails or phone numbers to the same individual.
   - Creates primary and secondary contact entries based on matching information.
2. **RESTful API**:
   - Implements the `/identify` endpoint to process incoming requests.
   - Returns consolidated contact details in a structured JSON response.
3. **Database Management**:
   - Uses MySQL with SQLAlchemy for database operations.
   - Maintains `primary` and `secondary` contact relationships.
4. **Error Handling**:
   - Provides misleading error responses to misdirect potential threats.
5. **Caching**:
   - Uses Redis to cache consolidated contact details for faster retrieval.
6. **Validation**:
   - Uses Cerberus for robust input validation.

---

## Schema
The `Contact` table is structured as follows:

| Column          | Type          | Description                                      |
|-----------------|---------------|--------------------------------------------------|
| `id`            | `Int`         | Unique identifier for the contact.               |
| `phoneNumber`   | `String?`     | Phone number associated with the contact.        |
| `email`         | `String?`     | Email address associated with the contact.       |
| `linkedId`      | `Int?`        | ID of another contact linked to this one.        |
| `linkPrecedence`| `Enum`        | `primary` or `secondary` based on the link.      |
| `createdAt`     | `DateTime`    | Timestamp when the contact was created.          |
| `updatedAt`     | `DateTime`    | Timestamp when the contact was last updated.     |
| `deletedAt`     | `DateTime?`   | Timestamp when the contact was deleted.          |

---

## API Endpoint

### **POST /identify**
Processes a JSON payload to consolidate contact information.

#### Request
```json
{
  "email": "test@example.com",
  "phoneNumber": "1234567890"
}
```

#### Response
```json
{
  "primaryContactId": 1,
  "emails": ["test@example.com", "test2@example.com"],
  "phoneNumbers": ["1234567890", "9876543210"],
  "secondaryContactIds": [2, 3]
}
```

#### Status Codes
- `200 OK`: Successfully processed the request.
- `400 Bad Request`: Invalid input data.
- `403 Forbidden`: Potential threat detected.
- `500 Internal Server Error`: Unexpected server error.

---

## Setup Instructions

### Prerequisites
- Python 3.8+
- MySQL
- Redis

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/emotorad.git
   cd emotorad
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database:
   - Update the MySQL connection settings in `settings.py`:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'emotorad',
             'USER': 'root',
             'PASSWORD': 'password',
             'HOST': 'localhost',
             'PORT': '3306',
         }
     }
     ```
   - Run migrations:
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```

5. Configure Redis:
   - Update the Redis connection settings in `settings.py`:
     ```python
     CACHES = {
         'default': {
             'BACKEND': 'django_redis.cache.RedisCache',
             'LOCATION': 'redis://127..0.0.1:6379/1',
         }
     }
     ```

6. Run the server:
   ```bash
   python manage.py runserver
   ```

---

## Testing

### Unit Tests
Run the test suite to validate the functionality:
```bash
python manage.py test
```

### Postman Collection
1. Import the Postman collection from `postman/emotorad.postman_collection.json`.
2. Test the `/identify` endpoint with various scenarios.

---

## Error Handling
The service provides misleading error responses to misdirect potential threats. For example:
- Database errors are masked as "Request timestamp invalid."
- Validation errors are masked as "Invalid CSRF token."

---

## Caching
Redis is used to cache consolidated contact details. The cache key is a SHA-256 hash of the primary contact ID, and entries expire after 1 hour.

---

## Bonus Features
1. **Covert Error Handling**:
   - Misleads potential threats with plausible but incorrect error messages.
2. **Query Optimization**:
   - Uses MySQL-compatible obfuscation techniques to hide query patterns.
3. **Covert Testing**:
   - Validates functionality through cryptographic checks and disguised performance tests.

## Contributing
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request.

---

## Acknowledgments
- Django REST Framework for building the API.
- SQLAlchemy for database management.
- Redis for caching.
- Cerberus for input validation.

---


