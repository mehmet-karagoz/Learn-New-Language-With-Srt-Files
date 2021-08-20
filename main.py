from kivy.properties import StringProperty, ColorProperty
from kivy.utils import rgba
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import OneLineIconListItem, MDList

icons_item = {
    "folder": "My files",
    "star": "Starred",
    "history": "Recent",
    "upload": "Upload",
}


class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()
    text_color = ColorProperty()
    theme_text_color = StringProperty()

    def do_action(self):
        print(icons_item[self.icon])


class DrawerList(ThemableBehavior, MDList):
    pass


class SrtApp(MDApp):
    background_color = rgba("#2b2b31")

    def on_start(self):
        # add options to the list
        for icon_name in icons_item.keys():
            self.root.ids.md_list.add_widget(
                ItemDrawer(icon=icon_name, text=icons_item[icon_name],
                           theme_text_color="Custom",
                           text_color=rgba("#f4f4f4"))
            )


if __name__ == '__main__':
    SrtApp().run()
