import secrets
import string
import json

def generate_keys_json():
    # De data structuur voor onze keys
    keys = {
        "alfanumeriek": ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32)),
        "url_safe": secrets.token_urlsafe(24)[:32],
        "hexadecimaal": secrets.token_hex(16),
        "mflux_seed": secrets.randbelow(10**10)
    }

    # Omzetten naar een JSON string
    # indent=4 zorgt voor een mooi leesbaar formaat
    json_output = json.dumps(keys, indent=4)
    
    return json_output

def generate_unique_name(length=12):
    """Genereer een unieke naam van een bepaalde lengte."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    resultaat = generate_keys_json()
    print(resultaat)
