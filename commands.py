import interfaces
import mimetypes
import sqlite3
import pytube
import magic
import time
import sys
import os


class CommandHandler:
	def __init__(self, client):
		"""
		Объект этого класса обрабатывает ввод пользователя и на его основе создает объекты команд.
		self.processing - флаг работы программы (см. условие цикла while в main.py и self.get_is_processing)
		self.client - объект класса Client, чтобы с ним взаимодействовать
		"""
		self.processing = True
		self.client = client

	def get_query(self, query_string):
		"""
		Создает список из команды, введенной пользователем.
		"""
		self.query = query_string.split()

	def push_query(self):
		"""
		Эта функция создает объекты команд, отправляя в конструктор параметры из ввода пользователя
		"""
		if self.query[0] == "exit":
			self.processing = False
		elif self.query[0] == "set":
			SetCommand(self.client, *self.query[1:])
			print("fefsound> ", end='')
		elif self.query[0] == "show" and self.client.get_is_accessed(): # команда show ... работает только
			ShowCommand(self.client, *self.query[1:])                   # для авторизованных пользователей
			print("fefsound> ", end='')									# как и последующие
		elif self.query[0] == "add" and self.client.get_is_accessed(): 
			AddCommand(self.client, *self.query[1:])
			print("fefsound> ", end='')
		elif self.query[0] == "mk" and self.client.get_is_accessed():
			MakeCommand(self.client, *self.query[1:])
			print("fefsound> ", end='')
		elif self.query[0] == "download" and self.client.get_is_accessed():
			DownloadCommand(self.client, *self.query[1:])
			print("fefsound> ", end='')
		elif self.query[0] == "del" and self.client.get_is_accessed():
			DeleteCommand(self.client, *self.query[1:])
			print("fefsound> ", end='')
		else:
			OtherCommand(self.query)
			print("fefsound> ", end='')
																		
	def get_is_processing(self):
		"""
		Используется в "жизненном" цикле работы программы. См. main.py.
		"""
		return self.processing


class Command:
	"""
	Класс, задающий единый способ инициализации объектов команд.
	От него наследуются все классы команд, кроме OtherCommand. Также в нем 
	хранятся полезные функции.	
	"""
	def __init__(self, client, *params):
		self.client = client
		self.params = params
		self.num_of_params = len(params)

	def is_playlist_exist(self, playlist_name):
		"""
		Проверка существования плейлиста по переданному названия для 
		текущего пользователя.
		"""
		login = self.client.get_login()
		with sqlite3.connect("data/tracks.db") as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM tracks WHERE login=? AND playlist=?", (login, playlist_name))
			return bool(cursor.fetchall())

	def is_user_exist(self, login):
		"""
		Этот метод принимает логин пользователя и проверяет, есть ли такой 
		пользователь в базе. Возвращает bool.
		"""
		with sqlite3.connect("data/users.db") as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM users WHERE login=?", (login, ))
			return bool(cursor.fetchone())

	def is_track_in_tracks(self, track, playlist):
		"""
		Проверяет, есть ли данный трек track в базе данных по 
		указанному плейлисту playlist для текущего пользователя.
		"""
		with sqlite3.connect("data/tracks.db") as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM tracks WHERE login=? AND track=? AND playlist=?;", (self.client.get_login(),
				track, playlist))
			
			if cursor.fetchone():
				return True
			return False

	def add_track_to_tracks_db(self, track, path, playlist):
		"""
		Добавляет трек track в базу данных по указанным параметрам.
		"""
		with sqlite3.connect("data/tracks.db") as conn:
			cursor = conn.cursor()
			cursor.execute("INSERT INTO tracks (login, playlist, track, path) VALUES (?, ?, ?, ?);", (self.client.get_login(),
			playlist, track, path))


	def add_user(self, login):
		"""
		Добавляет новый логин в базу данных users.db
		"""
		with sqlite3.connect("data/users.db") as conn:
			cursor = conn.cursor()
			cursor.execute("INSERT INTO users (login) VALUES (?)", (login, ))
			# TODO: добавлять плейлист all через вызов AddCommand при
			# добавлении нового пользователя.


	def get_tracks(self, playlist_name):
		"""
		Возвращает из базы данных список треков указанного плейлиста.
		Список состоит из кортежей вида (<название трека>, <путь>).
		"""
		with sqlite3.connect("data/tracks.db") as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM tracks WHERE login=? AND playlist=?", (self.client.get_login(), playlist_name))
			lines = cursor.fetchall()

			tracklist = []
			for line in lines:
				name = line[2]
				path = line[3]
				tracklist.append((name, path))
			return tracklist
		
	def get_playlists(self):
		"""
		Возвращает список плейлистов текущего пользователя.
		"""
		with sqlite3.connect("data/tracks.db") as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM tracks WHERE login=?", (self.client.get_login(), ))
			lines = cursor.fetchall()
			
			all_playlists = set()
			for line in lines:
				all_playlists = all_playlists | {line[1]}

			return all_playlists


