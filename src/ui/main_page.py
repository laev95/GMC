from __future__ import annotations

import asyncio

from nicegui import ui, app

from src.gq.device import GMCDevice
from .gmc_state import GlobalState
from ..gq.errors import ServiceError

device = GMCDevice()
device_lock = asyncio.Lock()
state = GlobalState()


def shutdown():
    state.is_connected = False
    state.is_active = False
    device.disconnect()


async def fetch_history() -> None:
    async with device_lock:
        try:
            history = await asyncio.to_thread(device.history.get_history)
            state.history_data = str(history)
        except ServiceError as e:
            state.error_message = f"Error fetching history: {e} ({e.__class__.__name__})"
            shutdown()


async def fetch_radiation_data() -> None:
    async with device_lock:
        try:
            await asyncio.to_thread(lambda: state.radiation.update({
                'cpm': device.radiation.get_cpm(),
                'cps': device.radiation.get_cps(),
                'max_cps': device.radiation.get_max_cps(),
                'cpm_high': device.radiation.get_cpm_high_tube(),
                'cpm_low': device.radiation.get_cpm_low_tube()
            }))
        except ServiceError as e:
            state.error_message = f"Error fetching radiation: {e} ({e.__class__.__name__})"
            shutdown()


async def device_live_data_loop():
    while True:
        state.is_connected = device.connection_status
        if state.is_connected:
            async with device_lock:
                state.device_name = await asyncio.to_thread(device.device_info.get_hardware_model)
            if state.is_active:
                await fetch_radiation_data()
        else:
            async with device_lock:
                await asyncio.to_thread(device.auto_connect)
        await asyncio.sleep(1)


def toggle_active():
    if state.is_connected:
        state.is_active = not state.is_active
    else:
        state.error_message = "Cannot start transmission. Device not connected!"


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
    error_banner()

    with ui.row().classes('items-center p-4'):
        ui.label().bind_text_from(state, 'device_name', backward=lambda v: f"Device: {v}").classes('text-h4')
        ui.icon('circle', color='red').bind_visibility_from(state, 'is_connected', backward=lambda x: not x).classes('text-h5')
        ui.icon('circle', color='green').bind_visibility_from(state, 'is_connected')

    with ui.grid(columns=4).classes('gap-4 mx-auto w-full'):
        with ui.card().classes('col-span-1'):
            with ui.row().classes('items-center w-full justify-between mb-4'):
                ui.label('GQ GMC Radiation Values').classes('text-h5')

            with ui.row().classes('items-center pb-4'):
                ui.button('Stop', icon='stop', on_click=toggle_active) \
                    .bind_visibility_from(state, 'is_active')
                ui.button('Start', icon='play_arrow', on_click=toggle_active) \
                    .bind_visibility_from(state, 'is_active', backward=lambda x: not x)

                ui.button("Update once", on_click=fetch_radiation_data).props('outline icon=refresh')

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

            ui.textarea(label='History Data').props('readonly outlined') \
                .classes('w-full mt-4') \
                .style('min-height: 300px') \
                .bind_value_from(state, 'history_data')


app.on_startup(lambda: asyncio.create_task(device_live_data_loop()))
app.on_shutdown(device.disconnect)
app.on_shutdown(lambda: setattr(state, 'is_connected', False))
app.on_shutdown(lambda: setattr(state, 'active', False))
