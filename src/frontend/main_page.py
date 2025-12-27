import asyncio

from nicegui import ui, app
from serial.serialutil import SerialException
from src.gq.device import GMCDevice
from dataclasses import dataclass, field
from typing import Dict

device = GMCDevice()

@dataclass
class GlobalState:
    radiation: Dict[str, int] = field(default_factory=lambda: {
        'cpm': 0, 'cps': 0, 'max_cps': 0, 'cpm_high': 0, 'cpm_low': 0
    })
    connection_status: bool = True
    is_active: bool = False

state = GlobalState()


def fetch_data():
    state.radiation = {
        'cpm': device.radiation.get_cpm(),
        'cps': device.radiation.get_cps(),
        'max_cps': device.radiation.get_max_cps(),
        'cpm_high': device.radiation.get_cpm_high_tube(),
        'cpm_low': device.radiation.get_cpm_low_tube()
    }

async def device_main_loop():
    while True:
        result = device.auto_connect()
        if not result: continue

        try:
            _ = device.device_info.get_voltage()
            state.connection_status = True

            if state.is_active:
                fetch_data()

        except (SerialException, OSError) as e:
            ui.notify(f"Fehler beim Lesen der Daten: {e}", type='negative')
            state.connection_status = False
            state.is_active = False
            device.disconnect()

        await app_ui.refresh()
        await asyncio.sleep(1)


@ui.refreshable
def app_ui():
    def toggle_active():
        state.is_active = not state.is_active
        app_ui.refresh()

    with ui.card().classes('w-full max-w-md mx-auto'):
        with ui.row().classes('items-center w-full justify-between mb-4'):
            ui.label('GQ GMC Strahlungswerte').classes('text-h5')
            ui.icon('circle', color='green' if state.connection_status else 'red').classes('text-2xl')

        with ui.row().classes('items-center pb-4'):
            ui.button(
                "Stop" if state.is_active else "Start",
                on_click=toggle_active
            ).props(f'icon={"stop" if state.is_active else "play_arrow"}')

            ui.button("Einmalig aktualisieren", on_click=lambda: [fetch_data(), app_ui.refresh()]).props('outline icon=refresh')

        with ui.grid(columns=2).classes('w-full gap-4'):
            with ui.column():
                ui.label('Standard-Werte').classes('font-bold')
                ui.label().bind_text_from(state.radiation, backward=lambda d: f"CPM: {d['cpm']}")
                ui.label().bind_text_from(state.radiation, backward=lambda d: f"CPS: {d['cps']}")
                ui.label().bind_text_from(state.radiation, backward=lambda d: f"Max CPS: {d['max_cps']}")

            with ui.column():
                ui.label('Dual-Tube (GMC-500+)').classes('font-bold')
                ui.label().bind_text_from(state.radiation, backward=lambda d: f"High Tube CPM: {d['cpm_high']}")
                ui.label().bind_text_from(state.radiation, backward=lambda d: f"Low Tube CPM: {d['cpm_low']}")

app.on_startup(device_main_loop)
app.on_shutdown(device.disconnect)
