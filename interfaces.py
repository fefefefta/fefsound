import curses
import pyglet
from time import sleep
from mutagen.mp3 import MP3


def draw_playlists(playlists, login):
    """
    Принимает список плейлистов. Создает интерфейс, обрабатывает выбор плейлиста.
    """
    def inner(window):
        key = 0 # Значение принятого символа в ASCII.
        cursor_y = 0 # Положение курсора строк. Он перемещается только по строками с
                     # именами плейлистов, а имена начинаются на первой строке, потому так.
        window.clear()
        window.refresh()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE) # Цвета для лэйбла приложения. 
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK) # Цвета для заглавия списка.
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE) # Цвета для строки с управлением 
                                                                    # и текущей строки плейлиста.
        curses.curs_set(0) # Отключение мигающей каретки. В параметрах уровень видимости (есть еще 1 и 2).

        height, width = window.getmaxyx()
        len_of_visible = height

        first_visible_playlist_index = 0
        last_visible_playlist_index = first_visible_playlist_index + len_of_visible - 1

        if len(playlists) > len_of_visible:
            visible_playlists = playlists[first_visible_playlist_index:last_visible_playlist_index+1]
        else:
            visible_playlists = playlists
                                                                    
        while key != ord('q'):

            window.clear()
            height, width = window.getmaxyx()

            if key == 10:                            # Обрабатываем нажатие enter, 
                return playlists[cursor_y] # в этом случае возвращаем текущую строку       
            elif key == curses.KEY_DOWN:
                cursor_y = cursor_move(len(playlists), cursor_y, value='down') # Обрабатываем стрелки так, 
            elif key == curses.KEY_UP:                         # чтобы курсор ходил только по списку плейлистов 
                cursor_y = cursor_move(len(playlists), cursor_y, value='up')  

            # cursor_y = cursor_y % len(list_of_playlists)

            height, width = window.getmaxyx()
            len_of_visible = height - 2
            last_visible_playlist_index = first_visible_playlist_index + len_of_visible - 1   

            if playlists[cursor_y] not in visible_playlists and cursor_y == last_visible_playlist_index + 1:
                first_visible_playlist_index += 1
                last_visible_playlist_index += 1
                
            elif playlists[cursor_y] not in visible_playlists and cursor_y == first_visible_playlist_index - 1:
                first_visible_playlist_index -= 1
                last_visible_playlist_index -= 1   

            if len(playlists) > len_of_visible:
                visible_playlists = playlists[first_visible_playlist_index:last_visible_playlist_index+1]
            else:
                visible_playlist = playlists

            # Обозначаем надписи
            fefsound_label = "fefsound v0.1"[:width-1]
            list_label = f"Список плейлистов {login}"[:width-1]
            control_menu_label = "Press 'q' to exit | enter to choose | arrows to move"[:width-1]

            window.addstr(0, 0, list_label, curses.color_pair(2))     # Добавляем все надписи на экран, раскрашивая их
            window.addstr(0, width-len(fefsound_label), fefsound_label, curses.color_pair(1))

            for y in range(len(visible_playlists)):

                if y == cursor_y - first_visible_playlist_index:
                    window.addstr(y+1, 0, visible_playlists[y], curses.color_pair(3))
                else:
                    window.addstr(y+1, 0, visible_playlists[y])

            window.addstr(height-1, 0, control_menu_label + " " * (width - len(control_menu_label) - 1), curses.color_pair(3))

            window.refresh()
            key = window.getch()

    return curses.wrapper(inner)


def duration_format(secs):
    secs = int(secs)
    mins = secs // 60
    secs %= 60
    return f'{mins}:{str(secs).zfill(2)}'


