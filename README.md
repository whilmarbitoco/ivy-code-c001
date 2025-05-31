## Recent Updates

This update focused on making the game's code cleaner and easier to manage, especially how the different screens are handled and how new math problems are generated.

- **UI Handled by `GameApp` (Single Responsibility Principle):** The main window class was refactored and renamed to `GameApp`. It now centralizes all the UI pages (start, setup, game, game over) and controls switching between them.
- **Smarter UI Management:** The `UIManager` now tells `GameApp` which screen to show, keeping things organized.
- **Clearer Connections:** Different parts of the game now communicate better. For instance, game pages directly use specific methods from the `GameController` for actions.
- **Flexible Question Generation (Open/Closed Principle):**
  - We've introduced a **`ProblemGenerator` interface (Abstract Base Class)**.
  - Now, adding a new difficulty level (like "Very Hard") simply means creating a new problem generator class and adding it to a list. You **don't need to change existing code** in the main `QuestionGenerator` class. This makes it much easier to extend the game with new challenges without modifying core logic.
- **Preparing for Constants:** We've identified "magic numbers" (like the number of questions or player lives) that can now be turned into named constants, making them easier to find and change in the future.
