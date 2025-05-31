import random
import time
from PyQt5 import QtCore, QtGui, QtWidgets

class AnimatedButton(QtWidgets.QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4A6FA5;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 15px 30px;
                font-size: 18px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #5D8BF4;
            }
            QPushButton:pressed {
                background-color: #3A56B0;
            }
        """)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.effect = QtWidgets.QGraphicsDropShadowEffect()
        self.effect.setBlurRadius(10)
        self.effect.setOffset(3, 3)
        self.effect.setColor(QtGui.QColor(0, 0, 0, 100))
        self.setGraphicsEffect(self.effect)


class FadeLabel(QtWidgets.QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)

    def fade_in(self, duration=500):
        self.animation = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()


class NameInputDialog(QtWidgets.QDialog):
    def __init__(self, num_players, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Player Setup")
        self.setModal(True)
        self.num_players = num_players

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1E3B70, stop:1 #2952A3);
            }
            QLabel {
                color: white;
                font-size: 18px;
            }
            QLineEdit {
                background-color: white;
                color: black;
                border: 2px solid #4A6FA5;
                border-radius: 8px;
                padding: 8px;
                font-size: 16px;
                min-width: 200px;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        title = FadeLabel("Enter Player Names")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        title.fade_in()

        self.input_widgets = []
        for i in range(num_players):
            hbox = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f"Player {i+1}:")
            line_edit = QtWidgets.QLineEdit()
            line_edit.setPlaceholderText(f"Name for Player {i+1}")
            hbox.addWidget(label)
            hbox.addWidget(line_edit)
            layout.addLayout(hbox)
            self.input_widgets.append(line_edit)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = AnimatedButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        submit_btn = AnimatedButton("Start Game")
        submit_btn.clicked.connect(self.accept)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(submit_btn)
        layout.addLayout(btn_layout)

        self.resize(400, 300)

    def get_names(self):
        names = [w.text().strip() for w in self.input_widgets]
        for i, name in enumerate(names):
            if not name:
                names[i] = f"Player {i+1}"
        return names


class GamePage(QtWidgets.QWidget):
    def __init__(self, submit_callback, game_over_callback):
        super().__init__()
        self.submit_callback = submit_callback
        self.game_over_callback = game_over_callback
        self.player_inputs = []

        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1E3B70, stop:1 #2952A3);
            }
            QFrame {
                background-color: rgba(255,255,255,0.1);
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: white;
                color: black;
                border: 2px solid #4A6FA5;
                border-radius: 8px;
                padding: 8px;
                font-size: 18px;
                min-width: 100px;
            }
            #headerLabel {
                font-size: 28px;
                font-weight: bold;
            }
            #questionLabel {
                font-size: 32px;
                font-weight: bold;
                color: #FFD700;
            }
            #timerLabel {
                font-size: 24px;
                color: #4CC9F0;
            }
            #leaderboardLabel {
                font-size: 24px;
                font-weight: bold;
            }
            #livesLabel {
                font-size: 20px;
                color: #F72585;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header_layout = QtWidgets.QHBoxLayout()

        self.back_btn = AnimatedButton("← Menu")
        self.back_btn.clicked.connect(self.show_menu)
        self.back_btn.setStyleSheet("font-size: 16px; padding: 8px 15px;")

        self.level_label = QtWidgets.QLabel("Easy Level")
        self.level_label.setObjectName("headerLabel")

        self.lives_label = QtWidgets.QLabel()
        self.lives_label.setObjectName("livesLabel")

        header_layout.addWidget(self.back_btn)
        header_layout.addStretch()
        header_layout.addWidget(self.level_label)
        header_layout.addStretch()
        header_layout.addWidget(self.lives_label)

        layout.addLayout(header_layout)

        self.question_label = QtWidgets.QLabel("Get ready for the first question!")
        self.question_label.setObjectName("questionLabel")
        self.question_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.question_label)

        self.timer_label = QtWidgets.QLabel("Time: 0.00s")
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.timer_label)

        self.player_inputs_container = QtWidgets.QWidget()
        self.player_inputs_layout = QtWidgets.QVBoxLayout()
        self.player_inputs_container.setLayout(self.player_inputs_layout)
        layout.addWidget(self.player_inputs_container)

        self.leaderboard_label = QtWidgets.QLabel("Leaderboard")
        self.leaderboard_label.setObjectName("leaderboardLabel")
        self.leaderboard_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.leaderboard_label)

        self.leaderboard = QtWidgets.QLabel()
        self.leaderboard.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.leaderboard)

        layout.addStretch()

    def show_menu(self):
        reply = QtWidgets.QMessageBox.question(
            self, 'Return to Menu',
            'Are you sure you want to return to the main menu?\nYour current progress will be lost.',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.game_over_callback(back_to_menu=True)

    def setup_player_inputs(self, players):
        # Clear existing
        for i in reversed(range(self.player_inputs_layout.count())):
            self.player_inputs_layout.itemAt(i).widget().setParent(None)

        self.player_inputs = []

        for player in players:
            player_frame = QtWidgets.QFrame()
            player_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255,255,255,0.1);
                    border-radius: 10px;
                }
            """)

            frame_layout = QtWidgets.QHBoxLayout()
            player_frame.setLayout(frame_layout)

            info_layout = QtWidgets.QVBoxLayout()
            name_label = QtWidgets.QLabel(f"{player.avatar} {player.name}")
            name_label.setStyleSheet("font-weight: bold; font-size: 20px;")

            lives_display = QtWidgets.QLabel(f"Lives: {'❤' * player.lives}")
            lives_display.setObjectName("livesLabel")

            info_layout.addWidget(name_label)
            info_layout.addWidget(lives_display)
            frame_layout.addLayout(info_layout)

            answer_edit = QtWidgets.QLineEdit()
            answer_edit.setPlaceholderText("Your answer...")
            answer_edit.setStyleSheet("color: black;")

            # We connect the returnPressed signal to the submit callback
            answer_edit.returnPressed.connect(lambda _, p=player: self.submit_callback(p))

            submit_btn = AnimatedButton("Submit")
            submit_btn.clicked.connect(lambda _, p=player: self.submit_callback(p))
            submit_btn.setStyleSheet("font-size: 16px; padding: 8px 15px;")

            frame_layout.addWidget(answer_edit)
            frame_layout.addWidget(submit_btn)

            self.player_inputs.append((player, answer_edit, lives_display))
            self.player_inputs_layout.addWidget(player_frame)

    def update_leaderboard(self, players):
        sorted_players = sorted(players, key=lambda p: (-p.score, p.response_time))

        leaderboard_text = """
        <table border='0' cellspacing='10' style='margin: 0 auto; color: white;'>
            <tr>
                <th style='padding: 5px 15px; text-align: left;'>Rank</th>
                <th style='padding: 5px 15px; text-align: left;'>Player</th>
                <th style='padding: 5px 15px; text-align: center;'>Score</th>
                <th style='padding: 5px 15px; text-align: center;'>Time</th>
                <th style='padding: 5px 15px; text-align: center;'>Correct</th>
                <th style='padding: 5px 15px; text-align: center;'>Lives</th>
            </tr>
        """

        for i, player in enumerate(sorted_players):
            leaderboard_text += f"""
            <tr>
                <td style='padding: 5px 15px;'>{i+1}</td>
                <td style='padding: 5px 15px;'>{player.avatar} {player.name}</td>
                <td style='padding: 5px 15px; text-align: center;'>{player.score}</td>
                <td style='padding: 5px 15px; text-align: center;'>{player.response_time:.2f}s</td>
                <td style='padding: 5px 15px; text-align: center;'>{player.correct_answers}</td>
                <td style='padding: 5px 15px; text-align: center; color: #F72585;'>{'❤' * player.lives}</td>
            </tr>
            """

        leaderboard_text += "</table>"
        self.leaderboard.setText(leaderboard_text)

    def update_timer(self, elapsed):
        self.timer_label.setText(f"⏱️ Time: {elapsed:.2f}s")

    def update_lives_display(self):
        for player, _, lives_display in self.player_inputs:
            lives_display.setText(f"Lives: {'❤' * player.lives}")

    def show_game_over(self, winner=None):
        if winner:
            self.question_label.setText(f"🏆 {winner.name} wins with {winner.score} points!")
        else:
            self.question_label.setText("Game Over!")

        for _, input_field, _ in self.player_inputs:
            input_field.setEnabled(False)


