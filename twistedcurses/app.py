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

import curses
from curses import ascii

from signal import signal, SIGWINCH

from twisted.python import log


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

    def __init__(self, reactor, title='My App', menu={}):
        '''menu -> { 'file':callback, 'view':callback}
        '''

        log.startLogging(open('log.log', 'w'))
        self.__reactor = reactor

        signal(SIGWINCH, self.onResize)

        #curses.setupterm()
        self.__first_time_through = True

        self.__stdscr = curses.initscr()
        self.__stdscr.keypad(True)
        self.__stdscr.nodelay(True)

        self._menu = curses.newwin(curses.tigetnum('lines'),
                                   curses.tigetnum('cols'),
                                   0,
                                   0)

        self.__last_size = (curses.tigetnum('lines'),
                            curses.tigetnum('cols'))

        self.__focus__items = []
        self.__in_focus = 0

        curses.start_color()
        # focused colour
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)

        self.title = title
        self.__menu__ = menu
        self.__key_handler__ = {}

        # list of widgets
        self._widgets = {}

        # refresh
        self.draw(True)

        # so we can read stdio
        self.__reactor.addReader(self)

    def onResize(self, sig, stack):
        self.process_character(curses.KEY_RESIZE)

    def add_widget(self, name, widget):
        # TODO: change to meta programming, since we will have more the list
        # boxes
        self._widgets[name] = widget

        if name not in self.__focus__items:
            if len(self.__focus__items) == 0:
                widget.set_focus(True)
            self.__focus__items.append(name)

        self.draw(True)

    def set_editable(self, name, editable):
        '''allow widgets to be selectable (and thus editable) or now'''

        if name in self._widgets:
            self._widgets[name].set_editable(editable)

            if name in self.__focus__items and not editable:

                # might have to change which widget has focus, if we are
                # making the current selected widget write only
                if name == self.__focus__items[self.__in_focus]:
                    self.__in_focus = 0
                    self._widgets[self.__focus__items[self.__in_focus]]\
                        .set_focus(True)

                self.__focus__items.remove(name)
                self._widgets[name].set_focus(False)

            if name not in self.__focus__items and editable:
                self.__focus__items.append(name)

            self.draw(True)

    def widget(self, name):
        if name in self._widgets:
            return self._widgets[name]
        return None

    def __draw_menu(self):
        position = 2
        for menu, callback in self.__menu__:
            text = menu.split('&')
            hot_key = text[1][0]
            self._menu.addstr(1, position, text[0], curses.A_NORMAL)
            position += len(text[0])

            self._menu.addstr(1,
                              position,
                              hot_key,
                              curses.A_UNDERLINE | curses.A_BOLD)
            position += 1
            self._menu.addstr(1, position, text[1][1:], curses.A_NORMAL)
            position += len(text[1][1:]) + 2

            self.__key_handler__['menu'] = {ord(hot_key): callback}

        # draw app title
        middle = (curses.tigetnum('cols') - position) / 2

        self._menu.addstr(1, middle, '=== ' +\
            self.title + " ===", curses.A_NORMAL)

    def __drawwidgets(self, force):
        # TODO meta programming
        # should be a list of child widgets
        for name, widget in self._widgets.items():
            widget.draw(force)

    def draw(self, force=False):
        '''draw everything, and all widgets'''

        _size = (curses.tigetnum('lines'),
                 curses.tigetnum('cols'))

        if force or self.__last_size != _size:

            log.msg("App Draw called, new_size", _size)

            self._menu.resize(*_size)
            self._menu.clear()
            self._menu.hline(2,
                             1,
                             curses.ACS_HLINE,
                             curses.tigetnum('cols') - 2)
            self._menu.box()
            self.__draw_menu()

            self._menu.refresh()

        # draw children last
        self.__drawwidgets(force)

        self.__last_size = _size

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

    def quit(self, key=None):
        self.close()
        self.__reactor.stop()

    def doRead(self):
        '''Called when a character is waiting'''

        # this clears the screen ?
        key = self.__stdscr.getch()

        self.process_character(key)

    def process_character(self, c):

        log.msg("KEY PRESS")

        #TAB, change focus
        if c in (ascii.TAB,):
            log.msg("KEY TAB")
            self.__in_focus += 1
            self.__in_focus %= (len(self.__focus__items))
            focus = self.__focus__items[self.__in_focus]

            for widget_name, widget in self._widgets.items():
                widget.set_focus(focus == widget_name)

            self.draw(True)

        else:
            focus = self.__focus__items[self.__in_focus]

            # TODO there a whole lot more special key events, need to check
            # those too, e.g.  SUSPEND
            if c in (curses.KEY_RESIZE,):
                log.msg("KEY_RESIZE")
                self.draw(True)

            # menu handlers
            elif c in self.__key_handler__['menu']:
                if self.__key_handler__['menu'][c]:
                    self.__key_handler__['menu'][c](c)

            # custom handlers
            elif (focus in self.__key_handler__ and
                  c in self.__key_handler__[focus]):
                if self.__key_handler__[focus][c]:
                    self.__key_handler__[focus][c](c)

            # generic, say arrow keys to select items
            elif focus in self._widgets:
                if self._widgets[focus].command(c):
                    if self.__first_time_through:
                        self.draw(True)
                        self.__first_time_through = False
                    else:
                        self._widgets[focus].draw(False)

#
