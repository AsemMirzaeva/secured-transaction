import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger("apps")


def custom_exception_handler(exc, context):
   
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "error": {
                "detail": response.data,
                "status_code": response.status_code,
            }
        }
        return response

    logger.exception("Unhandled exception in %s", context.get("view"))
    return Response(
        {"error": {"detail": "Ichki server xatoligi yuz berdi.", "status_code": 500}},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )