from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    """Custom exception handler for DRF (specified in ``settings.py``).
    Main use:
        > handling of django.core.ValidationError for better json returns of API
    """
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, "message_dict"):
            exc = DRFValidationError(detail={"error": exc.message_dict})
        elif hasattr(exc, "message"):
            exc = DRFValidationError(detail={"error": exc.message})
        elif hasattr(exc, "messages"):
            exc = DRFValidationError(detail={"error": exc.messages})

    return drf_exception_handler(exc, context)