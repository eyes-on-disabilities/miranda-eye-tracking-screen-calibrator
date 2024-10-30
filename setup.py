from cx_Freeze import Executable, setup

build_exe_options = {
    "include_files": ["assets"],
}

setup(
    name="Miranda Eye Track",
    version="1",
    description="A middleware for easier usage of various eye and head tracking software",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base="gui",
            shortcut_name="Miranda Eye Track",
            shortcut_dir="DesktopFolder",
            icon="assets/icon.ico",
        )
    ],
)