def draw_playlist(tracklist, name='all'):

    def inner(window):

        key = 0 # Значение принятого символа в ASCII.
        cursor_y = 0 # Положение курсора строк. Он перемещается только по строками с
                     # именами плейлистов, а имена начинаются на первой, а не нулевой строке, потому так.
        window.clear()
        window.refresh()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE) # Цвета для лэйбла приложения. 
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK) # Цвета для заглавия списка.
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE) # Цвета для строки с управлением 
                                                                    # и текущей строки плейлиста.
        curses.curs_set(0) # Отключение мигающей каретки. В параметрах уровень видимости (есть еще 1 и 2).

        player = pyglet.media.Player()
        current_track = None

        height, width = window.getmaxyx()
        len_of_visible = height

        first_visible_track_index = 0
        last_visible_track_index = first_visible_track_index + len_of_visible - 1

        if len(tracklist) > len_of_visible:
            visible_tracklist = tracklist[first_visible_track_index:last_visible_track_index+1]
        else:
            visible_tracklist = tracklist
                                        
        while key != ord('q'):

            window.clear()
            height, width = window.getmaxyx()

            if key == curses.KEY_DOWN:
                cursor_y = cursor_move(len(tracklist), cursor_y, value='down') # Обрабатываем стрелки так,
          
            elif key == curses.KEY_UP:                 # чтобы курсор ходил только по списку плейлистов 
                cursor_y = cursor_move(len(tracklist), cursor_y, value='up')

            elif key == 32:
                if player.playing:
                    if current_track == tracklist[cursor_y][0]:
                        player.pause()
                    else:
                        player.pause()
                        player.queue(pyglet.media.load(tracklist[cursor_y][1], streaming=False))
                        player.next_source()
                        current_track = tracklist[cursor_y][0]
                        player.play()
                else:
                    if player.source and current_track == tracklist[cursor_y][0]:
                        player.play()
                    elif player.source and current_track != tracklist[cursor_y][0]:
                        player.queue(pyglet.media.load(tracklist[cursor_y][1], streaming=False))
                        player.next_source()
                        current_track = tracklist[cursor_y][0]
                        player.play()
                    elif not player.source:
                        player.queue(pyglet.media.load(tracklist[cursor_y][1], streaming=False))
                        current_track = tracklist[cursor_y][0]
                        player.play()

            height, width = window.getmaxyx()
            len_of_visible = height - 2
            last_visible_track_index = first_visible_track_index + len_of_visible - 1   

            if tracklist[cursor_y] not in visible_tracklist and cursor_y == last_visible_track_index + 1:
                first_visible_track_index += 1
                last_visible_track_index += 1
                
            elif tracklist[cursor_y] not in visible_tracklist and cursor_y == first_visible_track_index - 1:
                first_visible_track_index -= 1
                last_visible_track_index -= 1   

            if len(tracklist) > len_of_visible:
                visible_tracklist = tracklist[first_visible_track_index:last_visible_track_index+1]
            else:
                visible_tracklist = tracklist          
            
            # Обозначаем надписи
            fefsound_label = "fefsound v0.1"[:width-1]
            list_label = f"Плейлист {name}"[:width-1]
            control_menu_label = "Press 'q' to exit | space to play | arrows to move"[:width-1]

            window.addstr(0, 0, list_label, curses.color_pair(2))     # Добавляем все надписи на экран, раскрашивая их
            window.addstr(0, width-len(fefsound_label), fefsound_label, curses.color_pair(1))

            for y in range(len(visible_tracklist)):

                if y == cursor_y - first_visible_track_index:
                    window.addstr(y+1, 0, visible_tracklist[y][0], curses.color_pair(3)) # Добавляю название выбранного трека.
                    # window.addstr(y+1, 36, duration_format(tracklist[y][1].duration))                      # Добавляю длительность.
                else:
                    window.addstr(y+1, 0, visible_tracklist[y][0])                       # То же самое для невыбранных треков.
                    # window.addstr(y+1, 36, duration_format(tracklist[y][1].duration))

            window.addstr(height-1, 0, control_menu_label + " " * (width - len(control_menu_label) - 1), curses.color_pair(3))

            window.refresh()
            key = window.getch()

    return curses.wrapper(inner)


