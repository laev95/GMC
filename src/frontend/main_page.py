import asyncio
from dataclasses import dataclass, field
from typing import Dict

from nicegui import ui, app
from serial.serialutil import SerialException

from src.gq.device import GMCDevice

device = GMCDevice()
device_lock = asyncio.Lock()

@dataclass
class GlobalState:
    radiation: Dict[str, int] = field(default_factory=lambda: {
        'cpm': 0, 'cps': 0, 'max_cps': 0, 'cpm_high': 0, 'cpm_low': 0
    })
    is_connected: bool = True
    is_active: bool = False
    error_message: str = ''
    history_data: str = ''

state = GlobalState()


async def fetch_history():
    async with device_lock:
        loop = asyncio.get_running_loop()
        try:
            history = await loop.run_in_executor(None, device.history.get_history)
            state.history_data = str(history)
        except Exception as e:
            state.history_data = f"Error fetching history: {e}"


def fetch_radiation_data():
    if state.is_connected:
        state.radiation.update({
            'cpm': device.radiation.get_cpm(),
            'cps': device.radiation.get_cps(),
            'max_cps': device.radiation.get_max_cps(),
            'cpm_high': device.radiation.get_cpm_high_tube(),
            'cpm_low': device.radiation.get_cpm_low_tube()
        })


async def device_live_data_loop():
    while True:
        try:
            async with device_lock:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, device.auto_connect)

                if result:
                    _ = await loop.run_in_executor(None, device.device_info.get_voltage)
                    state.is_connected = True
                    if state.is_active:
                        await loop.run_in_executor(None, fetch_radiation_data)
                else:
                    state.is_connected = False

                if state.is_active:
                    await loop.run_in_executor(None, fetch_radiation_data)

        except (SerialException, OSError) as e:
            state.is_connected = False
            state.is_active = False
            state.error_message = f"Connection lost: {e}"
            device.disconnect()
            await asyncio.sleep(2)

        await asyncio.sleep(0.5)


@ui.refreshable
def error_banner():
    with ui.row().classes(
            'bg-red-100 text-red-900 w-full p-4 items-center justify-between mb-4 rounded-lg border border-red-200') \
            .bind_visibility_from(state, 'error_message'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('report_problem', color='red-700').classes('text-xl')

            ui.label().classes('text-sm md:text-base') \
                .bind_text_from(state, 'error_message')

        ui.button(on_click=lambda: setattr(state, 'error_message', None)) \
            .props('flat round icon=close') \
            .classes('text-red-900 hover:bg-red-200')


@ui.refreshable
def app_ui():
    def toggle_active():
        state.is_active = not state.is_active
        app_ui.refresh()

    if state.error_message:
        error_banner()

    with ui.grid(columns=4).classes('gap-4 mx-auto w-full'):
        with ui.card().classes('col-span-1'):
            with ui.row().classes('items-center w-full justify-between mb-4'):
                ui.label('GQ GMC Radiation Values').classes('text-h5')
                ui.icon('circle', color='green').bind_visibility_from(state, 'is_connected')
                ui.icon('circle', color='red').bind_visibility_from(state, 'is_connected', backward=lambda x: not x)

            with ui.row().classes('items-center pb-4'):
                ui.button(
                    "Stop" if state.is_active else "Start",
                    on_click=toggle_active
                ).props(f'icon={"stop" if state.is_active else "play_arrow"}')

                ui.button("Update once", on_click=lambda: [fetch_radiation_data(), app_ui.refresh()]).props('outline icon=refresh')

            with ui.grid(columns=2).classes('w-full gap-4'):
                with ui.column():
                    ui.label('Standard Values').classes('font-bold')
                    ui.label().bind_text_from(state.radiation, 'cpm', backward=lambda v: f"CPM: {v}")
                    ui.label().bind_text_from(state.radiation, 'cps', backward=lambda v: f"CPS: {v}")
                    ui.label().bind_text_from(state.radiation, 'max_cps', backward=lambda v: f"Max CPS: {v}")

                with ui.column():
                    ui.label('Dual-Tube (GMC-500+)').classes('font-bold')
                    ui.label().bind_text_from(state.radiation, 'cpm_high', backward=lambda v: f"High Tube CPM: {v}")
                    ui.label().bind_text_from(state.radiation, 'cpm_low', backward=lambda v: f"Low Tube CPM: {v}")

        with ui.card().classes('col-span-3'):
            ui.label('History Data').classes('text-h5 mb-4')

            ui.button("Get history data", on_click=fetch_history).props('icon=history')

            ui.textarea(label='History Data') \
                .props('readonly outlined') \
                .classes('w-full mt-4') \
                .style('min-height: 300px') \
                .bind_value_from(state, 'history_data')


app.on_startup(lambda: asyncio.create_task(device_live_data_loop()))
app.on_shutdown(device.disconnect)
app.on_shutdown(lambda: setattr(state, 'is_connected', False))
app.on_shutdown(lambda: setattr(state, 'active', False))
