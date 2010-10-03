## ebook-maker

Simple Text based GUI framework which uses Twisted and Curses.

### Dependencies

 [Twisted](http://twistedmatrix.com/trac/)

### Usage

See example.py, which will create a text only application, ... something that could be used over an ssh connection.

              ┌──────────────────────────────────────────────────────────────────────────────┐
              │ File  Test  Quit            === Simple App ===                               │
              ┌──────────────────┐───────────────────────────────────────────────────────────│
              │ item 1           │                                                           │
              │ item 2           │                                                           │
              │>item 3           │                                                           │
              │ item 4           │                                                           │
              │ item 5           │                                                           │
              │ item 6           │                                                           │
              │ item 7           │                                                           │
              │ item 8           │                                                           │
              │ item 9           │                                                           │
              │                  │          ┌────────┐                                       │
              │                  │          │>item 3 │                                       │
              │                  │          │        │                                       │
              │                  │          │        │                                       │
              │                  │          │        │                                       │
              │                  │          │        │                                       │
              │                  │          │        │                                       │
              │                  │          │        │                                       │
              │                  │          │        │                                       │
              │                  │          └────────┘                                       │
              │                  │                                                           │
              │                  │                                                           │
              │                  │                                                           │
              │                  │                                                           │
              └──────────────────┘───────────────────────────────────────────────────────────┘

