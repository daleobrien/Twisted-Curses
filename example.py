#!/usr/bin/env python
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

from twistedcurses.app import App
from twistedcurses.list_box import ListBox
from twistedcurses.table import Table

class myApp(App):
    '''a simple app'''

    def __init__(self):
        self.menu = [('&File',None),
                     ('Te&st',None),
                     ('&Quit',self.quit )]

        App.__init__(self, 'Simple App', self.menu)

    def list_box_active_item_changed(self, arg):
        '''test callback, 
            here, we just add the callback to other listbox
        '''
        #self.widget('table').set_cells( (1,2,arg['active'],) )
        #self.widget('table').draw()

if __name__ == "__main__":
    '''   '''

    from twisted.internet import reactor

    app = myApp()

    # create a listbox (it's all we have so far)
    list_box = ListBox( (0,0), (20,-1), app.list_box_active_item_changed)

    list_box.add_rows( ('item 1', 'item 2', 'item 3',
                        'item 4', 'item 5', 'item 6',
                        'item 7', 'item 8', 'item 9') )
    app.add_widget( 'side', list_box )

    # add another listbox
    table = Table( (30,3),
                   (61,11),
                   None,
                   (5,5))
    table.set_cells( ((0,0,"0,0"),
                      (1,0,"1,0"),
                      (1,1,"1,1"),
                      (0,2,"0,2")))

    app.add_widget( 'table',table)

    app.set_editable('table',True)

    # twisted, ... Run Lola Run
    reactor.run()





