"""
Created on 2024-02-05

based on https://raw.githubusercontent.com/zauberzeug/nicegui/main/examples/chat_app/main.py

@author: wf
"""
from ngwidgets.llm import LLM
from datetime import datetime
from typing import List, Tuple
from uuid import uuid4

from nicegui import Client, ui

messages: List[Tuple[str, str, str, str]] = []
llm = LLM()
chat_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/64px-ChatGPT_logo.svg.png"

@ui.refreshable
def chat_messages(own_id: str) -> None:
    for user_id, avatar, text, stamp in messages:
        ui.chat_message(text=text, stamp=stamp, avatar=avatar, sent=own_id == user_id)
    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')


@ui.page('/')
async def home(client: Client):
    def send() -> None:
        stamp = datetime.utcnow().strftime('%X')
        messages.append((user_id, avatar, text.value, stamp))
        stamp = datetime.utcnow().strftime('%X')
        answer = llm.ask(text.value)
        messages.append((user_id, chat_icon, answer, stamp))
        text.value = ''
        chat_messages.refresh()

    user_id = str(uuid4())
    avatar = f'https://robohash.org/{user_id}?bgset=bg2'

    anchor_style = r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}'
    ui.add_head_html(f'<style>{anchor_style}</style>')
    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            with ui.avatar().on('click', lambda: ui.open(home)):
                ui.image(avatar)
            text = ui.textarea(placeholder='message').on('keydown.enter', send) \
                .props('rounded outlined input-class=mx-3') \
                .props("clearable") \
                .props("cols=120")\
                .props("rows=10")\
                .classes('flex-grow')
        ui.markdown('simple chat app built with [NiceGUI](https://nicegui.io)') \
            .classes('text-xs self-end mr-8 m-[-1em] text-primary')

    await client.connected()  # chat_messages(...) uses run_javascript which is only possible after connecting
    with ui.column().classes('w-full max-w-2xl mx-auto items-stretch'):
        chat_messages(user_id)

def run_chat():
    ui.run(port=8681,reload=False)

if __name__ == "__main__":
    run_chat()