class SetCommand(Command):
	"""
	Обрабатывает команды:

	set login <имя пользователя> - для регистрации в программе
	и для входа в аккаунт 	
	"""
	def __init__(self, client, *params):
		super().__init__(client, *params)

		if self.params[0] == "login":
			self.set_login()
			

	def set_login(self):
		"""
		Обработка команды >set login <...>
		"""
		if len(self.params) != 2:
			print("Команда ввода логина должна соответствовать схеме: \
				>set login <ваш логин>\nВведите команду help для получения справки.\n")
		
		elif self.client.get_is_accessed() == True: # Верная по написанию команда, но клиент уже осуществил вход
			print(f"Вы уже вошли в аккаунт {self.client.get_login()}")
		
		elif self.is_user_exist(self.params[1]) == False: # Верная по написанию команада, но пользователя не существует

			choice = input("Зарегистрировать пользователя? Y/n: ")
			if choice.lower() == 'y':
				self.add_user(self.params[1])
				self.client.set_login(self.params[1])
				self.client.make_access()
				print("Вы зарегистрировались.")
			else:
				pass

		else: # Верная по написанию команда, пользователь существует, входа не осуществлял
			self.client.make_access()
			self.client.set_login(self.params[1])
			print("Вы вошли в аккаунт")


class ShowCommand(Command):
	"""
	Обрабатывает команды типа show	
	"""
	def __init__(self, client, *params):
		super().__init__(client, *params)

		if self.params[0] == "playlists":
			self.show_all_playlists()
		elif len(self.params) == 1:
			self.show_playlist()
			

	def show_playlist(self):
		"""
		Обрабатывает команды вида >show <имя плейлиста>, 
		выводит на экран список треков заданного плейлиста.
		В случае, если будет нажат space на одном из треков, 
		заработает функция play_track(), трек заиграет
		"""
		if self.params[0] in self.get_playlists():
			tracklist = self.get_tracks(self.params[0])
			try:
				interfaces.draw_playlist(tracklist, name=self.params[0])
			except IndexError:
				print("Вы пока не добавили ни одного трека.")
		else:
			print("You have no playlist named like this")

	def show_all_playlists(self):
		"""
		Обрабатывает команду >show playlists, выводит на экран 
		список названий всех плейлистов с помощью функции draw_playlists.
		Она возвращает либо название некоторого плейлиста из списка, либо None.
		Если вернулось название, то функция меняет значение self.params[0] с 
		"playlists" на название плейлиста и запускает функцию self.show_playlist(). 
		"""
		list_of_playlists = list(self.get_playlists())

		for i in range(len(list_of_playlists)):
			if list_of_playlists[i] == "all":
				list_of_playlists[i], list_of_playlists[0] = list_of_playlists[0], list_of_playlists[i] 

		try:		
			selected_playlist = interfaces.draw_playlists(list_of_playlists, self.client.get_login())
			if selected_playlist:
				ShowCommand(self.client, selected_playlist)
			else:
				pass	
		except IndexError:
			print("Вы пока не создали ни одного плейлиста.")

			
# create table playlists (login TEXT, playlist TEXT, track TEXT, path TEXT)
# create table users (login TEXT)

class AddCommand(Command):
	"""
	"add from /"
	"add /"
	"add to music"

	add <путь к папке или файлу> - добавляет либо конкретный файл,
	либо все аудио-файлы из папки
	
	add from <путь к папке> - добавляет все аудио-файлы из дерева
	файловой системы, начиная с указанной папки
	
	add to <имя плейлиста> - открывает список всех треков пользователя
	и позволяет выбрать треки для добавления в указанный плейлист
	"""
	def __init__(self, client, *params):
		super().__init__(client, *params)

		if self.params[0] == "from":
			self.add_from_tree()
			
		elif self.params[0] == "to":
			self.add_to_playlist()
			
		else:
			self.add_from_dir()
			

	def add_from_dir(self):
		"""
		Добавление музыки из конкретной папки (путь к ней 
		находится в self.params)
		"""
		path = self.params[0]
		items = os.listdir(path)
		for item in items:
			if path[-1] == '/':
				full_path = path + item
			else:
				full_path = path + '/' + item

			try:
				if "audio" in magic.from_file(full_path, mime=True) or \
				"audio" in mimetypes.guess_type(full_path)[0]:
					if not self.is_track_in_tracks(item, 'all'):
						self.add_track_to_tracks_db(item, full_path, 'all')
			except:
				pass
		print("Аудиозаписи из этой папки добавлены.")
		
				

	def add_from_tree(self):
		"""
		Добавляет музыку из дерева папок, начиная с переданной в 
		self.params.
		"""
		path = self.params[1]
		if "/home" in path:
			for cur_dir, dirs, items in os.walk(path):
				for item in items:
					if cur_dir[-1] == '/':
						full_path = cur_dir + item
					else:
						full_path = cur_dir + '/' + item

					try:
						if "audio" in magic.from_file(full_path, mime=True):
							if not self.is_track_in_tracks(item, 'all'):
								self.add_track_to_tracks_db(item, full_path, 'all')
					except:
						pass

			print("Аудиозаписи добавлены.")
		else:
			print("Введите корректный путь. /help - для справки")

	def add_to_playlist(self):
		"""
		Открывает пользовательский интерфейс для добавления некоторых треков из
		общего плейлиста в один из уже созданных плейлистов.
		"""
		playlist_name = self.params[1]

		all_tracks = self.get_tracks("all")

		try:
			playlist_tracks = interfaces.draw_making_playlist_interface(all_tracks, playlist_name)

			for track_name, path in playlist_tracks:
				if not self.is_track_in_tracks(track_name, playlist_name):
					self.add_track_to_tracks_db(track_name, path, playlist_name)
		except IndexError:
			print("Вы пока не добавили ни одной аудиозаписи")


