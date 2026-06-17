import os
import json
import random
import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont

from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime


# --- Question Loader ---

def load_questions(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- Persistent Memory for Asked Questions ---
QUESTION_MEMORY_FILE = "asked_questions.json"

def load_asked_questions():
    if os.path.exists(QUESTION_MEMORY_FILE):
        with open(QUESTION_MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_asked_questions(questions):
    with open(QUESTION_MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

def reset_question_memory():
    if os.path.exists(QUESTION_MEMORY_FILE):
        os.remove(QUESTION_MEMORY_FILE)

# --- Global Quiz State ---
questions_asked = []
correct_answers = 0
question_queue = []
current_question = 0
# Questions answered correctly across sessions
question_memory = []

# --- Score History ---
SCORE_HISTORY_FILE = "score_history.json"

def load_score_history():
    if os.path.exists(SCORE_HISTORY_FILE):
        with open(SCORE_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_score_history(history):
    with open(SCORE_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def record_score(score, correct, total):
    history = load_score_history()
    history.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "correct": correct,
        "total": total,
        "score": score
    })
    save_score_history(history)


def mark_question_correct(question_data):
    """Record a correctly answered question to persistent memory."""
    global question_memory
    if question_data not in question_memory:
        question_memory.append(question_data)
        save_asked_questions(question_memory)


def close_program():
    """Safely and idempotently close the application."""
    global root
    if root is not None:
        try:
            root.quit()     # Exit the main loop cleanly
            root.destroy()  # Destroy the root window safely
        except tk.TclError:
            pass  # If it's already destroyed, ignore
        root = None


def create_scrollable_window(title):
    """Return a fullscreen scrollable window and its content frame."""
    win = tk.Toplevel(root)
    win.title(title)
    win.attributes('-fullscreen', True)
    win.resizable(True, True)
    win.protocol("WM_DELETE_WINDOW", close_program)

    canvas = tk.Canvas(win)
    scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas)

    frame.bind(
        "<Configure>",
        lambda event: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return win, frame

# --- Ask a Question Dispatcher ---
def ask_question():
    global current_question
    if current_question >= len(question_queue):
        end_quiz()
        return

    question_data = question_queue[current_question]
    question_number = current_question + 1

    question_type = question_data.get('type', 'multiple_choice')
    if question_type == 'multiple_choice':
        ask_multiple_choice(question_data, question_number)
    elif question_type == 'drag_and_drop':
        ask_drag_and_drop(question_data, question_number)

# --- Multiple Choice Logic ---
def ask_multiple_choice(question_data, question_number):
    """Display a multiple choice question."""
    global correct_answers

    question = question_data['question']
    options = question_data['options']
    correct = question_data['answer']
    explanation = question_data.get('explanation', 'No explanation available.')
    image_path = question_data.get('image')

    win, frame = create_scrollable_window(f"Question {question_number}")

    if image_path:
        try:
            base_dir = os.path.dirname(__file__)
            full_path = os.path.join(base_dir, image_path)
            img = Image.open(full_path)
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.imshow(img)
            ax.axis('off')
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)
        except Exception as e:
            print(f"Failed to show image: {e}")

    tk.Label(frame, text=f"Question {question_number}", font=("Arial", 18, "bold")).pack(pady=5)
    tk.Label(frame, text=question, wraplength=800, font=("Arial", 16)).pack(pady=10)

    user_vars = []
    for i, opt in enumerate(options):
        var = tk.IntVar()
        tk.Checkbutton(frame, text=f"{chr(65+i)}. {opt}", variable=var).pack(anchor='w')
        user_vars.append(var)

    def submit():
        global correct_answers, current_question
        selected = [chr(65+i) for i, var in enumerate(user_vars) if var.get() == 1]
        is_correct = set(selected) == set(correct)
        if is_correct:
            result = f"Correct!\nExplanation: {explanation}"
            correct_answers += 1
            mark_question_correct(question_data)
        else:
            result = f"Wrong! Correct answer: {', '.join(correct)}\nExplanation: {explanation}"
        show_result(win, result)

    tk.Button(frame, text="Submit", command=submit).pack(pady=10)
    tk.Button(frame, text="End Quiz", command=end_quiz).pack(pady=5)

# --- Drag and Drop Logic ---
def ask_drag_and_drop(question_data, question_number):
    """Display a drag and drop question."""
    global correct_answers

    question = question_data['question']
    options = question_data['options']
    correct = question_data['answer']
    explanation = question_data.get('explanation', '')

    win, frame = create_scrollable_window(f"Question {question_number}")

    image_path = question_data.get('image')
    if image_path:
        try:
            base_dir = os.path.dirname(__file__)
            full_path = os.path.join(base_dir, image_path)
            img = Image.open(full_path)
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.imshow(img)
            ax.axis('off')
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)
        except Exception as e:
            print(f"Failed to show image: {e}")

    tk.Label(frame, text=f"Question {question_number}", font=("Arial", 18, "bold")).pack(pady=5)
    tk.Label(frame, text=question, wraplength=800, font=("Arial", 16)).pack(pady=10)

    selected_vars = []
    for _ in correct:
        var = tk.StringVar()
        var.set("Select option")
        dropdown = tk.OptionMenu(frame, var, *options)
        dropdown.pack(pady=2)
        selected_vars.append(var)

    def submit():
        global correct_answers, current_question
        selected = [v.get().split("|")[0].strip() for v in selected_vars]
        expected = [opt.split("|")[0].strip() for opt in correct]
        if selected == expected:
            result = f"Correct!\nExplanation: {explanation}"
            correct_answers += 1
            mark_question_correct(question_data)
        else:
            result = f"Wrong!\nCorrect sequence: {', '.join(expected)}\nExplanation: {explanation}"
        show_result(win, result)

    tk.Button(frame, text="Submit", command=submit).pack(pady=10)
    tk.Button(frame, text="End Quiz", command=end_quiz).pack(pady=5)

# --- Show Result Popup ---
def show_result(parent, message):
    global current_question
    result_win = tk.Toplevel(root)
    result_win.title("Result")
    result_win.protocol("WM_DELETE_WINDOW", close_program)

    result_text = tk.Text(result_win, wrap="word", height=10, borderwidth=0, relief="flat", bg=result_win.cget("bg"))
    result_text.insert("1.0", message)
    result_text.config(state="disabled", cursor="arrow")
    result_text.pack(padx=20, pady=10, fill="both", expand=True)

    tk.Button(result_win, text="OK", command=lambda: (result_win.destroy(), parent.destroy(), next_question())).pack(pady=5)

# --- End Quiz Logic ---
def end_quiz():
    total_answered = current_question if current_question > 0 else 1
    score = (correct_answers / total_answered) * 100

    # record score history
    record_score(score, correct_answers, total_answered)

    # Image map based on score range
    result_images = {
        "pass": "Images/meow.jpg",
        "fail": "Images/tryharder.jpg"
    }

    # Determine which image to show
    image_file = result_images["pass"] if score >= 79 else result_images["fail"]

    end_win = tk.Toplevel(root)
    end_win.title("Quiz Ended")
    end_win.protocol("WM_DELETE_WINDOW", close_program)
    tk.Label(end_win, text=f"Score: {correct_answers}/{total_answered} ({score:.2f}%)").pack(pady=10)

    try:
        base_dir = os.path.dirname(__file__)
        full_path = os.path.join(base_dir, image_file)
        img = Image.open(full_path)

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.imshow(img)
        ax.axis('off')
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=end_win)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    except Exception as e:
        print(f"Failed to show result image: {e}")
        tk.Label(end_win, text=f"(Could not load image: {image_file})", fg="red").pack(pady=5)

    # show score history
    history = load_score_history()
    if history:
        tk.Label(end_win, text="Score History:").pack(pady=5)
        lines = [f"{h['date']}: {h['correct']}/{h['total']} ({h['score']:.2f}%)" for h in history]
        text = tk.Text(end_win, wrap="word", height=min(10, len(lines)+1), borderwidth=0, relief="flat", bg=end_win.cget("bg"))
        text.insert("1.0", "\n".join(lines))
        text.config(state="disabled")
        text.pack(padx=10, pady=5, fill="both", expand=True)

    tk.Button(end_win, text="Close", command=close_program).pack(pady=10)