class StartPage(QtWidgets.QWidget):
    def __init__(self, start_callback):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1E3B70, stop:1 #2952A3);
            }
            QLabel {
                color: white;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QtWidgets.QWidget()
        header.setStyleSheet("background-color: rgba(0,0,0,0.2);")
        header_layout = QtWidgets.QVBoxLayout(header)
        header_layout.setContentsMargins(0, 40, 0, 40)

        self.title = FadeLabel("Brain Buster Math")
        self.title.setStyleSheet("font-size: 72px; font-weight: bold; color: #FFD700;")
        self.title.setAlignment(QtCore.Qt.AlignCenter)

        self.subtitle = FadeLabel(" Levels Adventure")
        self.subtitle.setStyleSheet("font-size: 36px; color: #4CC9F0;")
        self.subtitle.setAlignment(QtCore.Qt.AlignCenter)

        header_layout.addWidget(self.title)
        header_layout.addWidget(self.subtitle)
        layout.addWidget(header)

        center = QtWidgets.QWidget()
        center_layout = QtWidgets.QVBoxLayout(center)
        center_layout.setContentsMargins(50, 30, 50, 30)
        center_layout.setSpacing(30)

        features = [
            "🎯 15 challenging math questions",
            "⚡ Simultaneous answering",
            "👥 Play with friends or against AI",
            "💖 3 lives per player",
            "🏆 Leaderboard tracks scores"
        ]

        for feature in features:
            label = QtWidgets.QLabel(feature)
            label.setStyleSheet("font-size: 24px;")
            center_layout.addWidget(label)

        center_layout.addStretch()

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()

        self.start_btn = AnimatedButton("Start Game")
        self.start_btn.clicked.connect(start_callback)
        self.start_btn.setStyleSheet("font-size: 24px; padding: 15px 30px;")

        quit_btn = AnimatedButton("Quit")
        quit_btn.clicked.connect(QtWidgets.QApplication.quit)
        quit_btn.setStyleSheet("font-size: 24px; padding: 15px 30px;")

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(quit_btn)
        btn_layout.addStretch()

        center_layout.addLayout(btn_layout)
        layout.addWidget(center)

        footer = QtWidgets.QLabel("© 2023 Math Challenge Game")
        footer.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.7);")
        footer.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(footer)

        self.title.fade_in(1000)
        self.subtitle.fade_in(1500)


