import sys
import random
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from ui_components import AnimatedButton, FadeLabel, NameInputDialog, GamePage, StartPage, GameSetupPage, GameOverPage, ThemePalette
from abc import ABC, abstractmethod


# Constant Values
QUESTION_LIMIT = 15
INITIAL_LIVES = 3

class Answerable(ABC):
    @abstractmethod
    def answer(self, correct_answer, difficulty):
        pass

class Player(ABC):
    def __init__(self, name, is_bot=False):
        self.name = name
        self.is_bot = is_bot
        self.score = 0
        self.response_time = 0
        self.correct_answers = 0
        self.lives = INITIAL_LIVES
        self.avatar = random.choice(["👦", "👧", "🧑", "👩", "🤖", "👨", "👴", "👵"])

class HumanPlayer(Player):
    def __init__(self, name):
        super().__init__(name, is_bot=False)

class BotPlayer(Player, Answerable):
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

class ProblemGenerator(ABC):
    @abstractmethod
    def generate(self):
        pass

class MathOperation(ABC):
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
    def generate(self):
        op_symbol = random.choice(['+', '-', '*', '/'])
        operation = OperationFactory.get_operation(op_symbol, (1, 20), (1, 20))
        return operation.get_problem()

class MediumProblemGenerator(ProblemGenerator):
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

class TimerManager:
    def __init__(self, game_app):
        self.game_app = game_app
        self.question_start_time = 0
        self.timer = QtCore.QTimer(self.game_app)
        self.timer_interval = 100  # Milliseconds
        self.timer.timeout.connect(self.update_timer)

    def start_timer(self):
        self.question_start_time = time.time()
        self.timer.start(self.timer_interval)

    def stop_timer(self):
        self.timer.stop()

    def update_timer(self):
        elapsed = time.time() - self.question_start_time
        self.game_app.game_page.update_timer(elapsed)

    def get_elapsed_time(self):
        return time.time() - self.question_start_time

class QuestionManager:
    def __init__(self_obj, game_app):
        self_obj.game_app = game_app
        self_obj.current_problem = ""
        self_obj.current_answer = 0
        self_obj.current_level = 1
        self_obj.timer_manager = TimerManager(game_app)

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

        # Call enable_disable_player_inputs from GameManager
        self.game_app.game_manager.enable_disable_player_inputs()

        if self.game_app.stats.game_mode == 2: # If playing against a bot
            bot = next((p for p in self.game_app.stats.players if p.is_bot), None)
            if bot and bot.lives > 0:
                # Type hint to clarify bot is Answerable
                if isinstance(bot, Answerable):
                    QtCore.QTimer.singleShot(100, lambda: self.game_app.controller.bot_manager.bot_answer(bot))

class BotManager:
    def __init__(self, game_app):
        self.game_app = game_app

    def bot_answer(self, bot: 'Answerable'): # Type hint for clarity
        if not hasattr(self.game_app.controller.question_manager, 'current_answer') or bot.lives <= 0:
            return
        # The 'answer' method is now guaranteed to exist because bot is Answerable
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
        self.game_app.game_manager.initialize_game(game_mode, num_players, difficulty)

    def submit_answer(self, player):
        if not self.game_app.stats.game_active or player.lives <= 0:
            return

        input_field = self.game_app.game_manager.get_input_field(player)
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
            player.score += max(1, int(100 * (1 - min(1, response_time / 10.0))))
        else:
            player.lives -= 1
            if player.lives <= 0:
                input_field.setEnabled(False)

        input_field.setEnabled(False)
        self.game_app.game_page.update_leaderboard(self.game_app.stats.players)
        self.game_app.game_page.update_lives_display()
        self.check_game_over()

        # Call all_answered from GameManager
        if self.game_app.game_manager.all_answered() and self.game_app.stats.game_active:
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
            self.game_app.game_page.show_game_over(winner)
            QtCore.QTimer.singleShot(3000, lambda: self.end_game(winner))

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

class GameManager:
    def __init__(self, game_app):
        self.game_app = game_app

    def initialize_game(self, game_mode, num_players, difficulty):
        player = []
        self.game_app.stats.reset()
        self.game_app.stats.game_mode = game_mode
        self.game_app.stats.difficulty = difficulty
        self.game_app.stats.game_active = True

        dialog = NameInputDialog(num_players, self.game_app)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            names = dialog.get_names() # dynamic data from dialog (ui_components.py)
            if game_mode == 1: #if multiplayer mode
                players = [HumanPlayer(name) for name in names] #instantiate all players 
            else: #if single player mode
                players = [HumanPlayer(names[0]), BotPlayer()] #instantiate player and bot
        else:
            print("Game initialization cancelled or no players selected.")
            return None

        self.game_app.stats.players = players

        if not self.game_app.stats.players:
            print("Game initialization cancelled or no players selected.")
            return None

        self.game_app.setWindowTitle(f"Brain Buster - {'Multiplayer' if game_mode == 1 else 'Single Player'} Mode")
        self.game_app.game_page.setup_player_inputs(self.game_app.stats.players)
        self.game_app.controller.ui_manager.show_game()
        self.game_app.controller.question_manager.load_next_question()

        return self.game_app

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

class Application(QtWidgets.QMainWindow): # GameApp renamed to Application
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
        self.controller = GameController(UIManager(self), QuestionManager(self), BotManager(self), GameFlowManager(self))

        self.game_manager = GameManager(self)

        self.start_page = StartPage(self.controller.show_setup)
        self.setup_page = GameSetupPage(self.controller.start_game, self.controller.show_start)
        self.game_page = GamePage(self.controller.submit_answer, self.controller.game_over)
        self.game_over_page = GameOverPage(self.controller.play_again, self.controller.show_start)

        for page in [self.start_page, self.setup_page, self.game_page, self.game_over_page]:
            self.stacked_widget.addWidget(page)
        self.controller.show_start()

class GameController:
    def __init__(self, ui_manager: UIManager, question_manager: QuestionManager, bot_manager: BotManager, game_flow_manager: GameFlowManager):
        self.ui_manager = ui_manager
        self.question_manager = question_manager
        self.bot_manager = bot_manager
        self.game_flow_manager = game_flow_manager

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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    theme_palette = ThemePalette()
    theme_palette.apply_to(app)
    game_app = Application()
    game_app.show()
    sys.exit(app.exec_())