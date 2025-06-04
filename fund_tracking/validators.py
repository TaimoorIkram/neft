from django.core.exceptions import ValidationError
from stdnum import iban

def validate_iban(value):
    """
    Validate an IBAN using the `python-stdnum` library.
    """
    if not iban.is_valid(value):
        raise ValidationError(f"{value} is not a valid IBAN.")
