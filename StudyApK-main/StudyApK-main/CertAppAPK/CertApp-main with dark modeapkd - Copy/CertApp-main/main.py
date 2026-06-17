# main.py

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from quiz_screen import QuizScreen
from history_screen import HistoryScreen
from kivy.resources import resource_add_path
import os

# Add images path or fallback to zip archive
images_dir = os.path.abspath("Images")
if os.path.isdir(images_dir):
    resource_add_path(images_dir)
else:
    zip_path = os.path.abspath("Images.zip")
    if os.path.exists(zip_path):
        resource_add_path(zip_path)
class QuizApp(App):
    """
    Main application class.
    Manages navigation between the quiz and history screens.
    """
    def build(self):
        sm = ScreenManager()
        sm.add_widget(QuizScreen(name='quiz_screen'))
        sm.add_widget(HistoryScreen(name='history_screen'))
        sm.current = 'quiz_screen'
        return sm

if __name__ == '__main__':
    QuizApp().run()
