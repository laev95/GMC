from frontend.main_page import app, ui
from src.startup.startup import connect

if __name__ == "__main__":
    try:
        test_connection = connect()
    except OSError as exc:
        print(f"Failed to connect to device: {exc}")
        quit(1)

    app()
    ui.run()