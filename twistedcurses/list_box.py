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

from curses import (panel,
                    KEY_DOWN,
                    KEY_UP,
                    KEY_END,
                    KEY_HOME,
                    KEY_ENTER,
                    A_UNDERLINE,
                    tigetnum,
                    newwin,
                    ascii,
                    color_pair)

class ListBox():

    def __init__(self,position,size,callback):

        self.w,self.h = size
        self.x,self.y = position
        self.y += 2

        self.__last_size = None
        self.__has_focus = False
        h,w = self.__size__()

        self.__panel__ = panel.new_panel(newwin(h,w,self.y,self.x))

        self.__rows__    = []
        self.__changed   = True

        # which row is selected
        self.selected = 0
        self.active   = 0

        self.callback = callback
        self.draw()

    def __size__(self):
        # look for springs (-1 means fix to screen dim)

        # use -1 , fill width,
        # -2, half of the width ??
        w = tigetnum('cols')  - self.x if self.w < 0 else self.w
        h = tigetnum('lines') - self.y if self.h < 0 else self.h

        if (w,h) != self.__last_size:
            self.__changed   = True
            self.__last_size = (w,h)

        self.__max_number_of_displayed_rows__ = h-2
        return h,w

    def set_focus(self,state):

        if state != self.__has_focus:
            self.__changed   = True
            self.__has_focus = state

    def add_rows(self, rows):
        self.__rows__ += rows 
        self.__changed = True

    def remove_row(self,index):
        '''TODO'''
        self.__changed = True

    def command(self, key):
        '''process commands'''

        if key==KEY_UP and self.selected:
            self.selected -= 1
            self.__changed = True

        elif key==KEY_DOWN and self.selected+1 < len(self.__rows__):
            self.selected += 1
            self.__changed = True

        elif key in (KEY_ENTER,10): # ENTER doesn't work, but 10 does
            if self.active != self.selected:
                self.active = self.selected
                self.__changed = True

            if self.__changed and self.callback is not None:
                self.callback( {'active':self.__rows__[self.active]} )

        #self.draw()
        return self.__changed


    def draw(self,force=False):

        win = self.__panel__.window()
        win.resize( *self.__size__() )

        if self.__changed or force:

            self.__changed = False

            attr = color_pair(1) if self.__has_focus else color_pair(0)

            win.attrset(attr)
            win.clear()
            win.box()

            # sometimes there are more items than will fit in the in the visiable list,
            # so move a display window along as needed
            offset = 0
            if len(self.__rows__) > self.__max_number_of_displayed_rows__:
                offset = min( len(self.__rows__) - self.__max_number_of_displayed_rows__, 
                             max(self.selected -self.__max_number_of_displayed_rows__ + 2,0))

            for line_no,row in enumerate(self.__rows__):
                attr = color_pair(1) if self.active == line_no else color_pair(0)
                #if line_no == self.active:
                #    attr |= A_UNDERLINE

                # don't draw below the bottom
                if line_no>=offset  and line_no-offset < self.__max_number_of_displayed_rows__:
                    if self.selected == line_no:
                        win.addstr(line_no+1-offset,1,">%s"%row, attr)
                    else:
                        win.addstr(line_no+1-offset,2,row, attr)

            win.refresh()
