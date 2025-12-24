from frontend.main_page import app, ui


def main():
    app()
    ui.run()


if __name__ in {"__main__", "__mp_main__"}:
    main()