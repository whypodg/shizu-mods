#          █   █ █ █ ▀▄▀ █▀█ █▀█ ▄▄█ █▀▀
#          ▀▄▀▄▀ █▀█  █  █▀▀ █▄█ █▄█ █▄█ ▄
#                © Copyright 2023
#
#             👤 https://t.me/whypodg
#
# 🔒 Licensed under CC-BY-NC-ND 4.0
# 🌐 https://creativecommons.org/licenses/by-nc-nd/4.0

# banner: https://raw.githubusercontent.com/whypodg/shizu-mods/main/badges/deleter.png
# requiremets: tidalapi

import asyncio
from loguru import logger

from pyrogram import Client, types

from .. import loader, utils


@loader.module(name="Deleter", author="whypodg", version=1.0)
class DeleterMod(loader.Module):
	"""Модуль для удаления твоих N сообщений"""

	@loader.command()
	async def delmsgcmd(self, app: Client, message: types.Message):
		"""Удалить сообщения"""

		args = message.text.split()[1:]
		count = 1
		if args and args[0].isdigit():
			count = int(args[0])

		msgs = []
		async for msg in app.get_chat_history(chat_id=message.chat.id, limit=50+count):
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
	async def editmsgscmd(self, app: Client, message: types.Message):
		"""Включить/выключить редактирование сообщений перед их удалением"""

		edit_need = self.db.get("DeleterMod", "edit_need", False)
		need = False if edit_need else True
		self.db.set("DeleterMod", "edit_need", need)

		await utils.answer(
			message,
			"<emoji id=5213305971891248967>✏️</emoji> <b>Теперь сообщения будут редактироваться перед их удалением</b>" if need else "<emoji id=5231010832107708935>🗑</emoji> <b>Теперь сообщения не будут редактировать перед их удалением</b>"
		)


	@loader.command()
	async def setedittextcmd(self, app: Client, message: types.Message):
		"""Изменить текст редактирования сообщений (если указать «-» — изменит текст на невидимый символ)"""

		edit_text = self.db.get("DeleterMod", "edit_text", None)
		args = utils.get_args_raw(message)
		text = args if args and args not in ["-", "–", "—"] else "\xad"
		self.db.set("DeleterMod", "edit_text", text)
		self.db.set("DeleterMod", "edit_need", True)

		await utils.answer(
			message,
			f"<emoji id=5213305971891248967>✏️</emoji> <b>Теперь я буду редактировать сообщения на " + (f"«<code>{text}</code>»" if text != "\xad" else "невидимый символ") + f" перед их удалением</b>"
		)
