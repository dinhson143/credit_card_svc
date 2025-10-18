import pytest
from fastapi.responses import JSONResponse
from unittest.mock import patch

from src.services.credit_card_service import CreditCardService


@pytest.fixture
def service():
    return CreditCardService()


class TestCreditCardService:
    @pytest.mark.parametrize(
            "number,expected",
            [
                ("4111-1111-1111-1111", "4111111111111111"),
                ("  5500 0000 0000 0004  ", "5500000000000004"),
                ("", ""),
                (None, "")
            ]
    )
    def test_clean_number(self, service, number, expected):
        assert service.clean_number(number) == expected

    def test_clean_number_exception(self, service):
        # simulate exception by passing an invalid regex input type
        with patch("src.services.credit_card_service.re.sub", side_effect=Exception("regex error")):
            result = service.clean_number("4111")
            assert result == "4111"

    @pytest.mark.parametrize(
            "number,expected_status",
            [
                ("abc123", 400),
                ("1234567890", 400),
                ("123456789012", None),
                ("1234567890123456789", None),
            ]
    )
    def test_validate_integrity(self, service, number, expected_status):
        response = service.validate_integrity(number)
        if expected_status:
            assert isinstance(response, JSONResponse)
            assert response.status_code == expected_status
        else:
            assert response is None

    @patch("src.services.credit_card_service.get_card_scheme", return_value="VISA")
    @patch("src.services.credit_card_service.is_valid_luhn", return_value=True)
    @patch("src.services.credit_card_service.logger")
    def test_validate_success(
            self, mock_logger, mock_luhn, mock_scheme, service
    ):
        number = "4111111111111111"
        response = service.validate(number)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        body = response.body.decode()
        assert body == '{"valid":true,"scheme":"VISA","message":"OK"}'

        mock_luhn.assert_called_once_with(number)
        mock_scheme.assert_called_once_with(number)

    @patch("src.services.credit_card_service.get_card_scheme", return_value="VISA")
    @patch("src.services.credit_card_service.is_valid_luhn", return_value=False)
    @patch("src.services.credit_card_service.logger")
    def test_validate_invalid_luhn(self, mock_logger, mock_luhn, mock_scheme, service):
        number = "4111111111111111"
        response = service.validate(number)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert "Invalid credit card number" in response.body.decode()

    @patch("src.services.credit_card_service.is_valid_luhn", side_effect=Exception("test error"))
    @patch("src.services.credit_card_service.logger")
    def test_validate_exception(self, mock_logger, mock_luhn, service):
        response = service.validate("4111111111111111")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert "Internal server error" in response.body.decode()
        mock_logger.error.assert_called()


