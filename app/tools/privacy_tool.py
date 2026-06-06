import re
import os

def anonymize(data: str) -> str:
    """
    Filtre RGPD — anonymise les données sensibles
    avant envoi vers Claude API.
    Configurable via .env : PRIVACY_LEVEL=strict|standard|off
    """
    level = os.getenv("PRIVACY_LEVEL", "standard")

    if level == "off":
        return data

    # Emails → j***@***.com
    data = re.sub(
        r'[\w.+-]+@[\w-]+\.[a-zA-Z]+',
        'email@***.***',
        data
    )

    # Numéros de CB → **** **** **** 4521
    data = re.sub(
        r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        '**** **** **** ****',
        data
    )

    # Téléphones français → 06** *** ***
    data = re.sub(
        r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}',
        '0X** *** ***',
        data
    )

    # IBAN → IBAN****
    data = re.sub(
        r'[A-Z]{2}\d{2}[\s]?[\d\s]{4,}',
        'IBAN****',
        data
    )

    if level == "strict":
        # Noms propres potentiels (Prénom Nom)
        data = re.sub(
            r'\b[A-Z][a-zéèêàâ]+\s[A-Z][A-ZÉÈÊÀÂa-zéèêàâ]+\b',
            'CLIENT_XXX',
            data
        )

    return data


def anonymize_dict(data: dict) -> dict:
    """Anonymise récursivement un dictionnaire"""
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = anonymize(value)
        elif isinstance(value, dict):
            result[key] = anonymize_dict(value)
        elif isinstance(value, list):
            result[key] = [
                anonymize(v) if isinstance(v, str) else v
                for v in value
            ]
        else:
            result[key] = value
    return result