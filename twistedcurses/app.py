'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You have not received a copy of the GNU Lesser General Public License
    along with this program.  Please see <http://www.gnu.org/licenses/>.

'''

from twisted.internet.task import LoopingCall
from twisted.internet import reactor

import curses 

from curses.ascii import TAB

from curses import (initscr,
                    setupterm,
                    newwin,
                    endwin,
                    tigetnum,
                    start_color,
                    init_pair,
                    noecho,
                    echo,
                    cbreak,
                    curs_set,

                    KEY_END,
                    KEY_RESIZE,

                    COLOR_BLACK,
                    COLOR_BLUE,
                    COLOR_CYAN,
                    COLOR_GREEN,
                    COLOR_MAGENTA,
                    COLOR_RED,
                    COLOR_WHITE,
                    COLOR_YELLOW,

                    A_NORMAL,        # Normal display (no highlight)
                    A_STANDOUT,      # Best highlighting mode of the terminal.
                    A_UNDERLINE,     # Underlining
                    A_REVERSE,       # Reverse video
                    A_BLINK,         # Blinking
                    A_DIM,           # Half bright
                    A_BOLD,          # Extra bright or bold
                    A_PROTECT,       # Protected mode
                    A_INVIS,         # Invisible or blank mode
                    A_ALTCHARSET,    # Alternate character set
                    A_CHARTEXT,      # Bit-mask to extract a character
                    )


''' some attrs
    A_NORMAL        Normal display (no highlight)
    A_STANDOUT      Best highlighting mode of the terminal.
    A_UNDERLINE     Underlining
    A_REVERSE       Reverse video
    A_BLINK         Blinking
    A_DIM           Half bright
    A_BOLD          Extra bright or bold
    A_PROTECT       Protected mode
    A_INVIS         Invisible or blank mode
    A_ALTCHARSET    Alternate character set
    A_CHARTEXT      Bit-mask to extract a character

    COLOR_PAIR(n)   Color-pair number n 


'''

class CursesStdIO:
    """fake fd to be registered as a reader with the twisted reactor.
       Curses classes needing input should extend this"""

    def __init__(self):
        pass

    def fileno(self):
        """ We want to select on FD 0 """
        return 0

    def doRead(self):
        """called when input is ready"""

class App(CursesStdIO):

    def __init__(self, title='My App', menu={}):
        '''menu -> { 'file':callback, 'view':callback}
        '''

        curses.setupterm()
        self.__stdscr = initscr()
        self.__stdscr.nodelay(1)
        self.__stdscr.keypad(True)

        self.__screen__ = newwin(tigetnum('lines'),
                                 tigetnum('cols'),
                                 0,0)

        self.__last_size = (tigetnum('lines'), tigetnum('cols'))

        self.__focus__items = ['menu']
        self.__in_focus = 0

        start_color()

        # focus border
        init_pair(1, COLOR_BLUE, COLOR_BLACK)

        noecho()
        cbreak()
        # so we capture arrow keys, rather than excape squences
        curs_set(False)

        self.title = title
        self.__menu__ = menu
        self.__key_handler__ = {}

        # list of widgets
        self._widgets = {}

        # refresh
        self.draw(True)

        # so we can read stdio
        reactor.addReader(self)

        # hack, to allow it to resize, it's not the right way though
        #self.__check_screen_size_hack = LoopingCall(self.resize_hack)
        #self.__check_screen_size_hack.start(0.5,True)

    def add_widget(self, name, widget ):
        # TODO: change to meta programming, since we will have more the list boxes
        self._widgets[name] = widget
        if name not in self.__focus__items:
            self.__focus__items.append(name)
        self.draw(True)

    def widget(self, name ):
        if self._widgets.has_key(name):
            return self._widgets[name]
        return None

    def __draw_window(self):
        '''only really holds the menu bar, could only repaint part of it ...'''
        self.__screen__.box()
        self.__screen__.hline(2,1,curses.ACS_HLINE,tigetnum('cols')-2)

    def __draw_menu(self):
        position = 2
        for menu,callback in self.__menu__:
            text    = menu.split('&')
            hot_key = text[1][0]
            self.__screen__.addstr(1, position, text[0],     A_NORMAL)
            position += len(text[0])
            self.__screen__.addstr(1, position, hot_key,     A_UNDERLINE)
            position += 1 
            self.__screen__.addstr(1, position, text[1][1:], A_NORMAL)
            position += len(text[1][1:]) + 2

            self.__key_handler__['menu'] = { ord(hot_key): callback }

        # draw app title
        middle = (tigetnum('cols') - position )/2
        self.__screen__.addstr(1, middle, '=== '+self.title+" ===", A_NORMAL) 

    def __drawwidgets(self,force):
        # TODO meta programming
        # should be a list of child widgets
        for name,widget in self._widgets.items():
            widget.draw(force)

    def draw(self, force=False):
        '''draw everything, and all widgets'''

        curses.setupterm()
        _size = (tigetnum('lines'), tigetnum('cols'))

        if force or self.__last_size != _size:

            self.__last_size = _size

            self.__screen__.resize( *_size )
            self.__screen__.clear()
            self.__draw_window()
            self.__draw_menu()
            self.__screen__.refresh()

        self.__drawwidgets(force)

    def resize_hack(self):
        self.draw(True)

    def logPrefix(self):
        pass

    def connectionLost(self, reason):
        self.close()

    def close(self):
        """ clean up """
        curses.nocbreak()
        self.__stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def quit(self,key=None):
        echo()
        endwin()
        reactor.stop()

    def doRead(self):
        '''called when a character is waiting'''

        # doesn't seem to response to KEY_RESIZE,
        # like it did when I didn't use twisted ?
        # what has twsited got againt it ?
        key = self.__stdscr.getch()

        self.process_character(key)

    def process_character(self,c):
        #TAB, change focus
        if c in (TAB,):
            self.__in_focus += 1
            self.__in_focus %= (len(self.__focus__items))
            focus = self.__focus__items[self.__in_focus]

            for list_box_name,list_box in self._widgets.items():
                list_box.set_focus(focus==list_box_name)

            self.draw(True)

        else:
            focus = self.__focus__items[self.__in_focus]

            # TODO there a whole lot more special key events, need to check those too, e.g.  SUSPEND
            if c in (KEY_RESIZE,):
                self.draw()

            # menu handlers
            elif c in self.__key_handler__['menu']:
                if self.__key_handler__['menu'][c]:
                    self.__key_handler__['menu'][c](c)

            # custom handlers
            elif self.__key_handler__.has_key(focus) and c in self.__key_handler__[focus]:
                if self.__key_handler__[focus][c]:
                    self.__key_handler__[focus][c](c)

            # generic, say arrow keys to select items
            elif focus in self._widgets:
                self._widgets[focus].command(c)

            else:
                # TODO, pressing unued keys when it first starts up seems to blank the screen
                self.draw(True)

