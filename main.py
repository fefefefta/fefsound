from client import Client
from commands import *


my_client = Client()
terminal = CommandHandler(my_client)

print("Введите help, чтобы ознакомиться с командами.")
print("fefsound> ", end='')
while terminal.get_is_processing():
	"""
	здесь нужно принимать входящие команды в объект класса CommandHandler
	"""
	terminal.get_query(input())
	terminal.push_query()
	
