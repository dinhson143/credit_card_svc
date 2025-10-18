from aws_lambda_powertools import Logger


logger = Logger(service="credit_card_svc")


def mask_card(card_number: str) -> str:
    if not card_number:
        return ""
    visible = 4
    masked = "*" * max(len(card_number) - visible, 0) + card_number[-visible:]
    return masked
