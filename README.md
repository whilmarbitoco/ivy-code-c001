# Brain Buster Math Levels Adventure: SOLID Principle Implementation

**By Whilmar Bitoco**

## Single Responsibility Principle (SRP)

The **Single Responsibility Principle** states that a class should have only one reason to change. Each class in this design has a single, well-defined purpose, which significantly enhances manageability and ease of updates.

Here are the classes that primarily embody the Single Responsibility Principle:

- **`GameApp`**: Its core responsibility is managing the overall application window and the navigation between different UI pages using a `QStackedWidget`.
- **`GameStats`**: Exclusively responsible for maintaining and resetting the current game's state and statistics, such as `question_number`, `start_time`, `players`, `game_mode`, `difficulty`, and `game_active`.
- **`UIManager`**: Dedicated to handling the transitions and display of various user interface screens. It orchestrates UI changes (e.g., showing `StartPage`, `GameSetupPage`, `GamePage`, `GameOverPage`) without containing game logic.
- **`PlayerManager`**: Manages all aspects related to players, including their creation (`HumanPlayer`, `BotPlayer`), handling name input, enabling/disabling their input fields, and checking if all players have submitted answers for a round.
- **`TimerManager`**: Solely responsible for managing the question timer, encompassing starting, stopping, recording elapsed time, and updating its display on the `GamePage`.
- **`QuestionManager`**: Focuses on loading and presenting new math problems. It coordinates with the `QuestionGenerator` to obtain problems and with the `TimerManager` to control question duration. It also handles triggering bot answers.
- **`BotManager`**: Specifically manages the artificial intelligence logic for bot players, including simulating their answer generation and submitting their responses to the game.
- **`GameFlowManager`**: Orchestrates the high-level game progression. It handles game initiation (`start_game`), processing player answer submissions (`submit_answer`), updating scores and lives, checking for game-over conditions (`check_game_over`), and managing transitions to the game over screen or back to the main menu.
- **`GameController`**: Functions as a central orchestrator or "facade." It holds references to all other manager classes (`UIManager`, `PlayerManager`, `QuestionManager`, `BotManager`, `GameFlowManager`) and provides a unified interface for the GUI pages to trigger specific game logic by delegating tasks to the appropriate manager.

---

## Open/Closed Principle (OCP)

The **Open/Closed Principle** dictates that software entities should be open for extension but closed for modification. This means new functionalities can be added without altering existing, proven code. The game demonstrates this through its extensible architecture, particularly in areas where new variations or types can be introduced.

Here are the classes and hierarchies that exemplify the Open/Closed Principle:

- **`ProblemGenerator` hierarchy (`ProblemGenerator` ABC, `EasyProblemGenerator`, `MediumProblemGenerator`, `HardProblemGenerator`)**:
  - The `ProblemGenerator` Abstract Base Class (ABC) defines a standard `generate()` interface for problem creation.
  - Concrete implementations like `EasyProblemGenerator`, `MediumProblemGenerator`, and `HardProblemGenerator` extend this interface for specific problem types and difficulties.
  - **How it applies OCP**: Adding new difficulty levels (e.g., an "ExtremeProblemGenerator") requires only creating a new class inheriting from `ProblemGenerator` and registering it in `QuestionGenerator._GENERATORS`, leaving existing generator classes unchanged.
- **`MathOperation` hierarchy (`MathOperation` ABC, `AdditionOperation`, `SubtractionOperation`, `MultiplicationOperation`, `DivisionOperation`)**:
  - The `MathOperation` ABC defines the core interface for a single mathematical operation (`get_problem()`).
  - **How it applies OCP**: New operations (e.g., `ModulusOperation`, `ExponentiationOperation`) can be added by creating a new class inheriting from `MathOperation` and registering it in the `OperationFactory`. This expands mathematical capabilities without modifying existing operation logic.
- **`Player` hierarchy (`Player` ABC, `HumanPlayer`, `BotPlayer`)**:
  - The `Player` ABC defines a common interface and base behavior for different player types.
  - **How it applies OCP**: Adding new player behaviors (e.g., a "CooperativeBot" or a "TricksterBot") is achieved by creating new classes inheriting from `Player` and implementing their unique `answer()` logic, without altering `HumanPlayer` or `BotPlayer`.
