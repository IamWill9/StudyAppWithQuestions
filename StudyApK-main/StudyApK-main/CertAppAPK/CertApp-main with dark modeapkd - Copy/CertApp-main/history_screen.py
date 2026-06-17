# history_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
import os
from utils import load_json, get_storage_path

class HistoryScreen(Screen):
    """
    Screen to display the user's quiz attempt history.
    Loads from score_history.json and displays the last 10 valid attempts.
    """

    def on_enter(self):
        """
        Loads history from JSON and displays recent attempts.
        """
        history = load_json(get_storage_path('score_history.json'))
        if not isinstance(history, list):
            history = []

        # Filter out bogus zero-attempts, show most recent first
        valid_history = [h for h in history if h.get('total', 0) > 0]
        recent = valid_history[-10:][::-1]  # Last 10, newest first

        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        layout.add_widget(Label(text="Quiz History (Last 10 Attempts)", font_size=22))

        if not recent:
            layout.add_widget(Label(text="No history yet. Complete a quiz to see your results.", font_size=18))
        else:
            for h in recent:
                entry = f"{h['date']} - {h['correct']}/{h['total']} ({h['score']}%)"
                layout.add_widget(Label(text=entry, font_size=16))

        btn_reset = Button(text="Reset Learned Questions", size_hint=(1, 0.15))
        btn_reset.bind(on_press=self.reset_learned_questions)
        layout.add_widget(btn_reset)

        btn_quiz = Button(text="Back to Quiz", size_hint=(1, 0.15))
        btn_quiz.bind(on_press=self.goto_quiz)
        layout.add_widget(btn_quiz)

        self.add_widget(layout)

    def goto_quiz(self, instance):
        """
        Navigates back to the quiz screen.
        """
        self.manager.current = 'quiz_screen'

    def reset_learned_questions(self, instance):
        """Delete files tracking learned questions and show confirmation."""
        removed = []
        for fname in ['correct_questions.json', 'asked_questions.json']:
            path = get_storage_path(fname)
            if os.path.exists(path):
                try:
                    os.remove(path)
                    removed.append(fname)
                except Exception as e:
                    print(f"Error removing {fname}: {e}")

        if removed:
            msg = "\n".join([f"Deleted {name}" for name in removed])
        else:
            msg = "No learned question files found."

        popup = Popup(title="Reset Learned Questions",
                      content=Label(text=msg),
                      size_hint=(0.8, 0.4))
        popup.open()
