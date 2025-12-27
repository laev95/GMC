from frontend.main_page import app_ui, ui


def main():
    app_ui()
    ui.run()


if __name__ in {"__main__", "__mp_main__"}:
    main()