import secrets
import string

secret_phrases = ["some phrase", "digit123nospace"]
secret_generate_data = [
    ("secret phrase", "secret"),
    (
        "".join(
            [secrets.choice(string.ascii_letters + string.digits) for _ in range(19)]
        ),
        "".join(
            [secrets.choice(string.ascii_letters + string.digits) for _ in range(19)]
        ),
    ),
]
