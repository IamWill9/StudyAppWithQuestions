import argparse
from quiz_app import load_questions, start_gui


def main():
    parser = argparse.ArgumentParser(description="Launch the quiz application")
    parser.add_argument('--file', default='questions/sc-200.json', help='Path to question JSON file')
    parser.add_argument('--count', type=int, default=5, help='Number of questions to ask')
    parser.add_argument('--dark', action='store_true', help='Enable dark mode')
    args = parser.parse_args()

    start_gui(args.file, args.count, dark_mode=args.dark)


if __name__ == '__main__':
    main()
