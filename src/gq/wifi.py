from .core import write, read_ack, read_exact


def set_wifi_ssid(ssid: str) -> bool:
    """
    RFC1801: <SETSSID...>> setzt SSID (ASCII-String).
    Rückgabe: 0xAA (ACK)
    """
    write(b"<SETSSID" + ssid.encode("ascii", errors="strict") + b">>")
    return read_ack()


def set_wifi_password(password: str) -> bool:
    """
    RFC1801: <SETWIFIPW...>> setzt WiFi Passwort (ASCII-String).
    Rückgabe: 0xAA (ACK)
    """
    write(b"<SETWIFIPW" + password.encode("ascii", errors="strict") + b">>")
    return read_ack()


def set_website(website: str) -> bool:
    """
    RFC1801: <SETWEBSITE...>> setzt Website-Parameter (ASCII-String).
    Rückgabe: 0xAA (ACK)
    """
    write(b"<SETWEBSITE" + website.encode("ascii", errors="strict") + b">>")
    return read_ack()


def set_url(url: str) -> bool:
    """
    RFC1801: <SETURL...>> setzt URL (ASCII-String).
    Rückgabe: 0xAA (ACK)
    """
    write(b"<SETURL" + url.encode("ascii", errors="strict") + b">>")
    return read_ack()


def set_user_id(user_id: str) -> bool:
    """
    RFC1801: <SETUSERID...>> setzt UserID (ASCII-String).
    Rückgabe: 0xAA (ACK)
    """
    write(b"<SETUSERID" + user_id.encode("ascii", errors="strict") + b">>")
    return read_ack()


def set_counter_id(counter_id: str) -> bool:
    """
    RFC1801: <SETCOUNTERID...>> setzt CounterID (ASCII-String).
    Rückgabe: 0xAA (ACK)
    """
    write(b"<SETCOUNTERID" + counter_id.encode("ascii", errors="strict") + b">>")
    return read_ack()


def set_period_hex(period: int) -> bool:
    """
    RFC1801: <SETPERIOD[Param in hex]>> setzt das Sendeintervall/Perioden-Param.
    Rückgabe: 0xAA (ACK)

    Implementationshinweis:
    Das RFC beschreibt "Param in hex". In der Praxis ist es i.d.R. 1 Byte Rohwert (0..255),
    analog zu anderen [D0]-Parametern.
    """
    if not (0 <= period <= 0xFF):
        raise ValueError("period must be 0..255")
    write(b"<SETPERIOD" + bytes([period]) + b">>")
    return read_ack()


def wifi_on() -> bool:
    """
    RFC1801: <WiFiON>> aktiviert WiFi.
    Rückgabe: 0xAA (ACK)
    """
    write(b"<WiFiON>>")
    return read_ack()


def wifi_off() -> bool:
    """
    RFC1801: <WiFiOFF>> deaktiviert WiFi.
    Rückgabe: 0xAA (ACK)
    """
    write(b"<WiFiOFF>>")
    return read_ack()


def at_command(command: str = "") -> bytes:
    """
    RFC1801: <AT>> oder <AT+...>> reicht AT-Kommandos an das WiFi-Modul durch.

    Rückgabe:
      - typischerweise ASCII ("OK", oder ausführlicher)
      - Länge im RFC nicht fixiert → hier als Raw-Read mit fixer Obergrenze implementiert.
    """
    if command:
        write(b"<AT" + command.encode("ascii", errors="strict") + b">>")
    else:
        write(b"<AT>>")
    return read_exact(256)


def wifi_level() -> bytes:
    """
    RFC1801: <WiFiLevel>> liefert Signal/Status aus dem WiFi-Modul.
    Länge im RFC nicht fixiert → Raw-Read.
    """
    write(b"<WiFiLevel>>")
    return read_exact(256)