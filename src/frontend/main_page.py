from nicegui import ui
from serial.serialutil import SerialException
from src.gq.radiation import get_cpm, get_cps, get_max_cps, get_cpm_high_tube, get_cpm_low_tube


@ui.refreshable
def app():
    values = ui.state({
        'cpm': 0,
        'cps': 0,
        'max_cps': 0,
        'cpm_high': 0,
        'cpm_low': 0
    })

    is_active, set_is_active = ui.state(False)
    connection_status = ui.state(True)
    last_error = ui.state("")

    def update_data():
        try:
            values.value = {
                'cpm': get_cpm(),
                'cps': get_cps(),
                'max_cps': get_max_cps(),
                'cpm_high': get_cpm_high_tube(),
                'cpm_low': get_cpm_low_tube()
            }
            connection_status.value = True
        except (SerialException, OSError) as e:
            ui.notify(f"Fehler beim Lesen der Daten: {e}", type='negative')
            last_error.value = str(e)

    with ui.card().classes('w-full max-w-md mx-auto'):
        ui.label('GQ GMC Strahlungswerte').classes('text-h5 mb-4')

        with ui.row().classes('items-center pb-4'):
            ui.button(
                "Stop" if is_active else "Start",
                on_click=lambda: set_is_active(not is_active)
            ).props('icon=play_arrow' if not is_active else 'icon=stop')

            ui.button("Einmalig aktualisieren", on_click=update_data).props('outline icon=refresh')

        with ui.grid(columns=2).classes('w-full gap-4'):
            with ui.column():
                ui.label('Standard-Werte').classes('font-bold')
                ui.label(f"CPM: {values.value['cpm']}")
                ui.label(f"CPS: {values.value['cps']}")
                ui.label(f"Max CPS: {values.value['max_cps']}")

            with ui.column():
                ui.label('Dual-Tube (GMC-500+)').classes('font-bold')
                ui.label(f"High Tube CPM: {values.value['cpm_high']}")
                ui.label(f"Low Tube CPM: {values.value['cpm_low']}")

        ui.timer(1.0, update_data, active=is_active)