from drf_standardized_errors.formatter import ExceptionFormatter
from drf_standardized_errors.types import ErrorResponse


class MyExceptionFormatter(ExceptionFormatter):
    def format_error_response(self, error_response: ErrorResponse):
        error = error_response.errors[0]

        if error_response.type == "validation_error" and error.attr != "non_field_errors" and error.attr != None:
            return {
                "success": False,
                "type": error_response.type,
                "code": error.code,
                "error": f"{error.attr}: {error.detail}",
                "field_name": error.attr
            }
        return {
            "success": False,
            "type": error_response.type,
            "code": error.code,
            "error": error.detail
        }
