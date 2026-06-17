# File: quiz_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.properties import ListProperty, NumericProperty
from kivy.resources import resource_find
from utils import load_json, save_json, get_storage_path, normalize_mc_answer_to_letters, format_correct_answer, is_mc_selection_correct
import re
import webbrowser
from datetime import datetime
import os
import random


class QuizScreen(Screen):
    questions = ListProperty([])
    current_index = NumericProperty(0)
    correct_count = NumericProperty(0)
    asked_questions = ListProperty([])
    question_limit = NumericProperty(0)

    def on_enter(self):
        questions_path = resource_find('data/sc-200.json')
        if not questions_path:
            self.clear_widgets()
            self.add_widget(Label(text="Questions file not found!", font_size=20))
            return

        self.questions = load_json(questions_path)
        if not self.questions:
            self.clear_widgets()
            self.add_widget(Label(text="No questions loaded!", font_size=20))
            return

        random.shuffle(self.questions)  # Randomize order
        self._ask_question_limit()

    def _ask_question_limit(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        content.add_widget(Label(text="How many questions?", size_hint_y=None, height=30))
        txt = TextInput(multiline=False, input_filter='int')
        content.add_widget(txt)
        btn_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        btn_start = Button(text="Start")
        btn_cancel = Button(text="Cancel")
        btn_box.add_widget(btn_start)
        btn_box.add_widget(btn_cancel)
        content.add_widget(btn_box)
        popup = Popup(title="Quiz Length", content=content, size_hint=(0.8, 0.4), auto_dismiss=False)
        btn_start.bind(on_press=lambda *a: self._begin_quiz(txt.text, popup))
        btn_cancel.bind(on_press=lambda *a: (popup.dismiss(), self.exit_quiz(None)))
        popup.open()

    def _begin_quiz(self, value, popup):
        popup.dismiss()
        try:
            self.question_limit = int(value) if value.strip() else len(self.questions)
        except ValueError:
            self.question_limit = len(self.questions)
        self.questions = self.questions[:self.question_limit]
        self.current_index = 0
        self.correct_count = 0
        self.asked_questions = []
        self.display_question()

    def display_question(self):
        self.clear_widgets()
        if self.current_index >= len(self.questions):
            self.show_result()
            return

        q = self.questions[self.current_index]
        main_layout = BoxLayout(orientation='vertical')

        # --- Scrollable Question Area ---
        question_area = BoxLayout(orientation='vertical', size_hint=(1, 0.55))
        scroll = ScrollView(size_hint=(1, 1), bar_width=8, scroll_type=['bars', 'content'], do_scroll_x=True, do_scroll_y=True)
        vbox = BoxLayout(orientation='vertical', size_hint_x=None, size_hint_y=None, padding=[12, 18, 12, 10])
        vbox.bind(minimum_height=vbox.setter('height'), minimum_width=vbox.setter('width'))

        vbox.add_widget(Label(text=f"Question {self.current_index + 1} of {len(self.questions)}", font_size=18, size_hint_y=None, height=32, color=(1,1,1,1)))

        min_width = max(350, int(Window.width * 0.9))
        question_label = Label(text=q['question'], font_size=22, size_hint_y=None, size_hint_x=None, halign='left', valign='top', color=(1,1,1,1), text_size=(None, None))
        def update_label_size(instance, value):
            instance.width = max(min_width, instance.texture_size[0] + 32)
            instance.height = instance.texture_size[1] + 16
        question_label.bind(texture_size=update_label_size)
        vbox.add_widget(question_label)

        # Add image if present
        img_path = q.get('image') or q.get('Image')
        if img_path:
            resolved_img = resource_find(img_path)
            if resolved_img and os.path.exists(resolved_img):
                vbox.add_widget(KivyImage(source=resolved_img, size_hint=(1, None), height=180))
            else:
                print(f"Image not found: {img_path}")

        scroll.add_widget(vbox)
        question_area.add_widget(scroll)
        main_layout.add_widget(question_area)

        # --- Options & Actions Footer ---
        footer = BoxLayout(orientation='vertical', size_hint=(1, 0.45), spacing=10, padding=[20, 8, 20, 12])
        self.option_buttons = []
        option_btn_height = 56

        correct = q.get('answer') or q.get('answers')
        if not isinstance(correct, list):
            correct = [correct]

        options = q.get('options', [])
        options_lower = [o.strip().lower() for o in options]
        self.is_yes_no_multi = (len(options_lower) == 2 and sorted(options_lower) == ['no', 'yes'] and len(correct) > 1)

        if self.is_yes_no_multi:
            # Create Yes/No groups for each expected answer
            for i in range(len(correct)):
                for opt in options:
                    btn = ToggleButton(text=f"{i+1}:{opt}", group=f"yn_{i}", size_hint_y=None, height=option_btn_height, font_size=20)
                    self.option_buttons.append(btn)
                    footer.add_widget(btn)
        else:
            for idx, opt in enumerate(options):
                letter = chr(65 + idx)
                btn = ToggleButton(text=f"{letter}. {opt}", size_hint_y=None, height=option_btn_height, font_size=20, color=(1,1,1,1))
                self.option_buttons.append(btn)
                footer.add_widget(btn)

        submit_btn = Button(text="Submit", size_hint_y=None, height=option_btn_height, font_size=20, background_color=(0.16, 0.62, 0.28, 1))
        submit_btn.bind(on_press=self.on_submit)
        footer.add_widget(submit_btn)

        exit_btn = Button(text="Exit", size_hint_y=None, height=option_btn_height, font_size=20, background_color=(0.45, 0.12, 0.16, 1))
        exit_btn.bind(on_press=self.exit_quiz)
        footer.add_widget(exit_btn)

        main_layout.add_widget(footer)
        self.add_widget(main_layout)

    def on_submit(self, instance):
        q = self.questions[self.current_index]
        correct = q.get('answer') or q.get('answers')
        if not isinstance(correct, list):
            correct = [correct]

        options = q.get('options', [])

        if getattr(self, 'is_yes_no_multi', False):
            selected = []
            for i in range(len(correct)):
                group = f"yn_{i}"
                choice = None
                for b in self.option_buttons:
                    if b.group == group and b.state == 'down':
                        choice = b.text.split(':', 1)[1]
                        break
                selected.append(choice or '')
            explanation = q.get('explanation', '')
            url_pattern = r'(https?://\S+)'
            explanation = re.sub(url_pattern, r'[ref=\1]\1[/ref]', explanation)
            selected_norm = [s.strip().lower() for s in selected]
            correct_norm = [c.strip().lower() for c in correct]
            is_correct = selected_norm == correct_norm
            if is_correct:
                result_text = "Correct!\n" + explanation
                self.correct_count += 1
            else:
                correct_text = ', '.join(correct)
                result_text = f"Wrong.\nCorrect answer(s): {correct_text}\n{explanation}"
        else:
            # Convert user's selected options to letters by index
            selected_indices = [i for i, b in enumerate(self.option_buttons) if b.state == 'down']
            selected_letters = {chr(65 + i) for i in selected_indices}
            is_correct, correct_display = is_mc_selection_correct(options, correct, selected_letters)

            explanation = q.get('explanation', '')
            url_pattern = r'(https?://\S+)'
            explanation = re.sub(url_pattern, r'[ref=\1]\1[/ref]', explanation)

            if is_correct:
                result_text = "Correct!\n" + explanation
                self.correct_count += 1
            else:
                result_text = f"Wrong.\nCorrect answer(s): {correct_display}\n{explanation}"

        self.asked_questions.append(q)
        save_json(get_storage_path('asked_questions.json'), self.asked_questions)

        result_label = Label(text=result_text, font_size=20, color=(1,1,1,1), markup=True, halign='left', valign='top', size_hint=(None, None), width=Window.width * 0.7, text_size=(Window.width * 0.7, None), padding=(10, 10))
        result_label.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1]))
        result_label.bind(on_ref_press=lambda inst, url: webbrowser.open(url))

        scroll = ScrollView(size_hint=(1, 1), bar_width=8)
        scroll.add_widget(result_label)

        popup = Popup(title="Result", content=scroll, size_hint=(0.85, 0.55))
        popup.bind(on_dismiss=lambda *a: self._next_question())
        popup.open()

    def _next_question(self):
        self.current_index += 1
        self.display_question()

    def show_result(self):
        self.clear_widgets()
        total_questions = len(self.questions)
        correct_count = self.correct_count
        main_layout = BoxLayout(orientation='vertical')

        # Scrollable result area
        result_area = BoxLayout(orientation='vertical', size_hint=(1, 0.58), padding=20)
        scroll = ScrollView(size_hint=(1, 1))
        vbox = BoxLayout(orientation='vertical', size_hint_y=None)
        vbox.bind(minimum_height=vbox.setter('height'))

        if total_questions > 0:
            percent_score = int(correct_count / total_questions * 100)
            score = {"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "correct": correct_count, "total": total_questions, "score": percent_score}
            score_file = get_storage_path('score_history.json')
            history = load_json(score_file)
            if not isinstance(history, list):
                history = []
            history = [h for h in history if h.get('total', 0) > 0]
            history.append(score)
            save_json(score_file, history)

            result_img = "Images/meow.jpg" if percent_score >= 70 else "Images/tryharder.jpg"
            resolved_img = resource_find(result_img)
            if resolved_img:
                vbox.add_widget(KivyImage(source=resolved_img, size_hint=(1, None), height=180))

            vbox.add_widget(Label(text=f"Quiz complete!\nScore: {correct_count}/{total_questions} ({percent_score}%)", font_size=22, size_hint_y=None, height=60, color=(1,1,1,1)))
        else:
            vbox.add_widget(Label(text="No questions were answered. Quiz history not saved.", font_size=22, size_hint_y=None, height=60, color=(1,1,1,1)))

        scroll.add_widget(vbox)
        result_area.add_widget(scroll)
        main_layout.add_widget(result_area)

        # Footer buttons
        footer = BoxLayout(orientation='vertical', size_hint=(1, 0.42), spacing=10, padding=[20, 8, 20, 12])
        btn_history = Button(text="View History", size_hint_y=None, height=56, font_size=20, background_color=(0.19, 0.38, 0.77, 1))
        btn_history.bind(on_press=self.goto_history)
        footer.add_widget(btn_history)

        btn_restart = Button(text="Restart Quiz", size_hint_y=None, height=56, font_size=20, background_color=(0.17, 0.52, 0.72, 1))
        btn_restart.bind(on_press=lambda x: self.on_enter())
        footer.add_widget(btn_restart)

        btn_exit = Button(text="Exit", size_hint_y=None, height=56, font_size=20, background_color=(0.45, 0.12, 0.16, 1))
        btn_exit.bind(on_press=self.exit_quiz)
        footer.add_widget(btn_exit)

        main_layout.add_widget(footer)
        self.add_widget(main_layout)

    def goto_history(self, instance):
        self.manager.current = 'history_screen'

    def exit_quiz(self, instance):
        from kivy.app import App
        if self.current_index > 0:
            self.show_result()
        App.get_running_app().stop()
