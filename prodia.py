# `7MMM.     ,MMF'`7MMM.     ,MMF'   `7MMM.     ,MMF'              `7MM
# MMMb    dPMM    MMMb    dPMM       MMMb    dPMM                  MM
# M YM   ,M MM    M YM   ,M MM       M YM   ,M MM  ,pW"Wq.    ,M""bMM  ,pP"Ybd
# M  Mb  M' MM    M  Mb  M' MM       M  Mb  M' MM 6W'   `Wb ,AP    MM  8I   `"
# M  YM.P'  MM    M  YM.P'  MM mmmmm M  YM.P'  MM 8M     M8 8MI    MM  `YMMMa.
# M  `YM'   MM    M  `YM'   MM       M  `YM'   MM YA.   ,A9 `Mb    MM  L.   I8
# .JML. `'  .JMML..JML. `'  .JMML.   .JML. `'  .JMML.`Ybmd9'   `Wbmd"MML.M9mmmP'
#
# (c) 2023 — licensed under Apache 2.0 — https://www.apache.org/licenses/LICENSE-2.0

#          █   █ █ █ ▀▄▀ █▀█ █▀█ ▄▄█ █▀▀
#          ▀▄▀▄▀ █▀█  █  █▀▀ █▄█ █▄█ █▄█ ▄
#             👤 https://t.me/whypodg

# banner: https://raw.githubusercontent.com/whypodg/shizu-mods/main/badges/prodia.png
# required: aiohttp

import aiohttp
import asyncio
import io
import random
import requests
from loguru import logger

from pyrogram import Client, types

from .. import loader, utils

name_models = {
	"Analog Diffusion V1": "analog-diffusion-1.0.ckpt [9ca13f02]",
	"Anything V3": "anythingv3_0-pruned.ckpt [2700c435]",
	"Anything V4": "anything-v4.5-pruned.ckpt [65745d25]",
	"Anything V5": "anythingV5_PrtRE.safetensors [893e49b9]",
	"Orangemix": "AOM3A3_orangemixs.safetensors [9600da17]",
	"Deliberate V2": "deliberate_v2.safetensors [10ec4b29]",
	"Dreamlike Diffusion V1": "dreamlike-diffusion-1.0.safetensors [5c9fd6e0]",
	"Dreamlike Diffusion V2": "dreamlike-diffusion-2.0.safetensors [fdcf65e7]",
	"Dreamshaper V5": "dreamshaper_5BakedVae.safetensors [a3fbf318]",
	"Dreamshaper V6": "dreamshaper_6BakedVae.safetensors [114c8abb]",
	"Elldreth's Vivid Mix": "elldreths-vivid-mix.safetensors [342d9d26]",
	"Lyriel V1.5": "lyriel_v15.safetensors [65d547c5]",
	"Meina V9": "meinamix_meinaV9.safetensors [2ec66ab0]",
	"OpenJourney V4": "openjourney_V4.ckpt [ca2f377f]",
	"Portrait V1": "portrait+1.0.safetensors [1400e684]",
	"Realistic Vision V2": "Realistic_Vision_V2.0.safetensors [79587710]",
	"Rev Animated V1.22": "revAnimated_v122.safetensors [3f4fefd9]",
	"Riffusion V1": "riffusion-model-v1.ckpt [3aafa6fe]",
	"StableDiffusion V1.4": "sdv1_4.ckpt [7460a6fa]",
	"StableDiffusion V1.5": "v1-5-pruned-emaonly.ckpt [81761151]",
	"Shonin's Beautiful People V1": "shoninsBeautiful_v10.safetensors [25d8c546]",
	"The Ally's Mix II": "theallys-mix-ii-churned.safetensors [5d9225a4]",
	"Timeless V1": "timeless-1.0.ckpt [7c4971d4]"
}


