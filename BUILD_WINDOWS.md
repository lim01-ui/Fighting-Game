# Building for Windows

The Windows build must be created on Windows. From the project folder:

1. Install 64-bit Python 3.12 and enable the Python Launcher (`py`).
2. Run `build_windows.bat`.
3. Launch `dist\FightingGame\FightingGame.exe`.

This creates an onedir build so the bundled PyAV/FFmpeg libraries and game
assets remain available beside the executable. Share the complete
`dist\FightingGame` folder; do not copy the `.exe` by itself.

The build includes the title video, music, sound effects, sprite sheets, and
portraits from `assets/`. Player preferences continue to be stored in the
user's home directory, separate from the installed game.

To diagnose a startup failure, temporarily change `console=False` to
`console=True` in `FightingGame.spec`, then run:

```bat
.venv-build\Scripts\python.exe -m PyInstaller --clean --noconfirm FightingGame.spec
```

Restore `console=False` before creating the normal windowed game build.
