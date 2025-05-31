import sys
import random
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from ui_components import AnimatedButton, FadeLabel, NameInputDialog, GamePage, StartPage, GameSetupPage, GameOverPage, ThemePalette
from abc import ABC, abstractmethod

# Player classes
class Player(ABC):
    def __init__(self, name, is_bot=False):
        self.name = name
        self.is_bot = is_bot
        self.score = 0
        self.response_time = 0
        self.correct_answers = 0
        self.lives = 3
        self.avatar = random.choice(["👦", "👧", "🧑", "👩", "🤖", "👨", "👴", "👵"])

    @abstractmethod
    def answer(self, correct_answer, difficulty):
        pass

class HumanPlayer(Player):
    def __init__(self, name):
        super().__init__(name, is_bot=False)

    def answer(self, correct_answer=None, difficulty=None):
        pass

class BotPlayer(Player):
    def __init__(self, name="Math Bot"):
        super().__init__(name, is_bot=True)

    def answer(self, correct_answer, difficulty):
        think_time = random.uniform(0.5, 3.0 - (difficulty * 0.5))
        time.sleep(think_time)
        if random.random() < (0.8 + (0.05 * difficulty)):
            return correct_answer
        else:
            if isinstance(correct_answer, int):
                return correct_answer + random.choice([-2, -1, 1, 2])
            else:
                return correct_answer + random.choice([-0.5, -0.25, 0.25, 0.5])

class GameStats:
    def __init__(self):
        self.reset()

    def reset(self):
        self.question_number = 0
        self.start_time = time.time()
        self.players = []
        self.game_mode = 1
        self.difficulty = 1
        self.game_active = False

class QuestionGenerator:
    def __init__(self, level):
        self.level = level

    def generate_problem(self):
        if self.level == 1:
            return EasyProblemGenerator().generate()
        elif self.level == 2:
            return MediumProblemGenerator().generate()
        elif self.level == 3:
            return HardProblemGenerator().generate()
        else:
            raise ValueError("Invalid level")

class EasyProblemGenerator:
    def generate(self):
        op = random.choice(['+', '-', '*', '/'])
        if op == '+':
            return self.add()
        elif op == '-':
            return self.subtract()
        elif op == '*':
            return self.multiply()
        else:
            return self.divide()

    def add(self):
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        return f"{a} + {b}", a + b

    def subtract(self):
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        if a < b:
            a, b = b, a
        return f"{a} - {b}", a - b

    def multiply(self):
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        return f"{a} × {b}", a * b

    def divide(self):
        b = random.randint(1, 10)
        a = b * random.randint(1, 10)
        return f"{a} ÷ {b}", a / b

class MediumProblemGenerator:
    def generate(self):
        op = random.choice(['+', '-', '*', '/', 'mixed'])
        if op == '+':
            return self.add()
        elif op == '-':
            return self.subtract()
        elif op == '*':
            return self.multiply()
        elif op == '/':
            return self.divide()
        else:
            return self.mixed()

    def add(self):
        a = random.randint(10, 50)
        b = random.randint(10, 50)
        return f"{a} + {b}", a + b

    def subtract(self):
        a = random.randint(10, 50)
        b = random.randint(10, 50)
        if a < b:
            a, b = b, a
        return f"{a} - {b}", a - b

    def multiply(self):
        a = random.randint(2, 12)
        b = random.randint(2, 12)
        return f"{a} × {b}", a * b

    def divide(self):
        b = random.randint(2, 12)
        a = b * random.randint(2, 12)
        return f"{a} ÷ {b}", round(a / b, 2)

    def mixed(self):
        a = random.randint(2, 10)
        b = random.randint(2, 10)
        c = random.randint(2, 10)
        return f"{a} × {b} + {c}", a * b + c

