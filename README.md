# Junker Newton

A physical adventure through space

## Dependencies

- Python 3.6
- pygame 2.0.0.dev10
- pytmx
- pyscroll
- pymunk


## Build

Using pyinstaller: `pyinstaller --onefile game.py` generates `game.exe` in a folder named `build`.
Copy the assets folder into the build folder.
Find the `chipmunk.dll` in your python folder `%python_install_path%/Lib/site_packages/pymunk/` and place it next to the exe.
Should work then :)
