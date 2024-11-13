from cx_Freeze import Executable, setup
import config

build_exe_options = {
    "include_files": ["assets"],
}

setup(
    name=config.APP_FULL_NAME,
    version="1",
    description=config.APP_DESCRIPTION,
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base="gui",
            shortcut_name=config.APP_SHORT_NAME,
            shortcut_dir="DesktopFolder",
            icon=config.APP_ICON_WINDOWS,
        )
    ],
)
