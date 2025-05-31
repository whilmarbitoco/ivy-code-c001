import sys
import random
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from ui_components import AnimatedButton, FadeLabel, NameInputDialog, GamePage, StartPage, GameSetupPage, GameOverPage, ThemePalette
from abc import ABC, abstractmethod


# Constant Values
QUESTION_LIMIT = 15
INITIAL_LIVES = 3

class Player(ABC):
    def __init__(self, name, is_bot=False):
        self.name = name
        self.is_bot = is_bot
        self.score = 0
        self.response_time = 0
        self.correct_answers = 0
        self.lives = INITIAL_LIVES
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

# --- Problem Generator Interface (remains unchanged) ---
class ProblemGenerator(ABC):
    """
    An abstract base class that defines the interface for all problem generators.
    All concrete problem generator classes must implement the 'generate' method.
    """
    @abstractmethod
    def generate(self):
        pass

# --- NEW: Abstract Base Class for Arithmetic Operations ---
class MathOperation(ABC):
    """
    Abstract base class for a single math operation (e.g., addition, subtraction).
    Defines the interface for generating operands and the problem string/answer.
    """
    def __init__(self, num_range_a, num_range_b):
        self.num_range_a = num_range_a
        self.num_range_b = num_range_b

    def _generate_operands(self):
        a = random.randint(*self.num_range_a)
        b = random.randint(*self.num_range_b)
        return a, b

    @abstractmethod
    def get_problem(self):
        pass

class AdditionOperation(MathOperation):
    def get_problem(self):
        a, b = self._generate_operands()
        return f"{a} + {b}", a + b

class SubtractionOperation(MathOperation):
    def get_problem(self):
        a, b = self._generate_operands()
        a, b = max(a, b), min(a, b)
        return f"{a} - {b}", a - b

class MultiplicationOperation(MathOperation):
    def get_problem(self):
        a, b = self._generate_operands()
        return f"{a} × {b}", a * b

class DivisionOperation(MathOperation):
    def get_problem(self):
        b = random.randint(*self.num_range_b)
        a = b * random.randint(*self.num_range_a)
        return f"{a} ÷ {b}", a / b

class OperationFactory:
    """
    A factory to create specific MathOperation instances based on an operator symbol.
    This centralizes the creation of basic arithmetic operations.
    """
    _OPERATIONS = {
        '+': AdditionOperation,
        '-': SubtractionOperation,
        '*': MultiplicationOperation,
        '/': DivisionOperation,
    }

    @staticmethod
    def get_operation(operator_symbol, num_range_a, num_range_b):
        operation_class = OperationFactory._OPERATIONS.get(operator_symbol)
        if not operation_class:
            raise ValueError(f"Unknown operator: {operator_symbol}")
        return operation_class(num_range_a, num_range_b)


class EasyProblemGenerator(ProblemGenerator):
    """
    Generates easy math problems using basic arithmetic operations.
    It delegates the actual operation generation to the OperationFactory.
    """
    def generate(self):
        op_symbol = random.choice(['+', '-', '*', '/'])
        # Easy problems use numbers from 1 to 20 for both operands
        operation = OperationFactory.get_operation(op_symbol, (1, 20), (1, 20))
        return operation.get_problem()

class MediumProblemGenerator(ProblemGenerator):
    """
    Generates medium math problems, including basic operations and mixed operations.
    Basic operations delegate to OperationFactory, while mixed operations are defined here.
    """
    def generate(self):
        op_choice = random.choice(['+', '-', '*', '/', 'mixed'])

        if op_choice == 'mixed':
            a = random.randint(2, 10)
            b = random.randint(2, 10)
            c = random.randint(2, 10)
            return f"{a} × {b} + {c}", a * b + c
        else:
            if op_choice in ['+', '-']:
                operation = OperationFactory.get_operation(op_choice, (10, 50), (10, 50))
            elif op_choice in ['*', '/']:
                operation = OperationFactory.get_operation(op_choice, (2, 12), (2, 12))
            else:
                raise ValueError(f"Unexpected operator choice: {op_choice}")
            return operation.get_problem()