- **`OperationFactory`**:
  - This static factory class provides a centralized way to create instances of `MathOperation` subclasses.
  - **How it applies OCP**: It's closed for modification in terms of its `get_operation` method's core logic, but open for extension by simply adding new entries to its internal `_OPERATIONS` dictionary when new `MathOperation` types are created.

---

## Liskov Substitution Principle (LSP)

The **Liskov Substitution Principle** states that objects of a superclass should be replaceable with objects of its subclasses without altering the correctness of the program. In essence, subtypes must be substitutable for their base types. This principle is robustly upheld throughout the game's design, particularly where polymorphism is utilized.

Here are the classes where the Liskov Substitution Principle is evident:

- **`Player` subclasses (`HumanPlayer`, `BotPlayer`)**:
  - Both `HumanPlayer` and `BotPlayer` inherit from the `Player` base class.
  - **How it applies LSP**: They can be used interchangeably wherever a `Player` object is expected (e.g., in the `GameStats.players` list, or when iterating players within `GameFlowManager` to manage input fields or update scores). The game logic interacts with the general `Player` interface (e.g., checking `player.lives`, `player.score`), making the specific subtype irrelevant for correct operation.
- **`ProblemGenerator` subclasses (`EasyProblemGenerator`, `MediumProblemGenerator`, `HardProblemGenerator`)**:
  - These classes are concrete implementations of the `ProblemGenerator` interface.
  - **How it applies LSP**: The `QuestionGenerator` uses them polymorphically. It simply calls the `generate()` method on any `ProblemGenerator` instance without needing to know the specific implementation details of how each problem is created, as all subclasses correctly fulfill the `generate()` contract.
- **`MathOperation` subclasses (`AdditionOperation`, `SubtractionOperation`, `MultiplicationOperation`, `DivisionOperation`)**:
  - These classes all inherit from `MathOperation`.
  - **How it applies LSP**: They are handled consistently by the `OperationFactory` and subsequently by the problem generators. All subclasses correctly provide the `get_problem()` method, fulfilling the exact contract defined by the `MathOperation` base class, allowing them to be substituted without issue.

---

## Dependency Inversion Principle (DIP)

The **Dependency Inversion Principle** asserts that high-level modules should not depend on low-level modules; both should depend on abstractions. Furthermore, abstractions should not depend on details; details should depend on abstractions. This principle is well-applied in the design, fostering loose coupling and flexibility.

Here are the key areas where the Dependency Inversion Principle is observed:

- **Managers and `GameController`**:
  - The `GameController` is a high-level module that coordinates the game's logic.
  - **How it applies DIP**: It depends on the abstract interfaces (public methods) provided by its manager classes (`UIManager`, `PlayerManager`, `QuestionManager`, `BotManager`, `GameFlowManager`). While concrete manager instances are created by `GameApp`, the `GameController` interacts with _what_ managers do, not _how_ they achieve it. This reduces tight coupling, enabling easier swapping of manager implementations (e.g., for testing with mock objects) without affecting the `GameController`'s core logic.
- **`QuestionGenerator` and `ProblemGenerator`**:
  - The `QuestionGenerator` (a high-level concept for managing questions) determines which type of problem to generate.
  - **How it applies DIP**: It depends on the `ProblemGenerator` abstraction, not directly on concrete implementations like `EasyProblemGenerator` or `HardProblemGenerator`. It uses a dictionary to select the appropriate `ProblemGenerator` _class_ based on the difficulty level, demonstrating its dependence on an abstraction.
- **`OperationFactory` and `MathOperation`**:
  - The `OperationFactory` is responsible for creating instances of `MathOperation` subclasses.
  - **How it applies DIP**: The problem generators that _use_ these operations depend on the `MathOperation` abstraction (for instance, by simply calling `operation.get_problem()`) rather than being tied to specific concrete operations like `AdditionOperation`. This allows for adding new mathematical operations without modifying the existing problem generation logic that consumes them.
