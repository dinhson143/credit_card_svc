import re
from fastapi.responses import JSONResponse
from typing import Optional

from src.services.luhn_service import is_valid_luhn, get_card_scheme
from src.utils.logging import logger, mask_card


class CreditCardService:

    def validate(self, number: str):
        cleaned_number = self.clean_number(number)
        try:
            error_response = CreditCardService.validate_integrity(cleaned_number)
            if error_response:
                return error_response

            # Luhn Algorithm
            is_valid = is_valid_luhn(cleaned_number)

            # Get card scheme
            scheme = get_card_scheme(cleaned_number)

            if not is_valid:
                logger.error(f"[CreditCardService] - [CARD_NUMBER: {mask_card(cleaned_number)}] - FAILED: Invalid credit card number")
                return JSONResponse(status_code=400, content={"error": "Invalid credit card number"})

            logger.error(f"[CreditCardService] - [CARD_NUMBER: {mask_card(cleaned_number)}] - SUCCESSFULLY")
            return JSONResponse(status_code=200, content={"valid": True, "scheme": scheme, "message": "OK"})
        except Exception as ex:
            logger.error(f"[CreditCardService] - [CARD_NUMBER: {mask_card(cleaned_number)}] - FAILED: {ex}")
            return JSONResponse(status_code=500, content={"error": "Internal server error"})


    @staticmethod
    def clean_number(number: Optional[str]) -> str:
        # Strip spaces/dashes before validating.
        try:
            if not number:
                return ""
            return re.sub(r"[\s-]", "", number)
        except Exception as ex:
            logger.error(f"[CreditCardService] - [CARD_NUMBER: {mask_card(number)}] - FAILED: {ex}")
            return number

    @staticmethod
    def validate_integrity(number: Optional[str]) -> Optional[JSONResponse]:
        if not number.isdigit():
            return JSONResponse(status_code=400, content={"error": "Card number must contain only digits"})

        # Only accept 12–19 digits after cleanup.
        if not 12 <= len(number) <= 19:
            return JSONResponse(status_code=400, content={"error": "Card number must be 12–19 digits"})

        return None
