from nicegui import ui
from serial.serialutil import SerialException
from src.gq.device import GMCDevice

device = GMCDevice()
device.auto_connect()

@ui.refreshable
def app():
    radiation_data, set_radiation_data = ui.state({
        'cpm': 0,
        'cps': 0,
        'max_cps': 0,
        'cpm_high': 0,
        'cpm_low': 0
    })

    is_active, set_is_active = ui.state(False)
    connection_status, set_connection_status = ui.state(True)


    def update_data():
        try:
            new_values = {
                'cpm': device.radiation.get_cpm(),
                'cps': device.radiation.get_cps(),
                'max_cps': device.radiation.get_max_cps(),
                'cpm_high': device.radiation.get_cpm_high_tube(),
                'cpm_low': device.radiation.get_cpm_low_tube()
            }
            set_radiation_data(new_values)
            set_connection_status(True)
        except (SerialException, OSError) as e:
            ui.notify(f"Fehler beim Lesen der Daten: {e}", type='negative')
            set_is_active(False)


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
                ui.label(f"CPM: {radiation_data['cpm']}")
                ui.label(f"CPS: {radiation_data['cps']}")
                ui.label(f"Max CPS: {radiation_data['max_cps']}")

            with ui.column():
                ui.label('Dual-Tube (GMC-500+)').classes('font-bold')
                ui.label(f"High Tube CPM: {radiation_data['cpm_high']}")
                ui.label(f"Low Tube CPM: {radiation_data['cpm_low']}")

        ui.timer(1.0, update_data, active=is_active)