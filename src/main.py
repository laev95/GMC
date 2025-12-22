from frontend.main_page import app, ui
from gq.startup.setup import connect

if __name__ == "__main__":
    test_connection = connect()

    app()
    ui.run()