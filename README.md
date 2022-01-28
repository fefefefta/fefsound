fefsound - это консольное приложение для прослушивания музыки. Управление приложением идет посредством команд, список которых приведен ниже:

Команды set:

set login <ваш логин> - эта команда необходима для начала работы. Каждому логину сопоставляется собственное пространство для создания плейлистов и добавления музыки.

Команды show:

show playlists - выводит список всех плейлистов пользователя на экран в специальном интерфейсе. Кнопки управления интерфейсами определены в нижних строках этих интерфейсов.
show <название плейлиста> - выводит список треков плейлиста. 

Команды mk:

mk <название нового плейлиста> - создает новый плейлист с указанным названием. 

Команды add:

add <путь к папке> - добавляет музыку из выбранной папки. Например "add /home/vanya/music".
add from <путь к папке> - добавляет музыку из выбранной папки и дерева всех вложенных папок.
add to <название плейлиста> - для добавления треков из общего списка пользователя в какой-то плейлист.

Команда download:

download <ваш запрос> - скачивает трек с ютуба, добавляет его в плейлист all. Например "download у России три пути"

Команды del:

del playlist <название плейлиста> - удаляет указанный плейлист. Треки не удаляются, а остаются в общем плейлисте пользователя.
del track <название трека> - удаляет указанный трек из всех плейлистов пользователя, в том числе и из общего.
del from <название плейлиста> <название трека> - удаляет указанный трек из указанного плейлиста.

Дополнительные команды:

clear - очистить окно терминала.

exit - закрыть утилиту.