def draw_making_playlist_interface(all_tracks, playlist_name):
    """
    Принимает список плейлистов. Создает интерфейс, обрабатывает выбор плейлиста.
    """
    def inner(window):
        new_tracklist = [] 

        key = 0 # Значение принятого символа в ASCII.
        cursor_y = 0 # Положение курсора строк. Он перемещается только по строками с
                     # именами плейлистов, а имена начинаются на первой строке, потому так.
        window.clear()
        window.refresh()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE) # Цвета для лэйбла приложения. 
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK) # Цвета для заглавия списка.
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE) # Цвета для строки с управлением и текущей строки плейлиста.
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED) # Цвета для выбранных треков
        curses.curs_set(0) # Отключение мигающей каретки. В параметрах уровень видимости (есть еще 1 и 2).
         
        height, width = window.getmaxyx()
        len_of_visible = height

        first_visible_track_index = 0
        last_visible_track_index = first_visible_track_index + len_of_visible - 1

        if len(all_tracks) > len_of_visible:
            visible_tracklist = all_tracks[first_visible_track_index:last_visible_track_index+1]
        else:
            visible_tracklist = all_tracks

        while key != ord('q'):

            window.clear()
            height, width = window.getmaxyx()

            if key == 10:                            # Обрабатываем нажатие enter, 
                return new_tracklist # в этом случае возвращаем текущую строку       
            elif key == curses.KEY_DOWN:
                cursor_y = cursor_move(len(all_tracks), cursor_y, value='down') # Обрабатываем стрелки так, 
            elif key == curses.KEY_UP:                         # чтобы курсор ходил только по списку плейлистов 
                cursor_y = cursor_move(len(all_tracks), cursor_y, value='up')  
            elif key == 32:
                if all_tracks[cursor_y] not in new_tracklist:
                    new_tracklist.append(all_tracks[cursor_y]) 
                else:
                    new_tracklist.remove(all_tracks[cursor_y])
            # cursor_y = cursor_y % len(list_of_playlists)

            height, width = window.getmaxyx()
            len_of_visible = height - 2
            last_visible_track_index = first_visible_track_index + len_of_visible - 1   

            if all_tracks[cursor_y] not in visible_tracklist and cursor_y == last_visible_track_index + 1:
                first_visible_track_index += 1
                last_visible_track_index += 1
                
            elif all_tracks[cursor_y] not in visible_tracklist and cursor_y == first_visible_track_index - 1:
                first_visible_track_index -= 1
                last_visible_track_index -= 1   

            if len(all_tracks) > len_of_visible:
                visible_tracklist = all_tracks[first_visible_track_index:last_visible_track_index+1]
            else:
                visible_tracklist = all_tracks

            # Обозначаем надписи
            fefsound_label = "fefsound v0.1"[:width-1]
            list_label = f"Выберите треки в {playlist_name}"[:width-1]
            control_menu_label = "Press 'q' to exit | enter to save | space to choose | arrows to move"[:width-1]

            window.addstr(0, 0, list_label, curses.color_pair(2))     # Добавляем все надписи на экран, раскрашивая их
            window.addstr(0, width-len(fefsound_label), fefsound_label, curses.color_pair(1))

            for y in range(len(visible_tracklist)):

                if y == cursor_y - first_visible_track_index:
                    window.addstr(y+1, 0, visible_tracklist[y][0], curses.color_pair(3))
                else:
                    if visible_tracklist[y] in new_tracklist:
                        window.addstr(y+1, 0, visible_tracklist[y][0], curses.color_pair(4))
                    else:   
                        window.addstr(y+1, 0, visible_tracklist[y][0])

            window.addstr(height-1, 0, control_menu_label + " " * (width - len(control_menu_label) - 1), curses.color_pair(3))

            window.refresh()
            key = window.getch()

        return new_tracklist.clear()

    return curses.wrapper(inner)


def cursor_move(len_of_list, current_num, value='down'):
    if value == 'down':
        current_num += 1
        if current_num == len_of_list:
            current_num -= 1
    elif value == 'up':
        current_num -= 1
        if current_num < 0:
            current_num += 1
    return current_num    

