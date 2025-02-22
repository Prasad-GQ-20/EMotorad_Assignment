from rest_framework import serializers
import re
import tldextract

TEMP_EMAIL_DOMAINS = {
    "tempmail.com", "mailinator.com", "guerrillamail.com", "10minutemail.com",
    "throwawaymail.com", "sharklasers.com", "yopmail.com", "fakeinbox.com"
}

VALID_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com",
    "icloud.com", "zoho.com", "aol.com", "gmx.com"
}

class ContactSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_null=True)
    phoneNumber = serializers.CharField(required=False, allow_null=True, max_length=10)

    def validate_email(self, value):
        if value:
            # Extract domain from email
            domain = value.split('@')[-1].lower()
            
            # Check if the domain is a temporary email provider
            if domain in TEMP_EMAIL_DOMAINS:
                raise serializers.ValidationError("Temporary email addresses are not allowed")

            extracted = tldextract.extract(value)
            root_domain = f"{extracted.domain}.{extracted.suffix}"

            # Check if the root domain is valid
            if root_domain not in VALID_EMAIL_DOMAINS:
                raise serializers.ValidationError("Please use a valid email provider")

            # Ensure the email format is correct
            email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_regex, value):
                raise serializers.ValidationError("Invalid email format")

        return value

    def validate_phoneNumber(self, value):
        if value:
            if not re.match(r'^\d{10}$', value):
                raise serializers.ValidationError("Phone number must be exactly 10 digits")
        return value

    def validate(self, data):
        if not data.get('email') and not data.get('phoneNumber'):
            raise serializers.ValidationError("At least one contact detail is required")
        return data
