# Racing Game (Python + Pygame)

A lightweight, self-contained 2D racing game implemented in Python using Pygame. The game renders a simple road, a player car, obstacles, and rival cars. It uses images from a local `cars/` directory when available. The player can customize the car visuals by placing images named according to a simple naming convention.

Key ideas:
- Player car can be replaced by an image named `pitstop_car_1.*` (in the `cars/` folder).
- Rival cars are loaded from `pitstop_car_2.*`, `pitstop_car_3.*`, etc., and appear on the track.
- Controls: left/right to steer within the road; avoid obstacles and rival cars.
- Restart with the R key after a game over, quit with Q.

This project is designed as a minimal, dependency-light playground for learning Pygame-based game logic.


## Prerequisites
- Python 3.8 or newer
- Pygame (install via `pip install pygame`)


## How to Run
1) Install dependencies
   - `pip install pygame`
2) Run the game
   - `python racing_game.py`

Optional debugging/configuration:
- Debug mode: set environment variable `RACING_DEBUG=1` to emit per-frame logs to console and `racing_debug.log`.
- Safe mode (no images): set `RACING_SAFE=1` to run with simple geometric shapes instead of images. Useful if image assets are missing.
- On Linux/macOS, set with export; on Windows use `set` in CMD or `$Env:` in PowerShell.


## Controls
- Left/Right arrows: move the car left and right within the road boundaries
- R: restart the game when you are in the game-over state
- Q: quit the game


## File structure
- racing_game.py: Main game implementation
- cars/: Directory for car images
  - pitstop_car_1.*: Player car image (used if present)
  - pitstop_car_2.*, pitstop_car_3.*, ...: Rival cars images


## Customization
- You can adjust gameplay parameters (road width, car size, speeds, spawn rates) by editing constants in racing_game.py. This is intentionally minimal to keep the example approachable.
- If you’d like to add more cars or different behaviors, you can extend the `load_player_car_image` and `load_racer_images` helpers.


## Known issues / Troubleshooting
- If you see a white/garbled Chinese font, ensure a Chinese font is available on your system or run in DEBUG mode to inspect font loading behavior.
- In headless environments, the code attempts to fall back to a dummy video driver when possible.


## Contributing
- This is a small educational example. If you want to contribute, consider adding more assets, polishing the visuals, or extending the game logic (e.g., different levels, scoring, or AI).


## License
See LICENSE file for details.
