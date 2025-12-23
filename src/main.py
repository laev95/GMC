from frontend.main_page import app, ui
from startup.startup import connect

try:
    _ = connect()
except OSError as exc:
    print(f"Failed to connect to device: {exc}")
    quit(1)

app()
ui.run()