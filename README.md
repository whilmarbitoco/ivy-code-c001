## Abstract Interfaces

### `Answerable`

This **interface** defines the `answer()` method, enabling classes like `BotPlayer` to **simulate providing an answer** to a question programmatically.

### `ProblemGenerator`

An **abstract base class** that establishes a contract for all problem generation types. It enforces the implementation of the `generate()` method, which is crucial for **creating diverse math problems**.

### `MathOperation`

This **abstract class** is designed to manage the generation of operands for mathematical problems. It mandates that its subclasses implement `get_problem()`, ensuring **specific math operations** (e.g., addition, subtraction) can be defined.

---

## Player Classes

### `Player`

The **foundational class** for all player types, `Player` encapsulates common attributes such as **name, score, response time, lives, and avatar**.

### `HumanPlayer`

A direct subclass of `Player`, `HumanPlayer` specifically represents a **player controlled by a human**.

### `BotPlayer`

Extending `Player` and implementing the `Answerable` interface, `BotPlayer` is engineered to **simulate automated question answering**, with its performance varying based on the game's difficulty.

---

## Game State Management

### `GameStats`

This class serves as the **central repository for all game-related state data**. It tracks essential information like the **current question number, game start time, active players, chosen difficulty level, and game mode**.

---

## Math Operations

### `AdditionOperation`, `SubtractionOperation`, `MultiplicationOperation`, `DivisionOperation`

These are **concrete implementations** of `MathOperation`. Each class is responsible for **generating a specific type of arithmetic problem** (e.g., "5 + 3") along with its correct numerical answer.

### `OperationFactory`

A **factory class** designed to **create instances of various math operation classes** dynamically. It allows for easy retrieval of the correct operation based on a given symbol (e.g., '+', '-', '\*', '/').

---

## Problem Generators

### `EasyProblemGenerator`, `MediumProblemGenerator`, `HardProblemGenerator`

These classes are **concrete implementations** of `ProblemGenerator`. Each is specialized in **generating math problems that progressively increase in difficulty**, offering a varied challenge to players.

### `QuestionGenerator`

Acting as a **coordinator**, `QuestionGenerator` takes a specified difficulty level (1 to 3) and then **selects and utilizes the appropriate `ProblemGenerator`** to generate the actual math questions for the game.

---

## UI Managers

### `UIManager`

This class is solely responsible for **managing the transitions between different user interface pages**. It controls which screen is displayed to the user, such as the start, game setup, active game, and game over screens.

### `TimerManager`

Dedicated to **handling all aspects of question timing**, `TimerManager` manages the start, stop, and continuous update of timers. It plays a crucial role in accurately **calculating player response times**.

### `QuestionManager`

A pivotal class that **orchestrates the entire question lifecycle**. It handles question generation, manages difficulty progression, initiates and stops the timer, and updates the UI accordingly. It also **integrates bot responses** when playing against an AI opponent.

---

## Bot Management

### `BotManager`

This class is dedicated to **managing and triggering bot answers** during gameplay. It effectively utilizes the `Answerable` interface to **simulate realistic bot input**, making the AI opponent responsive within the game.

---

## Game Logic

### `GameFlowManager`

The **strategic brain of the game**, `GameFlowManager` governs the overall game progression. Its responsibilities include **initiating the game, processing player answer submissions, evaluating win conditions, and overseeing the game's conclusion**.

---

## ✅ **SOLID Principles Applied**

### 1. **S – Single Responsibility Principle (SRP)**

Our design rigorously applies SRP, ensuring that **each class has one clear, distinct purpose**:

- `UIManager`: Exclusively manages **screen transitions**.

  ```python
  class UIManager:
      def __init__(self, game_app):
          self.game_app = game_app

      def show_start(self):
          self.game_app.stacked_widget.setCurrentWidget(self.game_app.start_page)

      def show_setup(self):
          self.game_app.stacked_widget.setCurrentWidget(self.game_app.setup_page)

      # ... other UI navigation methods
  ```

- `TimerManager`: Dedicated solely to **tracking and updating timers**.

  ```python
  class TimerManager:
      def __init__(self, game_app):
          self.game_app = game_app
          self.timer = QtCore.QTimer(self.game_app)
          self.timer.timeout.connect(self.update_timer)

      def start_timer(self):
          self.question_start_time = time.time()
          self.timer.start(100) # Start timer with 100ms interval

      def stop_timer(self):
          self.timer.stop()

      # ... other timer related methods
  ```

- `QuestionGenerator`: Its only concern is **generating math problems**.

  ```python
  class QuestionGenerator:
      def __init__(self, level):
          self.level = level
          self._problem_generator = self._GENERATORS[self.level]() # Selects specific generator

      def generate_problem(self):
          return self._problem_generator.generate()
  ```

- `BotManager`: Focuses entirely on **controlling bot answers**.

  ```python
  class BotManager:
      def __init__(self, game_app):
          self.game_app = game_app

      def bot_answer(self, bot: 'Answerable'):
          # Logic for bot to answer based on difficulty and current question
          answer = bot.answer(self.game_app.controller.question_manager.current_answer,
                              self.game_app.stats.difficulty)
          # ... update bot's input field
  ```

