Example usage:
```
"""
My first application
"""

from togax_commonglos import OptionWindow, create_webview_window, ScrollMainWindow, TabType
import toga
from toga.style.pack import Pack, COLUMN, ROW


class RootTab(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        main_box = toga.Box(children=[toga.Label(("Text" * 15 + "\n") * 100)])

        box = toga.Box(
                children=[
                    toga.Label('Dashboard', style=Pack(font_size=20, padding=5)),
                    toga.Button('Settings', on_press=lambda w: print("Settings clicked"), style=Pack(padding=5)),
                    toga.Label('Dashboard', style=Pack(flex=1, font_size=20, padding=5)),
                    toga.Button('Settings', on_press=lambda w: print("Settings clicked"), style=Pack(padding=5)),
                    toga.Label(("Text" * 15 + "\n") * 100),
                    toga.Button('Settings', on_press=lambda w: print("Settings clicked"), style=Pack(padding=5)),
                ], direction=COLUMN)
#        print(box)
        
        self.main_window = OptionWindow(
            [(toga.Box(
            children=[
                toga.Label('Dashboard', style=Pack(flex=1, font_size=20, padding=5)),
                toga.Button('Settings', on_press=lambda w: print("Settings clicked"), style=Pack(padding=5)),
            ],
            style=Pack(direction=ROW, background_color='#d3d3d3')
        ), "Hello", None, TabType.NORMAL),
#                (toga.OptionContainer(content=[("Tab 1", toga.Label("Content 1")), ("Tab 2", toga.Label("Content 2"))]), "Hello", None, TabType.NORMAL_FULL),
                (box, "World", None, TabType.SCROLL),
                (([], {"url": "https://google.com"}), "Website", None, TabType.WEB),
        ],
                                        )

#        self.main_window = create_webview_window(url="https://google.com")

#        self.main_window = ScrollMainWindow()
#        self.main_window.content = main_box
        
        self.main_window.show()

def main():
    return RootTab()
```