class HardProblemGenerator:
    def generate(self):
        op = random.choice(['*+', '*-', '/+', '/mixed'])
        if op == '*+':
            return self.multiply_add()
        elif op == '*-':
            return self.multiply_subtract()
        elif op == '/+':
            return self.divide_add()
        else:
            return self.divide_mixed()

    def multiply_add(self):
        a = random.randint(5, 15)
        b = random.randint(5, 15)
        c = random.randint(5, 15)
        return f"({a} × {b}) + {c}", a * b + c

    def multiply_subtract(self):
        a = random.randint(5, 15)
        b = random.randint(5, 15)
        c = random.randint(5, 15)
        return f"({a} × {b}) - {c}", a * b - c

    def divide_add(self):
        a = random.randint(10, 20)
        b = random.randint(2, 10)
        a = a * b
        c = random.randint(5, 15)
        return f"({a} ÷ {b}) + {c}", (a // b) + c

    def divide_mixed(self):
        a = random.randint(10, 20)
        b = random.randint(2, 10)
        a = a * b
        c = random.randint(2, 10)
        d = random.randint(2, 10)
        return f"({a} ÷ {b}) × {c} + {d}", round((a / b) * c + d, 2)

class UIManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def show_start(self):
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.start_page)

    def show_setup(self):
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.setup_page)

    def show_game(self):
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.game_page)

    def show_game_over(self, winner=None):
        self.main_window.game_over_page.set_results(self.main_window.stats.players, winner)
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.game_over_page)

class PlayerManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def setup_players(self, num_players, game_mode):
        dialog = NameInputDialog(num_players, self.main_window)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            names = dialog.get_names()
            if game_mode == 1:
                self.main_window.stats.players = [HumanPlayer(name) for name in names]
            else:
                self.main_window.stats.players = [HumanPlayer(names[0]), BotPlayer()]

    def enable_disable_player_inputs(self):
        for player, input_field, _ in self.main_window.game_page.player_inputs:
            input_field.setEnabled(player.lives > 0)

    def get_input_field(self, player):
        for p, field, _ in self.main_window.game_page.player_inputs:
            if p == player:
                return field
        return None

    def all_answered(self):
        return all(not field.isEnabled() for _, field, _ in self.main_window.game_page.player_inputs)

class TimerManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.question_start_time = 0
        self.timer = QtCore.QTimer(self.main_window)
        self.timer_interval = 100  # Milliseconds
        self.timer.timeout.connect(self.update_timer)

    def start_timer(self):
        """Start the timer and record the start time."""
        self.question_start_time = time.time()
        self.timer.start(self.timer_interval)

    def stop_timer(self):
        """Stop the timer."""
        self.timer.stop()

    def update_timer(self):
        """Update the timer display with elapsed time."""
        elapsed = time.time() - self.question_start_time
        self.main_window.game_page.update_timer(elapsed)

    def get_elapsed_time(self):
        """Return the elapsed time since the timer started."""
        return time.time() - self.question_start_time

class QuestionManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_problem = ""
        self.current_answer = 0
        self.current_level = 1
        self.timer_manager = TimerManager(main_window)  # Initialize TimerManager

    def load_next_question(self):
        if not self.main_window.stats.game_active:
            return

        self.main_window.stats.question_number += 1
        if self.main_window.stats.question_number > 15:
            self.main_window.controller.game_flow_manager.end_game()
            return

        self.current_level = (self.main_window.stats.question_number - 1) // 5 + 1
        level_names = ["Easy", "Medium", "Hard"]
        self.main_window.game_page.level_label.setText(f"{level_names[self.current_level-1]} Level")

        generator = QuestionGenerator(self.current_level)
        self.current_problem, self.current_answer = generator.generate_problem()
        self.main_window.game_page.question_label.setText(f"❓ {self.current_problem} = ?")

        self.timer_manager.start_timer()  # Start the timer using TimerManager

        self.main_window.controller.player_manager.enable_disable_player_inputs()

        if self.main_window.stats.game_mode == 2:
            bot = next((p for p in self.main_window.stats.players if p.is_bot), None)
            if bot and bot.lives > 0:
                QtCore.QTimer.singleShot(100, lambda: self.main_window.controller.bot_manager.bot_answer(bot))

class BotManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def bot_answer(self, bot):
        if not hasattr(self.main_window.controller.question_manager, 'current_answer') or bot.lives <= 0:
            return
        answer = bot.answer(self.main_window.controller.question_manager.current_answer,
                            self.main_window.stats.difficulty)
        for player, input_field, _ in self.main_window.game_page.player_inputs:
            if player == bot:
                input_field.setText(str(answer))
                self.main_window.controller.game_flow_manager.submit_answer(bot)
                break

class GameFlowManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def start_game(self, game_mode, num_players, difficulty):
        self.main_window.stats.reset()
        self.main_window.stats.game_mode = game_mode
        self.main_window.stats.difficulty = difficulty
        self.main_window.stats.game_active = True

        self.main_window.controller.player_manager.setup_players(num_players, game_mode)

        if not self.main_window.stats.players:
            return

        self.main_window.game_page.setup_player_inputs(self.main_window.stats.players)
        self.main_window.controller.ui_manager.show_game()
        self.main_window.controller.question_manager.load_next_question()

    def submit_answer(self, player):
        if not self.main_window.stats.game_active or player.lives <= 0:
            return

        input_field = self.main_window.controller.player_manager.get_input_field(player)
        if not input_field:
            return

        answer_text = input_field.text().strip()
        if not answer_text:
            return

        try:
            answer = float(answer_text) if '.' in answer_text else int(answer_text)
            if isinstance(self.main_window.controller.question_manager.current_answer, float):
                correct = abs(answer - self.main_window.controller.question_manager.current_answer) < 0.01
            else:
                correct = (answer == self.main_window.controller.question_manager.current_answer)
        except ValueError:
            QtWidgets.QMessageBox.warning(self.main_window, "Invalid Input", "Please enter a valid number!")
            return

        response_time = self.main_window.controller.question_manager.timer_manager.get_elapsed_time()
        player.response_time = response_time

        if correct:
            player.correct_answers += 1
            player.score += max(1, int(100 * (1 - min(1, response_time / 10.0))))
        else:
            player.lives -= 1
            if player.lives <= 0:
                input_field.setEnabled(False)

        input_field.setEnabled(False)
        self.main_window.game_page.update_leaderboard(self.main_window.stats.players)
        self.main_window.game_page.update_lives_display()
        self.check_game_over()

        if self.main_window.controller.player_manager.all_answered() and self.main_window.stats.game_active:
            self.main_window.controller.question_manager.timer_manager.stop_timer()
            QtCore.QTimer.singleShot(2000, self.main_window.controller.question_manager.load_next_question)

    def check_game_over(self):
        if not self.main_window.stats.game_active:
            return

        active_players = [p for p in self.main_window.stats.players if p.lives > 0]

        if len(active_players) <= 1:
            self.main_window.stats.game_active = False
            self.main_window.controller.question_manager.timer_manager.stop_timer()
            winner = active_players[0] if active_players else None
            self.main_window.game_page.show_game_over(winner)
            QtCore.QTimer.singleShot(3000, lambda: self.end_game(winner))

    def end_game(self, winner=None):
        self.main_window.controller.ui_manager.show_game_over(winner)

    def game_over(self, back_to_menu=False):
        self.main_window.controller.question_manager.timer_manager.stop_timer()
        if back_to_menu:
            self.main_window.controller.ui_manager.show_start()
        else:
            active_players = [p for p in self.main_window.stats.players if p.lives > 0]
            winner = active_players[0] if active_players else None
            self.end_game(winner)

    def play_again(self):
        self.main_window.controller.ui_manager.show_setup()

class GameController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.ui_manager = UIManager(main_window)
        self.player_manager = PlayerManager(main_window)
        self.question_manager = QuestionManager(main_window)
        self.bot_manager = BotManager(main_window)
        self.game_flow_manager = GameFlowManager(main_window)

    def show_start(self):
        self.ui_manager.show_start()

    def show_setup(self):
        self.ui_manager.show_setup()

    def start_game(self, game_mode, num_players, difficulty):
        self.game_flow_manager.start_game(game_mode, num_players, difficulty)

    def submit_answer(self, player):
        self.game_flow_manager.submit_answer(player)

    def game_over(self, back_to_menu=False):
        self.game_flow_manager.game_over(back_to_menu)

    def play_again(self):
        self.game_flow_manager.play_again()

class Mainbuster(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Brain Buster Math Levels Adventure")
        self.resize(1000, 800)
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        self.stacked_widget = QtWidgets.QStackedWidget()
        layout.addWidget(self.stacked_widget)

        self.controller = GameController(self)

        self.start_page = StartPage(self.controller.show_setup)
        self.setup_page = GameSetupPage(self.controller.start_game, self.controller.show_start)
        self.game_page = GamePage(self.controller.submit_answer, self.controller.game_over)
        self.game_over_page = GameOverPage(self.controller.play_again, self.controller.show_start)

        for page in [self.start_page, self.setup_page, self.game_page, self.game_over_page]:
            self.stacked_widget.addWidget(page)

        self.stats = GameStats()

        # Start the game
        self.controller.show_start()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    theme_palette = ThemePalette()
    theme_palette.apply_to(app)
    game = Mainbuster()
    game.show()
    sys.exit(app.exec_())