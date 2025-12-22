from nicegui import ui

from src.gq.radiation import get_cpm


@ui.refreshable
def app():
    is_turned_on, set_is_turned_on = ui.state(False)
    ui.button("Stop reading CPM" if is_turned_on else "Start reading CPM", on_click=lambda: set_is_turned_on(not is_turned_on))
    cpm_label = ui.label("CPM: ")
    if is_turned_on:
        ui.timer(1, lambda: cpm_label.set_text(f"CPM: {get_cpm()}"))
