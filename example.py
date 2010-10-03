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
        self.widget('mid').add_rows( (arg['active'],) )
        self.widget('mid').draw()

if __name__ == "__main__":
    '''   '''

    from twisted.internet import reactor

    app = myApp()

    # create a listbox (it's all we have so far)
    list_box = ListBox( (0,0), (20,-1), app.list_box_active_item_changed)
    list_box.add_rows( ('item 1', 'item 2', 'item 3',
                        'item 4', 'item 5', 'item 6',
                        'item 7', 'item 8', 'item 9') )
    app.add_widget( 'side',list_box ) 

    # add another listbox
    list_box = ListBox( (30,10), (10,10),None)
    app.add_widget( 'mid',list_box)

    # twisted, ... Run Lola Run
    reactor.run()





