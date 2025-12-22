from .core import write

def send_key(key: int) -> None:
    """
    RFC1801: Sendet einen Tastendruck.
    Erlaubte Formen:
      - <KEY[D0]>>
      - oder explizit: <KEY0>> .. <KEY3>>
    """
    if not (0 <= key <= 3):
        raise ValueError("key must be 0..3")
    write(f"<KEY{key}>>".encode("ascii"))