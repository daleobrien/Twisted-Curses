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

from twisted.python import log

import curses

from util import get_real_termial_size


class Table():

    def __init__(self, position, size, callback, dim):

        self.__editable = True

        self.w, self.h = size
        self.x, self.y = position
        self.y += 2

        # number of rows and columns (in that order)
        self.dim = dim

        self.__last_size = None
        self.__has_focus = False
        h, w = self.__size__()

        win = curses.newwin(h,
                            w,
                            self.y,
                            self.x)

        win.bkgd(' ', curses.color_pair(2))
        self.__panel__ = curses.panel.new_panel(win)

        # 2D grid

        self.__cells__ = [['' for c in range(dim[1])] for r in range(dim[0])]
        self.__changed = True

        # which row is selected
        self.selected = [0, 0]
        self.active = [0, 0]

        self.callback = callback
        #self.draw()

    def __size__(self):
        # look for springs (-1 means fix to screen dim)

        # use -1 , fill width,
        # -2, half of the width ??
        y, x = get_real_termial_size()
        w = x - self.x if self.w < 0 else self.w
        h = y - self.y if self.h < 0 else self.h

        if (w, h) != self.__last_size:
            self.__changed = True
            self.__last_size = (w, h)

        self.__column_width = self.w / self.dim[0] - 1  # (excluding the '|')
        self.__row_height = self.h / self.dim[1] - 1  # (excluding the '-')

        self.__max_number_of_displayed_rows__ = h - 2
        self.__max_number_of_displayed_cols__ = w / 4 - 2
        return h, w

    def set_editable(self, editable):

        if self.__editable != editable:
            self.__editable = editable
            if not editable and self.__has_focus:
                self.__changed = True
                self.__has_focus = False

    def set_focus(self, state):
        if state != self.__has_focus:
            self.__changed = True
            self.__has_focus = state

    def set_cells(self, cells):
        for c, r, value in cells:
            if self.__cells__[r][c] != value:
                self.__cells__[r][c] = value
                self.__changed = True

    def remove_row(self, index):
        '''TODO'''
        self.__changed = True

    def command(self, key):
        '''process commands'''

        if key == curses.KEY_UP and self.selected[0]:
            self.selected[0] -= 1
            self.__changed = True

        elif key == curses.KEY_DOWN and self.selected[0] + 1 < self.dim[0]:
            self.selected[0] += 1
            self.__changed = True

        elif key == curses.KEY_LEFT and self.selected[1]:
            self.selected[1] -= 1
            self.__changed = True

        elif key == curses.KEY_RIGHT and self.selected[1] + 1 < self.dim[1]:
            self.selected[1] += 1
            self.__changed = True

        elif key in (10,):

            curses.beep()
            if self.active != self.selected:
                self.active = self.selected[:]
                self.__changed = True

                if self.callback is not None:
                    r, c = self.active
                    self.callback({'active': self.__cells__[r][c]})

        return self.__changed

    def draw(self, force=False):

        new_size = self.__size__()

        log.msg("Table Draw called, new_size", new_size)

        win = self.__panel__.window()

        if self.__changed or force:

            # outline of table
            attr = curses.color_pair(2) if self.__has_focus else\
                curses.color_pair(1)

            win.resize(*new_size)
            win.clear()
            win.attrset(attr)
            win.box()

            # draw the internal gird
            h, w = self.__size__()
            for c in range(self.dim[1] - 1):
                x = (c + 1) * (self.__column_width + 1)
                win.vline(0, x, curses.ACS_TTEE, 1)
                win.vline(1, x, curses.ACS_VLINE, h - 2)
                win.vline(h - 1, x, curses.ACS_BTEE, 1)

            for r in range(self.dim[0] - 1):
                y = (r + 1) * (self.__row_height + 1)
                win.hline(y, 0, curses.ACS_LTEE, 1)
                win.hline(y, 1, curses.ACS_HLINE, w - 2)
                win.hline(y, w - 1, curses.ACS_RTEE, 1)

                # and draw the intersections or the grid lines
                for c in range(self.dim[1] - 1):
                    x = (c + 1) * (self.__column_width + 1)
                    win.hline(y, x, curses.ACS_PLUS, 1)

            # sometimes there are more items than will fit in the in the table,
            # so move a display window along as needed

            w = self.__column_width + 1
            h = self.__row_height + 1

            col_offset = 0
            if self.dim[1] > self.__max_number_of_displayed_cols__:
                a = self.dim[1] - self.__max_number_of_displayed_cols__
                b = max(self.selected[1] -\
                        self.__max_number_of_displayed_cols__ + 2, 0)
                col_offset = min(a, b)

            row_offset = 0
            if self.dim[0] > self.__max_number_of_displayed_rows__:
                a = self.dim[0] - self.__max_number_of_displayed_rows__
                b = max(self.selected[0] -\
                        self.__max_number_of_displayed_rows__ + 2, 0)
                row_offset = min(a, b)

            for row_no, row in enumerate(self.__cells__):
                for col_no, cell in enumerate(row):

                    # don't draw below the bottom
                    if (row_no >= row_offset and
                        row_no - row_offset < \
                            self.__max_number_of_displayed_rows__):

                        text = ("%s" % cell).rjust(self.__column_width - 1)
                        pos = [row_no, col_no]

                        if self.__editable:
                            attr = curses.color_pair(1) if self.active == pos\
                                else curses.color_pair(1)

                            if self.selected == pos:
                                attr |= curses.A_STANDOUT
                            if self.active == pos:
                                attr |= curses.A_UNDERLINE
                        else:
                            attr = curses.color_pair(1)

                        win.addstr(h * row_no + 1 + row_offset,
                                   w * col_no + 1 + col_offset,
                                   text,
                                   attr)

            win.refresh()

            self.__changed = False