class HardProblemGenerator(ProblemGenerator):
    """
    Generates hard math problems, which are typically multi-step or complex compositions.
    These are defined directly within this class as they represent specific problem structures
    for the hard difficulty, not just single arithmetic operations.
    """
    def generate(self):
        op_type = random.choice(['multiply_add', 'multiply_subtract', 'divide_add', 'divide_mixed'])

        if op_type == 'multiply_add':
            a = random.randint(5, 15)
            b = random.randint(5, 15)
            c = random.randint(5, 15)
            return f"({a} × {b}) + {c}", a * b + c
        elif op_type == 'multiply_subtract':
            a = random.randint(5, 15)
            b = random.randint(5, 15)
            c = random.randint(5, 15)
            return f"({a} × {b}) - {c}", a * b - c
        elif op_type == 'divide_add':
            b_div = random.randint(2, 10)
            a_div = b_div * random.randint(10, 20)
            c_add = random.randint(5, 15)
            return f"({a_div} ÷ {b_div}) + {c_add}", (a_div // b_div) + c_add
        elif op_type == 'divide_mixed':
            b_div = random.randint(2, 10)
            a_div = b_div * random.randint(10, 20)
            c_mul = random.randint(2, 10)
            d_add = random.randint(2, 10)
            return f"({a_div} ÷ {b_div}) × {c_mul} + {d_add}", round((a_div / b_div) * c_mul + d_add, 2)
        else:
            raise ValueError(f"Unexpected operator type: {op_type}")


class QuestionGenerator:
    _GENERATORS = {
        1: EasyProblemGenerator,
        2: MediumProblemGenerator,
        3: HardProblemGenerator,
    }

    def __init__(self, level):
        self.level = level
        if self.level not in self._GENERATORS:
            raise ValueError(f"Invalid level: {level}. No problem generator registered for this level.")
        self._problem_generator = self._GENERATORS[self.level]()

    def generate_problem(self):
        return self._problem_generator.generate()

class UIManager:
    def __init__(self, game_app):
        self.game_app = game_app

    def show_start(self):
        self.game_app.stacked_widget.setCurrentWidget(self.game_app.start_page)

    def show_setup(self):
        self.game_app.stacked_widget.setCurrentWidget(self.game_app.setup_page)

    def show_game(self):
        self.game_app.stacked_widget.setCurrentWidget(self.game_app.game_page)

    def show_game_over(self, winner=None):
        self.game_app.game_over_page.set_results(self.game_app.stats.players, winner)
        self.game_app.stacked_widget.setCurrentWidget(self.game_app.game_over_page)


class PlayerManager:
    def __init__(self, game_app):
        self.game_app = game_app

    def setup_players(self, num_players, game_mode):
        dialog = NameInputDialog(num_players, self.game_app)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            names = dialog.get_names()
            if game_mode == 1:
                self.game_app.stats.players = [HumanPlayer(name) for name in names]
            else:
                self.game_app.stats.players = [HumanPlayer(names[0]), BotPlayer()]

    def enable_disable_player_inputs(self):
        for player, input_field, _ in self.game_app.game_page.player_inputs:
            input_field.setEnabled(player.lives > 0)

    def get_input_field(self, player):
        for p, field, _ in self.game_app.game_page.player_inputs:
            if p == player:
                return field
        return None

    def all_answered(self):
        return all(not field.isEnabled() for _, field, _ in self.game_app.game_page.player_inputs)


class TimerManager:
    def __init__(self, game_app):
        self.game_app = game_app
        self.question_start_time = 0
        self.timer = QtCore.QTimer(self.game_app)
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
        self.game_app.game_page.update_timer(elapsed)

    def get_elapsed_time(self):
        """Return the elapsed time since the timer started."""
        return time.time() - self.question_start_time


class QuestionManager:
    def __init__(self, game_app):
        self.game_app = game_app
        self.current_problem = ""
        self.current_answer = 0
        self.current_level = 1
        self.timer_manager = TimerManager(game_app)

    def load_next_question(self):
        if not self.game_app.stats.game_active:
            return

        self.game_app.stats.question_number += 1
        if self.game_app.stats.question_number > QUESTION_LIMIT:
            self.game_app.controller.game_flow_manager.end_game()
            return

        self.current_level = (self.game_app.stats.question_number - 1) // 5 + 1
        level_names = ["Easy", "Medium", "Hard"]
        self.game_app.game_page.level_label.setText(f"{level_names[self.current_level-1]} Level")

        generator = QuestionGenerator(self.current_level)
        self.current_problem, self.current_answer = generator.generate_problem()
        self.game_app.game_page.question_label.setText(f"❓ {self.current_problem} = ?")

        self.timer_manager.start_timer()

        self.game_app.controller.player_manager.enable_disable_player_inputs()

        if self.game_app.stats.game_mode == 2: # If playing against a bot
            bot = next((p for p in self.game_app.stats.players if p.is_bot), None)
            if bot and bot.lives > 0:
                QtCore.QTimer.singleShot(100, lambda: self.game_app.controller.bot_manager.bot_answer(bot))


class BotManager:
    def __init__(self, game_app):
        self.game_app = game_app

    def bot_answer(self, bot):
        if not hasattr(self.game_app.controller.question_manager, 'current_answer') or bot.lives <= 0:
            return
        answer = bot.answer(self.game_app.controller.question_manager.current_answer,
                            self.game_app.stats.difficulty)
        for player, input_field, _ in self.game_app.game_page.player_inputs:
            if player == bot:
                input_field.setText(str(answer))
                self.game_app.controller.game_flow_manager.submit_answer(bot)
                break

class GameFlowManager:
    def __init__(self, game_app):
        self.game_app = game_app

    def start_game(self, game_mode, num_players, difficulty):
        self.game_app.stats.reset()
        self.game_app.stats.game_mode = game_mode
        self.game_app.stats.difficulty = difficulty
        self.game_app.stats.game_active = True

        self.game_app.controller.player_manager.setup_players(num_players, game_mode)

        if not self.game_app.stats.players:
            return

        self.game_app.game_page.setup_player_inputs(self.game_app.stats.players)
        self.game_app.controller.ui_manager.show_game()
        self.game_app.controller.question_manager.load_next_question()

    def submit_answer(self, player):
        if not self.game_app.stats.game_active or player.lives <= 0:
            return

        input_field = self.game_app.controller.player_manager.get_input_field(player)
        if not input_field:
            return

        answer_text = input_field.text().strip()
        if not answer_text:
            return

        try:
            answer = float(answer_text) if '.' in answer_text else int(answer_text)
            if isinstance(self.game_app.controller.question_manager.current_answer, float):
                correct = abs(answer - self.game_app.controller.question_manager.current_answer) < 0.01
            else:
                correct = (answer == self.game_app.controller.question_manager.current_answer)
        except ValueError:
            QtWidgets.QMessageBox.warning(self.game_app, "Invalid Input", "Please enter a valid number!")
            return

        response_time = self.game_app.controller.question_manager.timer_manager.get_elapsed_time()
        player.response_time = response_time

        if correct:
            player.correct_answers += 1
            # Score calculation: Faster correct answers get more points
            player.score += max(1, int(100 * (1 - min(1, response_time / 10.0))))
        else:
            player.lives -= 1
            if player.lives <= 0:
                input_field.setEnabled(False)

        input_field.setEnabled(False) # Disable input after submission
        self.game_app.game_page.update_leaderboard(self.game_app.stats.players)
        self.game_app.game_page.update_lives_display()
        self.check_game_over()

        if self.game_app.controller.player_manager.all_answered() and self.game_app.stats.game_active:
            self.game_app.controller.question_manager.timer_manager.stop_timer()
            QtCore.QTimer.singleShot(2000, self.game_app.controller.question_manager.load_next_question)

    def check_game_over(self):
        if not self.game_app.stats.game_active:
            return

        active_players = [p for p in self.game_app.stats.players if p.lives > 0]

        if len(active_players) <= 1:
            self.game_app.stats.game_active = False
            self.game_app.controller.question_manager.timer_manager.stop_timer()
            winner = active_players[0] if active_players else None
            self.game_app.game_page.show_game_over(winner) # Update game page to show game over state
            QtCore.QTimer.singleShot(3000, lambda: self.end_game(winner)) # Delay before transitioning

    def end_game(self, winner=None):
        self.game_app.controller.ui_manager.show_game_over(winner)

    def game_over(self, back_to_menu=False):
        self.game_app.controller.question_manager.timer_manager.stop_timer()
        if back_to_menu:
            self.game_app.controller.ui_manager.show_start()
        else:
            active_players = [p for p in self.game_app.stats.players if p.lives > 0]
            winner = active_players[0] if active_players else None
            self.end_game(winner)

    def play_again(self):
        self.game_app.controller.ui_manager.show_setup()


class GameController:
    def __init__(self, game_app):
        self.game_app = game_app
        self.ui_manager = UIManager(game_app)
        self.player_manager = PlayerManager(game_app)
        self.question_manager = QuestionManager(game_app)
        self.bot_manager = BotManager(game_app)
        self.game_flow_manager = GameFlowManager(game_app)

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


class GameApp(QtWidgets.QMainWindow):
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

        self.stats = GameStats()
        self.controller = GameController(self)

        self.start_page = StartPage(self.controller.show_setup)
        self.setup_page = GameSetupPage(self.controller.start_game, self.controller.show_start)
        self.game_page = GamePage(self.controller.submit_answer, self.controller.game_over)
        self.game_over_page = GameOverPage(self.controller.play_again, self.controller.show_start)

        for page in [self.start_page, self.setup_page, self.game_page, self.game_over_page]:
            self.stacked_widget.addWidget(page)
        self.controller.show_start()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    theme_palette = ThemePalette()
    theme_palette.apply_to(app)
    game_app = GameApp()
    game_app.show()
    sys.exit(app.exec_())   