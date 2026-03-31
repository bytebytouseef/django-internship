from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler — wraps ALL errors in a consistent format:

    {
        "success": false,
        "error": {
            "code": "not_found",
            "message": "No Product matches the given query.",
            "details": {...}
        },
        "status_code": 404
    }

    Without this, DRF returns different shapes for different errors,
    making frontend handling unpredictable.

    context = {'view': view_instance, 'request': request}
    """
    # Call DRF's default handler first — it handles most exceptions
    response = exception_handler(exc, context)

    if response is not None:
        # Get the error code from the exception class name
        error_code = exc.__class__.__name__.lower().replace('exception', '').replace('error', '')

        # Extract detailed errors if available (e.g., validation errors)
        details = None
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                details = exc.detail
            elif isinstance(exc.detail, list):
                details = {'non_field_errors': exc.detail}

        # Build our consistent error envelope
        custom_response = {
            'success': False,
            'error': {
                'code': error_code or 'error',
                'message': _get_error_message(exc),
                'details': details,
            },
            'status_code': response.status_code,
        }

        response.data = custom_response

        # Log server errors
        if response.status_code >= 500:
            logger.error(f'Server error: {exc}', exc_info=True)

    return response


def _get_error_message(exc):
    """Extract a clean string message from any exception type."""
    if hasattr(exc, 'detail'):
        detail = exc.detail
        if isinstance(detail, str):
            return detail
        if isinstance(detail, list) and detail:
            return str(detail[0])
        if isinstance(detail, dict):
            # Get first error message from dict
            first_key = next(iter(detail))
            first_val = detail[first_key]
            if isinstance(first_val, list) and first_val:
                return f'{first_key}: {first_val[0]}'
            return str(first_val)
    return str(exc)