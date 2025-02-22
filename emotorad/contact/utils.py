from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # If the response contains validation errors, structure the response accordingly
        errors = response.data
        formatted_errors = {}

        for field, messages in errors.items():
            formatted_errors[field] = messages if isinstance(messages, list) else [messages]

        response.data = {
            "error": "Invalid request",
            "details": formatted_errors  # Includes specific invalid fields and messages
        }

    return response