class GameOverPage(QtWidgets.QWidget):
    def __init__(self, play_again_callback, menu_callback):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1E3B70, stop:1 #2952A3);
            }
            QLabel {
                color: white;
            }
            #winnerLabel {
                font-size: 32px;
                font-weight: bold;
                color: #4CC9F0;
            }
            #loserLabel {
                font-size: 24px;
                color: #F72585;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)

        self.title_label = QtWidgets.QLabel("Game Over")
        self.title_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #FFD700;")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.winner_label = QtWidgets.QLabel()
        self.winner_label.setObjectName("winnerLabel")
        self.winner_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.winner_label)

        self.loser_label = QtWidgets.QLabel()
        self.loser_label.setObjectName("loserLabel")
        self.loser_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.loser_label)

        self.trophy_icon = QtWidgets.QLabel()
        self.trophy_icon.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.trophy_icon)

        self.leaderboard = QtWidgets.QLabel()
        self.leaderboard.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.leaderboard)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()

        menu_btn = AnimatedButton("Main Menu")
        menu_btn.clicked.connect(menu_callback)

        play_again_btn = AnimatedButton("Play Again")
        play_again_btn.clicked.connect(play_again_callback)

        btn_layout.addWidget(menu_btn)
        btn_layout.addWidget(play_again_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        layout.addStretch()

    def set_results(self, players, winner=None):
        sorted_players = sorted(players, key=lambda p: (-p.score, p.response_time))

        if winner:
            # If we had only 2 players and one is a bot, handle special text
            if len(players) == 2 and any(p.is_bot for p in players):
                human = next(p for p in players if not p.is_bot)
                bot = next(p for p in players if p.is_bot)

                if winner == human:
                    self.winner_label.setText(f"🎉 You win! {bot.name} loses 🎉")
                    self.loser_label.setText("Congratulations!")
                    self.trophy_icon.setText("🏆")
                else:
                    self.winner_label.setText(f"😢 You lose! {bot.name} wins 😢")
                    self.loser_label.setText("Better luck next time!")
                    self.trophy_icon.setText("💔")
            else:
                self.winner_label.setText(f"🏆 {winner.name} wins! 🏆")
                losers = [p for p in players if p != winner]
                if losers:
                    loser_names = ", ".join(p.name for p in losers)
                    self.loser_label.setText(f"Better luck next time {loser_names}!")
                self.trophy_icon.setText("🏆🏆🏆")
        else:
            self.winner_label.setText("Game Over!")
            self.loser_label.setText("All players have been eliminated!")
            self.trophy_icon.setText("😢")

        leaderboard_text = """
        <table border='0' cellspacing='10' style='margin: 0 auto; color: white;'>
            <tr>
                <th style='padding: 5px 15px; text-align: left;'>Rank</th>
                <th style='padding: 5px 15px; text-align: left;'>Player</th>
                <th style='padding: 5px 15px; text-align: center;'>Score</th>
                <th style='padding: 5px 15px; text-align: center;'>Correct</th>
            </tr>
        """

        for i, player in enumerate(sorted_players):
            leaderboard_text += f"""
            <tr>
                <td style='padding: 5px 15px;'>{i+1}</td>
                <td style='padding: 5px 15px;'>{player.avatar} {player.name}</td>
                <td style='padding: 5px 15px; text-align: center;'>{player.score}</td>
                <td style='padding: 5px 15px; text-align: center;'>{player.correct_answers}</td>
            </tr>
            """

        leaderboard_text += "</table>"
        self.leaderboard.setText(leaderboard_text)


class GameSetupPage(QtWidgets.QWidget):
    def __init__(self, start_callback, back_callback):
        super().__init__()
        self.start_callback = start_callback
        self.back_callback = back_callback

        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1E3B70, stop:1 #2952A3);
            }
            QGroupBox {
                background-color: rgba(255,255,255,0.15);
                border: 2px solid #4A6FA5;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QRadioButton {
                color: white;
                font-size: 16px;
                padding: 8px;
            }
            QLabel {
                color: white;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        title = FadeLabel("Game Settings")
        title.setStyleSheet("font-size: 36px; font-weight: bold;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        title.fade_in()

        mode_group = QtWidgets.QGroupBox("Game Mode")
        mode_layout = QtWidgets.QVBoxLayout()

        self.mode_multiplayer = QtWidgets.QRadioButton("🎮 Multiplayer (1-5 players)")
        self.mode_vs_bot = QtWidgets.QRadioButton("🤖 Play against a bot")
        self.mode_multiplayer.setChecked(True)

        for rb in [self.mode_multiplayer, self.mode_vs_bot]:
            rb.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            mode_layout.addWidget(rb)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        self.player_count_group = QtWidgets.QGroupBox("Number of Players")
        player_count_layout = QtWidgets.QHBoxLayout()

        self.player_count_btns = []
        for i in range(5):
            btn = QtWidgets.QRadioButton(str(i+1))
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            if i == 0:
                btn.setChecked(True)
            player_count_layout.addWidget(btn)
            self.player_count_btns.append(btn)

        self.player_count_group.setLayout(player_count_layout)
        layout.addWidget(self.player_count_group)

        self.bot_difficulty_group = QtWidgets.QGroupBox("Bot Difficulty")
        self.bot_difficulty_group.setVisible(False)
        bot_diff_layout = QtWidgets.QHBoxLayout()

        self.bot_diff_btns = []
        for i, diff in enumerate(["😊 Easy", "😐 Medium", "😠 Hard"]):
            btn = QtWidgets.QRadioButton(diff)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            if i == 1:
                btn.setChecked(True)
            bot_diff_layout.addWidget(btn)
            self.bot_diff_btns.append(btn)

        self.bot_difficulty_group.setLayout(bot_diff_layout)
        layout.addWidget(self.bot_difficulty_group)

        self.mode_multiplayer.toggled.connect(self.update_mode_display)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        back_btn = AnimatedButton("Back")
        back_btn.clicked.connect(self.back_callback)
        start_btn = AnimatedButton("Start Game")
        start_btn.clicked.connect(self.start_game)
        btn_layout.addWidget(back_btn)
        btn_layout.addWidget(start_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch()

    def update_mode_display(self, is_multiplayer):
        self.player_count_group.setVisible(is_multiplayer)
        self.bot_difficulty_group.setVisible(not is_multiplayer)

    def start_game(self):
        if self.mode_multiplayer.isChecked():
            game_mode = 1
            num_players = [i+1 for i, btn in enumerate(self.player_count_btns) if btn.isChecked()][0]
            difficulty = 1
        else:
            game_mode = 2
            num_players = 1
            difficulty = [i+1 for i, btn in enumerate(self.bot_diff_btns) if btn.isChecked()][0]

        self.start_callback(game_mode, num_players, difficulty)


class ThemePalette:
    """Class to set a dark theme palette for a QApplication."""
    def __init__(self):
        self.palette = QtGui.QPalette()
        self._setup_palette()

    def _setup_palette(self):
        """Configures the dark theme palette."""
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        self.palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        self.palette.setColor(QtGui.QPalette.Base, QtGui.QColor(35, 35, 35))
        self.palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        self.palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        self.palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        self.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        self.palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        self.palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        self.palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        self.palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(142, 45, 197).lighter())
        self.palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)

    def apply_to(self, app):
        """Applies the palette to the given QApplication."""
        app.setPalette(self.palette)