class MakeCommand(Command):
	"""
	Обрабатывает команды вида mk <название нового плейлиста> и создает плейлист с таким именем	
    """
	def __init__(self, client, *params):
		super().__init__(client, *params)

		if len(self.params) == 1:
			self.make_playlist()
			

	def make_playlist(self):
		"""
		Открывает пользовательский интерфейс для выбора некоторых треков из
		общего плейлиста. Из выбранных треков создает новый плейлист.
		"""
		if not self.is_playlist_exist(self.params[0]):
			all_tracks = self.get_tracks("all")

			try:
				playlist_tracks = interfaces.draw_making_playlist_interface(all_tracks, self.params[0])

				if playlist_tracks:
					for track_name, path in playlist_tracks:
						self.add_track_to_tracks_db(track_name, path, self.params[0])
			except IndexError:				
				print("Вы пока не добавили ни одной аудиозаписи")

class DeleteCommand(Command):
	"""
	Обрабатывает команды вида:
	del playlist <название плейлиста>
	del track <название трека>
	del from <название плейлиста> <название трека>
	"""
	def __init__(self, client, *params):
		super().__init__(client, *params)

		if len(self.params) == 2 and self.params[0] == "playlist":
			self.delete_playlist()
			
		elif self.params[0] == "track":
			tmp = ["track", " ".join(self.params[1:])]
			self.params = tmp
			self.delete_track()
			
		elif self.params[0] == "from":
			self.params = ["from", self.params[1], " ".join(self.params[2:])]
			self.delete_track_from()
			

	def delete_playlist(self):
		playlist_name = self.params[1]
		login = self.client.get_login()

		with sqlite3.connect('data/tracks.db') as conn:
			cursor = conn.cursor()
			cursor.execute("DELETE FROM tracks WHERE login=? AND playlist=?", (login, playlist_name))

	def delete_track(self):
		track_name = self.params[1]
		login = self.client.get_login()

		with sqlite3.connect('data/tracks.db') as conn:
			cursor = conn.cursor()
			cursor.execute("DELETE FROM tracks WHERE login=? AND track=?", (login, track_name))

	def delete_track_from(self):
		playlist_name = self.params[1]
		track_name = self.params[2]
		login = self.client.get_login()

		with sqlite3.connect('data/tracks.db') as conn:
			cursor = conn.cursor()
			cursor.execute("DELETE FROM tracks WHERE login=? AND track=? AND playlist=?", (login, track_name, playlist_name))


class DownloadCommand(Command):
	def __init__(self, client, *params):
		super().__init__(client, *params)

		if len(self.params) > 0:
			self.download_track()

	def download_track(self):
		query = ' '.join(self.params)
		path = '/home/fefta/coding/projects/fefsound/data/downloaded_music'

		search = pytube.Search(query) # получил search object
		yt = search.results[0] # получил youtube object, это первый ролик из списка результатов
		streams = yt.streams # получил все потоки по видео, теперь нужно получить аудио-поток как-то
		my_stream = streams.filter(only_audio=True)[0] # аудио поток
		my_stream.download(output_path=path, filename=query+'.mp3')

		name = query + '.mp3'
		self.add_track_to_tracks_db(name, path+'/'+query+'.mp3', 'all')
		print("Трек загружен и добавлен в плейлист all.")

class OtherCommand:
	def __init__(self, query):
		self.query = query

		if len(self.query) == 1 and self.query[0] == 'help':
			self.help_command()
		elif len(self.query) == 1 and self.query[0] == 'clear':
			self.clear_command()
		else:
			pass

	def help_command(self):
		with open("help.txt", 'r') as h:
			# for line in h.readlines():
			# 	print(line)
			print('\n', *h)

	def clear_command(self):
		os.system('clear')
		


