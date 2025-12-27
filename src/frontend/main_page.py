import asyncio
from dataclasses import dataclass, field
from typing import Dict

from nicegui import ui, app
from serial.serialutil import SerialException

from src.gq.device import GMCDevice


device = GMCDevice()

@dataclass
class GlobalState:
    radiation: Dict[str, int] = field(default_factory=lambda: {
        'cpm': 0, 'cps': 0, 'max_cps': 0, 'cpm_high': 0, 'cpm_low': 0
    })
    connection_status: bool = True
    is_active: bool = False
    error_message: str = ''

state = GlobalState()


def fetch_data():
    state.radiation.update({
        'cpm': device.radiation.get_cpm(),
        'cps': device.radiation.get_cps(),
        'max_cps': device.radiation.get_max_cps(),
        'cpm_high': device.radiation.get_cpm_high_tube(),
        'cpm_low': device.radiation.get_cpm_low_tube()
    })


async def device_main_loop():
    loop = asyncio.get_running_loop()
    while True:
        try:
            result = await loop.run_in_executor(None, device.auto_connect)
            if not result:
                state.connection_status = False
                state.is_active = False
                await app_ui.refresh()
                await asyncio.sleep(2)
                continue

            _ = await loop.run_in_executor(None, device.device_info.get_voltage)
            state.connection_status = True
            state.error_message = ''

            if state.is_active:
                await loop.run_in_executor(None, fetch_data)

        except (SerialException, OSError) as e:
            state.connection_status = False
            state.is_active = False
            state.error_message = f"Verbindung verloren: {e}"
            device.disconnect()
            await app_ui.refresh()
            await asyncio.sleep(2)

        await app_ui.refresh()
        await asyncio.sleep(0.5)

@ui.refreshable
def app_ui():
    def toggle_active():
        state.is_active = not state.is_active
        app_ui.refresh()

    if state.error_message:
        with ui.row().classes(
                'bg-red-100 text-red-900 w-full p-4 items-center justify-between mb-4 rounded-lg border border-red-200'):
            with ui.row().classes('items-center gap-3'):
                ui.icon('report_problem', color='red-700').classes('text-xl')
                ui.label(state.error_message).classes('text-sm md:text-base')

            ui.button(on_click=lambda: [setattr(state, 'error_message', None), app_ui.refresh()]) \
                .props('flat round icon=close').classes('text-red-900 hover:bg-red-200')

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
                ui.label(f"CPM: {state.radiation['cpm']}")
                ui.label(f"CPS: {state.radiation['cps']}")
                ui.label(f"Max CPS: {state.radiation['max_cps']}")

            with ui.column():
                ui.label('Dual-Tube (GMC-500+)').classes('font-bold')
                ui.label(f"High Tube CPM: {state.radiation['cpm_high']}")
                ui.label(f"Low Tube CPM: {state.radiation['cpm_low']}")

app.on_startup(lambda: asyncio.create_task(device_main_loop()))
app.on_shutdown(device.disconnect)
app.on_shutdown(lambda: setattr(state, 'connection_status', False))
app.on_shutdown(lambda: setattr(state, 'active', False))
