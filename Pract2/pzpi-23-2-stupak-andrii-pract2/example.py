import asyncio
import json
import time

class DiscordSnowflakeGenerator:
	"""Автономний генератор 64-бітних сортованих ID на основі міток часу."""
	def __init__(self, worker_id: int, datacenter_id: int):
		self.discord_epoch = 1420070400000  # Епоха Discord: 1 січня 2015 року
		self.worker_id = worker_id
		self.datacenter_id = datacenter_id
		self.sequence = 0
		self.last_timestamp = -1

	def _get_current_ms(self) -> int:
		return int(time.time() * 1000)

	def generate_id(self) -> int:
		timestamp = self._get_current_ms()

		if timestamp == self.last_timestamp:
			self.sequence = (self.sequence + 1) & 4095
			if self.sequence == 0:
				while timestamp <= self.last_timestamp:
					timestamp = self._get_current_ms()
		else:
			self.sequence = 0

		self.last_timestamp = timestamp

		# Порозрядне зміщення (Bit Shifting) для формування фінального 64-бітного ID
		return (
			((timestamp - self.discord_epoch) << 22) |
			(self.datacenter_id << 17) |
			(self.worker_id << 12) |
			self.sequence
		)


class DiscordGatewayProcessor:
	"""Сервіс обробки подій шлюзу з асинхронним фоновим воркером."""
	def __init__(self, worker_id: int, datacenter_id: int):
		self.id_generator = DiscordSnowflakeGenerator(worker_id, datacenter_id)
		self.task_queue = asyncio.Queue()  # Асинхронна черга для важких завдань

	async def background_worker(self):
		"""Нескінченний фоновий процес (Worker) для обслуговування черги."""
		while True:
			task = await self.task_queue.get()
			task_type = task.get("type")
			data = task.get("data")

			# Делегування важких операцій залежно від типу події
			if task_type == "INDEX_SEARCH":
				print(f"[Фон: Індексація]: Додавання повідомлення {data['id']} в ElasticSearch.")
				await asyncio.sleep(0.5)  # Імітація мережевого I/O з базою даних
			elif task_type == "PUSH_NOTIFY":
				print(f"[Фон: Push]: Масова розсилка сповіщень для сервера {data['guild_id']}.")
				await asyncio.sleep(0.3)  # Імітація запиту до Apple/Google Push сервісів

			self.task_queue.task_done()

	async def on_message_create(self, guild_id: int, content: str):
		"""Тригер шлюзу, що миттєво реагує на нове повідомлення в чаті."""
		# Автономна генерація унікального ID без звернення до центральної бази даних
		message_id = self.id_generator.generate_id()
		print(f"[Gateway]: Повідомлення {message_id} доставлено в чат.")

		# Неблокуюче скидання важких інфраструктурних задач в асинхронну чергу
		await self.task_queue.put({
			"type": "INDEX_SEARCH",
			"data": {"id": message_id, "content": content}
		})
		await self.task_queue.put({
			"type": "PUSH_NOTIFY",
			"data": {"guild_id": guild_id, "message_id": message_id}
		})