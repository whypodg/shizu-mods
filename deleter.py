#          █   █ █ █ ▀▄▀ █▀█ █▀█ ▄▄█ █▀▀
#          ▀▄▀▄▀ █▀█  █  █▀▀ █▄█ █▄█ █▄█ ▄
#                © Copyright 2023
#
#             👤 https://t.me/whypodg
#
# 🔒 Licensed under CC-BY-NC-ND 4.0
# 🌐 https://creativecommons.org/licenses/by-nc-nd/4.0

# requiremets: tidalapi

import asyncio

from pyrogram import Client, types

from .. import loader, utils


@loader.module(name="Deleter", author="whypodg", version=1.0)
class DeleterMod(loader.Module):
    """Модуль для удаления твоих N сообщений"""

    @loader.command(docs="Удалить сообщения")
    async def delmsg(self, app: Client, message: types.Message):
        args = message.text.split()[1:]
        count = int(args[0]) if args and args[0].isdigit() else 1
        msgs = []
        async for msg in app.get_chat_history(
            chat_id=message.chat.id, limit=50 + count
        ):
            if msg.id == message.id:
                continue
            if msg.from_user.id == self.tg_id:
                msgs.append(msg)
            continue

        if self.db.get("DeleterMod", "edit_need", False):
            await message.edit(self.db.get("DeleterMod", "edit_text", "\xad"))
        await message.delete()
        for i in msgs:
            if count == 0:
                break
            if self.db.get("DeleterMod", "edit_need", False):
                try:
                    await i.edit(self.db.get("DeleterMod", "edit_text", "\xad"))
                except:
                    pass
            await i.delete()
            count -= 1
            await asyncio.sleep(0.5)

    @loader.command()
    async def editmsgs(self, app: Client, message: types.Message):
        """Включить/выключить редактирование сообщений перед их удалением"""
        edit_need = self.db.get("DeleterMod", "edit_need", False)
        need = not edit_need
        self.db.set("DeleterMod", "edit_need", need)

        await utils.answer(
            message,
            "<emoji id=5213305971891248967>✏️</emoji> <b>Теперь сообщения будут редактироваться перед их удалением</b>"
            if need
            else "<emoji id=5231010832107708935>🗑</emoji> <b>Теперь сообщения не будут редактировать перед их удалением</b>",
        )

    @loader.command()
    async def setedittext(self, app: Client, message: types.Message):
        """Изменить текст редактирования сообщений (если указать «-» — изменит текст на невидимый символ)"""
        edit_text = self.db.get("DeleterMod", "edit_text", None)
        args = utils.get_args_raw(message)
        text = args if args and args not in ["-", "–", "—"] else "\xad"
        self.db.set("DeleterMod", "edit_text", text)
        self.db.set("DeleterMod", "edit_need", True)

        if text != "\xad":
            await message.answer(
                f"<emoji id=5213305971891248967>✏️</emoji> <b>Теперь я буду редактировать сообщения на «<code>{text}</code>» перед их удалением</b>"
            )
        else:
            await message.answer(
                "<emoji id=5213305971891248967>✏️</emoji> <b>Теперь я буду редактировать сообщения на невидимый символ перед их удалением</b>"
            )