# --- Next Question ---
def next_question():
    global current_question
    current_question += 1
    ask_question()

# --- Quiz Flow ---

def run_quiz(question_count, topics):
    global questions_asked, correct_answers, question_queue, current_question, question_memory
    questions_asked.clear()
    correct_answers = 0
    current_question = 0

    # GUI prompt for reset
    if messagebox.askyesno("Reset Memory", "Do you want to reset the previously asked questions?"):
        reset_question_memory()
        question_memory = []
    else:
        question_memory = load_asked_questions()

    all_questions = sum(topics.values(), [])
    remaining_questions = [q for q in all_questions if q not in question_memory]
    random.shuffle(remaining_questions)
    count = min(question_count, len(remaining_questions))
    question_queue = remaining_questions[:count]
    questions_asked[:] = question_queue[:]
    ask_question()



# --- Application Launcher ---

def apply_dark_mode(root):
    """Apply a simple dark theme to the given Tk root window."""
    root.tk_setPalette(
        background="#2e2e2e",
        foreground="#ffffff",
        activeBackground="#555555",
        activeForeground="#ffffff",
        highlightColor="#888888",
        highlightBackground="#555555",
    )


def start_gui(question_file, default_count=5, dark_mode=False):
    global root, question_count_var
    root = tk.Tk()
    root.title("SC-200 Quiz App")
    root.geometry("600x400")
    root.attributes("-fullscreen", False)
    root.resizable(True, True)
    root.protocol("WM_DELETE_WINDOW", close_program)

    if dark_mode:
        apply_dark_mode(root)

    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=14)
    root.option_add("*Font", default_font)
    tk.Label(root, text="How many questions would you like to answer?").pack(pady=10)
    question_count_var = tk.StringVar(value=str(default_count))
    tk.Entry(root, textvariable=question_count_var).pack(pady=5)

    def start_quiz_from_input():
        try:
            count = int(question_count_var.get())
            topics = load_questions(question_file)
            run_quiz(count, topics)
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a valid number.")

    tk.Button(root, text="Start Quiz", command=start_quiz_from_input).pack(pady=20)
    root.mainloop()