@loader.module(name="Prodia", author="whypodg", version=1.0)
class Prodia(loader.Module):
	"""Генератор изображений на основе Prodia API. Не требует API ключа. Автор: @sonnestinkt, оригинал: https://raw.githubusercontent.com/GD-alt/mm-hikka-mods/main/Prodia.py, список изменений: https://yaso.su/notrandomdiff"""

	@loader.command()
	async def setprodiacmd(self, app: Client, message: types.Message):
		"""<настройка> <значение> — Изменить настройки"""

		args = utils.get_args_raw(message).split(maxsplit=1)
		if (len(args) < 2) or (args[0] not in ["model", "negative", "cfg", "steps", "sampler"]):
			if len(args) < 2:
				out = f"<emoji id=5312526098750252863>❌</emoji> <b>Недостаточно аргументов"
			else:
				out = f"<emoji id=5312526098750252863>❌</emoji> <b>Вы указали неверную настройку, вот " \
					  f"доступные настройки:</b>\n<code>model</code>, <code>negative</code>, <code>cfg</code>, " \
					  f"<code>steps</code>, <code>sampler</code>"
			return await utils.answer(
				message=message,
				response=out
			)

		if args[0] == "model" and args[1] not in name_models.keys():
			out = f"<emoji id=5312526098750252863>❌</emoji> <b>Вы указали неверное значение для настройки, вот доступные значения:</b>"
			for i in name_models.keys():
				out += f"\n  ▪ <code>{i}</code>"
			return await utils.answer(
				message=message,
				response=out
			)
		elif args[0] == "cfg" and (not args[1].isdigit() or (int(args[1]) > 20 or int(args[1]) < 0)):
			return await utils.answer(
				message=message,
				response=f"<emoji id=5312526098750252863>❌</emoji> <b>Вы указали неверное значение для настройки, " \
						 f"доступные значения — числа от 0 до 20</b>"
			)
		elif args[0] == "steps" and (not args[1].isdigit() or (int(args[1]) > 30 or int(args[1]) < 1)):
			return await utils.answer(
				message=message,
				response=f"<emoji id=5312526098750252863>❌</emoji> <b>Вы указали неверное значение для настройки, " \
						 f"доступные значения — числа от 1 до 30</b>"
			)
		elif args[0] == "sampler" and args[1] not in ["Euler", "Euler a", "Heun", "DPM++ 2M Karras", "DDIM"]:
			return await utils.answer(
				message=message,
				response=f"<emoji id=5312526098750252863>❌</emoji> <b>Вы указали неверное значение для настройки, " \
						 f"вот доступные значения:</b>\n<code>Euler</code>, <code>Euler a</code>, <code>Heun</code>, <code>DPM++ 2M Karras</code>, <code>DDIM</code>"
			)

		self.db.set(
			name="Prodia", key=args[0],
			value=args[1] if args[0] not in ['cfg', 'steps'] else int(args[1])
		)
		await utils.answer(
			message=message,
			response=f"<emoji id=5314250708508220914>✅</emoji> Успешно изменил значение настройки <code>[{args[0]}]</code> " \
					 f"на [<code>{args[1]}</code>]"
		)


	@loader.command()
	async def prodiacmd(self, app: Client, message: types.Message):
		"""Сгенерировать изображение с помощью Prodia API"""

		prompt = utils.get_args_raw(message)
		neg_prompt = ""
		if not prompt:
			return await utils.answer(
				message, "<emoji id=5312526098750252863>❌</emoji> <b>Вы не указали аргументы…</b>"
			)
		if "\n" in prompt:
			prompt, neg_prompt = prompt.split("\n", 1)

		if not neg_prompt or neg_prompt == "[]":
			neg_prompt = self.db.get(
				name="Prodia", key="neg_def",
				default="(bad_prompt:0.8), multiple persons, multiple views, extra hands, " \
						"ugly, lowres, bad quality, blurry, disfigured, extra limbs, missing limbs, deep fried, " \
						"cheap art, missing fingers, out of frame, cropped, bad art, face hidden, text, speech bubble, " \
						"stretched, bad hands, error, extra digit, fewer digits, worst quality, low quality, " \
						"normal quality, mutated, mutation, deformed, severed, dismembered, corpse, pubic, poorly drawn, " \
						"(((deformed hands))), (((more than two hands))), (((deformed body))), ((((mutant))))"
			)

		mid = name_models[self.db.get("Prodia", "model", "StableDiffusion V1.5")]
		model = self.db.get("Prodia", "model", "StableDiffusion V1.5")
		cfg = self.db.get("Prodia", "cfg", 20)
		sampler = self.db.get("Prodia", "sampler", "Euler")
		steps = self.db.get("Prodia", "steps", 30)

		neg_out = f"\n<b><i>Отрицательный запрос:</i></b> <code>{neg_prompt}</code>" if neg_prompt else ""
		msg = await utils.answer(
			message,
			f"🎨 <b>Работаю над изображением…</b>\n"
			f"<b>Запрос:</b> <code>{prompt}</code>{neg_out}\n\n"
			f"<b>Указанные параметры:</b>\n"
			f"<b><i>Модель:</i></b> <code>{model}</code> — ID <code>{mid}</code>\n"
			f"<b><i>CFG:</i></b> <code>{cfg}</code>\n"
			f"<b><i>Сэмплер:</i></b> <code>{sampler}</code>\n"
			f"<b><i>Шаги:</i></b> <code>{steps}</code>",
		)

		pars = {
			"new": "true",
			"prompt": prompt,
			"model": mid,
			"negative_prompt": neg_prompt,
			"steps": steps,
			"cfg": cfg,
			"seed": random.randint(0, 1000000000),
			"sampler": sampler,
			"aspect_ratio": "square",
		}

		async with aiohttp.ClientSession() as s:
			async with s.get(
				f"https://api.prodia.com/generate", params=pars
			) as r:
				resp = await r.json()
				job_id = resp["job"]

			while True:
				async with s.get(f"https://api.prodia.com/job/{job_id}") as r:
					resp = await r.json()
					if resp["status"] == "succeeded":
						break
					await asyncio.sleep(0.15)

		await utils.answer(
			message=msg,
			response=f"https://images.prodia.xyz/{job_id}.png",
			photo=True,
			caption=f"🎉 <b>Ваше изображение готово!</b>\n" \
					f"<b>Запрос:</b> <code>{prompt}</code>{neg_out}\n\n" \
					f"<b><i>Модель:</i></b> <code>{model}</code> — ID <code>{mid}</code>\n" \
					f"<b><i>CFG:</i></b> <code>{cfg}</code>\n" \
					f"<b><i>Сэмплер:</i></b> <code>{sampler}</code>\n" \
					f"<b><i>Шаги:</i></b> <code>{steps}</code>\n"
		)
		await msg.delete()
