from typing import List


def is_valid_luhn(card_number: str) -> bool:
    if not card_number or not card_number.isdigit():
        return False

    total = 0
    reverse_digits: List[int] = [int(ch) for ch in card_number[::-1]]

    for i, n in enumerate(reverse_digits):
        if i % 2 == 1:
            n = n * 2
            if n > 9:
                n -= 9
        total += n

    return total % 10 == 0


def get_card_scheme(card_number: str) -> str:
    if card_number.startswith("4"):
        return "visa"
    if card_number.startswith(("51", "52", "53", "54", "55")):
        return "mastercard"
    if card_number.startswith(("34", "37")):
        return "amex"
    return "unknown"
