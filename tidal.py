#          █   █ █ █ ▀▄▀ █▀█ █▀█ ▄▄█ █▀▀
#          ▀▄▀▄▀ █▀█  █  █▀▀ █▄█ █▄█ █▄█ ▄
#                © Copyright 2023
#
#             👤 https://t.me/whypodg
#
# 🔒 Licensed under CC-BY-NC-ND 4.0
# 🌐 https://creativecommons.org/licenses/by-nc-nd/4.0

# required: tidalapi

import asyncio
import io
import requests
from loguru import logger

import tidalapi
from tidalapi import media

from pyrogram import Client, types

from .. import loader, utils


@loader.module(name="Tidal", author="whypodg", version=1.0)
class Tidal(loader.Module):
	"""Модуль для работы с API сервиса Tidal Hi-Fi Music"""

	def tidalLogin(self):
		login_credits = (
			self.db.get("TidalMod", "token_type"),
			self.db.get("TidalMod", "access_token"),
			self.db.get("TidalMod", "refresh_token"),
			self.db.get("TidalMod", "session_id")
		)
		tidal = tidalapi.Session()

		try:
			tidal.load_oauth_session(*login_credits)
			if tidal.check_login():
				return tidal
			return tidalapi.Session()
		except:
			logger.exception("Error loading OAuth Tidal session")
			return tidalapi.Session()


	@loader.command()
	async def tlogincmd(self, app: Client, message: types.Message):
		"""Авторизация в TIDAL"""

		tidal = self.tidalLogin()
		if tidal.check_login():
			await utils.answer(message, "<emoji id=5312526098750252863>🚫</emoji> <b>Ты уже авторизован</b>")
			return

		result, future = tidal.login_oauth()
		msg = await utils.answer(
			message=message,
			caption=f'<emoji id=5472308992514464048>🔐</emoji> <b><a href="https://{result.verification_uri_complete}">' \
					 f'Перейдите сюда</a> и авторизуйтесь в течении 5 минут!</b>',
			doc=True,
			response="https://0x0.st/oecP.MP4"
		)
		await message.delete()

		outer_loop = asyncio.get_event_loop()

		def callback(*args, **kwargs):
			if tidal.check_login():
				asyncio.ensure_future(
					utils.answer(
						message=msg,
						response="<emoji id=5314250708508220914>✅</emoji> <b>Успешно авторизованы!</b>"
					),
					loop=outer_loop,
				)
			else:
				asyncio.ensure_future(
					utils.answer(
						message=msg,
						response="<emoji id=5312526098750252863>❌</emoji> <b>Ошибка авторизации</b>"
					),
					loop=outer_loop
				)
			self.db.set("TidalMod", "token_type", tidal.token_type)
			self.db.set("TidalMod", "session_id", tidal.session_id)
			self.db.set("TidalMod", "access_token", tidal.access_token)
			self.db.set("TidalMod", "refresh_token", tidal.refresh_token)

		future.add_done_callback(callback)


	@loader.command()
	async def tidalcmd(self, app: Client, message: types.Message):
		"""Поиск в TIDAL"""

		stidal = self.tidalLogin()
		if not stidal:
			await utils.answer(message, "<emoji id=5312526098750252863>❌</emoji> <b>Сначала нужно авторизоваться</b>")
			return

		query = utils.get_args_raw(message)
		if not query:
			await utils.answer(message, "<emoji id=5312526098750252863>❌</emoji> <b>Укажите поисковый запрос</b>")
			return

		message = await utils.answer(message, "<emoji id=5309965701241379366>🔍</emoji> <b>Ищем...</b>")

		result = stidal.search(query=query)
		if not result or not result.get('tracks', None):
			await utils.answer(message, "<emoji id=5312526098750252863>❌</emoji> <b>Ничего не найдено</b>")
			return

		track = result['tracks'][0]
		track_res = {
			"url": track.get_url(), "id": track.id,
			"artists": [], "name": track.name,
			"tags": [], "duration": track.duration
		}

		meta = (
			stidal.request.request(
				"GET",
				f"tracks/{track_res['id']}",
			)
		).json()

		artists = track_res['artists']
		for i in meta["artists"]:
			if i['name'] not in artists:
				artists.append(i['name'])
		track_res['artists'] = artists
		full_name = f"{', '.join(artists)} - {track_res['name']}"

		if meta.get("explicit"):
			track_res['tags'].append("#explicit🤬")
		if meta.get("audioQuality"):
			track_res['tags'].append(f"#{meta['audioQuality']}🔈")
		if isinstance(meta.get("audioModes"), list):
			for tag in meta["audioModes"]:
				track_res['tags'].append(f"#{tag}🎧")

		search_string = "<emoji id=5370924494196056357>🖤</emoji> <b>{name}</b>\n" \
						"<emoji id=6334768915524093741>⏰</emoji> <b>Дата релиза (в Tidal):</b> <i>{release}</i>"
		text = search_string.format(
			name=str(full_name).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"),
			release=track.tidal_release_date.strftime(
				"%d.%m.%Y"
			)
		)
		message = await utils.answer(
			message, text + "\n\n<i>Загрузка аудио…</i>"
		)

		text += f"\n\n{', '.join(track_res['tags'])}"
		text += f"\n\n<emoji id=5359582743992737342>🎵</emoji> " \
				f"<b><a href='https://tidal.com/browse/track/{track_res['id']}'>Tidal</a></b>"

		await message.delete()
		track_by = requests.get(track_res['url']).content
		file = io.BytesIO(track_by)
		file.name = "track.mp3"
		await app.send_audio(
			chat_id=message.chat.id, caption=text, audio=file,
			duration=track_res['duration'], title=track_res['name'],
			performer=", ".join(track_res['artists'])
		)