### 2. **O – Open/Closed Principle (OCP)**

The codebase is structured to be **open for extension but closed for modification**:

- Developers can introduce **new math operations or difficulty levels** by simply adding new subclasses, without altering existing code.
- The use of **abstract base classes** like `MathOperation` and `ProblemGenerator` facilitates easy extension through subclassing.

  **Example: Extending Math Operations**

  ```python
  # Existing MathOperation abstract class
  # class MathOperation(ABC): ...

  # Adding a new operation (e.g., ExponentiationOperation) without modifying existing MathOperation or OperationFactory
  class ExponentiationOperation(MathOperation):
      def get_problem(self):
          a = random.randint(*self.num_range_a)
          b = random.randint(1, 3) # Exponents typically small
          return f"{a} ^ {b}", a ** b

  # To use it, simply register it in the OperationFactory (extension point)
  # Inside OperationFactory:
  # _OPERATIONS = {
  #     '+': AdditionOperation,
  #     '-': SubtractionOperation,
  #     '*': MultiplicationOperation,
  #     '/': DivisionOperation,
  #     '^': ExponentiationOperation, # New entry
  # }
  ```

### 3. **L – Liskov Substitution Principle (LSP)**

LSP is honored, meaning **subclasses can seamlessly replace their base classes without causing unexpected behavior**:

- Both `HumanPlayer` and `BotPlayer` can be used interchangeably wherever a `Player` object is expected.

  ```python
  # In GameStats or elsewhere where players are stored:
  self.players = [HumanPlayer("Alice"), BotPlayer()] # Both are Player instances

  # Later, iterating through players, any Player method works for both:
  for player in self.players:
      print(f"{player.name}: Score = {player.score}, Lives = {player.lives}")
  ```

- Concrete operation classes like `AdditionOperation` and `SubtractionOperation` function perfectly when a `MathOperation` instance is required.
  ```python
  # In QuestionGenerator:
  # operation = OperationFactory.get_operation(op_symbol, (1, 20), (1, 20))
  # 'operation' here could be AdditionOperation, SubtractionOperation, etc.,
  # but all implement get_problem() as expected by the MathOperation interface.
  problem, answer = operation.get_problem()
  ```

### 4. **I – Interface Segregation Principle (ISP)**

This principle is clearly demonstrated through the **`Answerable` interface**:

- The `answer()` method is **only implemented by `BotPlayer`**, as `HumanPlayer` does not require this specific functionality.
- This ensures that classes are not forced to depend on methods they don't use.

  **Example: `Answerable` Interface**

  ```python
  from abc import ABC, abstractmethod

  class Answerable(ABC):
      @abstractmethod
      def answer(self, correct_answer, difficulty):
          pass

  class Player(ABC): # Base player class
      def __init__(self, name, is_bot=False):
          self.name = name
          self.is_bot = is_bot
          # ... other player attributes

  class HumanPlayer(Player): # Does not implement Answerable
      def __init__(self, name):
          super().__init__(name, is_bot=False)

  class BotPlayer(Player, Answerable): # Only BotPlayer implements Answerable
      def __init__(self, name="Math Bot"):
          super().__init__(name, is_bot=True)

      def answer(self, correct_answer, difficulty):
          # Bot's logic to generate an answer
          pass

  # In BotManager, it depends on the Answerable interface, not specifically BotPlayer
  class BotManager:
      def bot_answer(self, bot: Answerable): # Type hint ensures 'bot' has 'answer' method
          if bot.lives > 0:
              bot.answer(self.game_app.controller.question_manager.current_answer,
                         self.game_app.stats.difficulty)
  ```

### 5. **D – Dependency Inversion Principle (DIP)**

Our architecture ensures that **high-level modules rely on abstractions, rather than concrete implementations**:

- `QuestionManager` depends on the **abstract `ProblemGenerator`**, allowing for flexible problem creation.

  ```python
  # In QuestionManager:
  class QuestionManager:
      def __init__(self, self_obj, game_app):
          self_obj.game_app = game_app
          self_obj.current_level = 1

      def load_next_question(self):
          # Depends on the abstraction ProblemGenerator, not Easy/Medium/HardProblemGenerator directly
          generator = QuestionGenerator(self.current_level)
          self.current_problem, self.current_answer = generator.generate_problem()
  ```

- `BotManager` interacts with any object that conforms to the **`Answerable` interface**, not specifically a `BotPlayer` instance, promoting loose coupling.

  ```python
  # In BotManager:
  class BotManager:
      def __init__(self, game_app):
          self.game_app = game_app

      def bot_answer(self, bot: 'Answerable'): # Depends on Answerable (abstraction)
          if not hasattr(self.game_app.controller.question_manager, 'current_answer') or bot.lives <= 0:
              return
          # The 'answer' method is now guaranteed to exist because bot is Answerable
          answer = bot.answer(self.game_app.controller.question_manager.current_answer,
                              self.game_app.stats.difficulty)
          # ... process bot's answer
  ```
