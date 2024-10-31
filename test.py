from data_sources import data_sources
from guis.tkinter_gui import MainMenuGUI
from tracking_approaches import tracking_approaches

main_menu = MainMenuGUI()
main_menu.start()
main_menu.set_data_source_options(data_sources)
main_menu.set_tracking_approach_options(tracking_approaches)
main_menu.on_data_source_change_requested(lambda x: print(f"data source changed: {x}"))
main_menu.on_tracking_approach_change_requested(lambda x: print(f"tracking approach changed: {x}"))
main_menu.on_calibration_requested(lambda gui: print("would start calibration now", gui))

main_menu.mainloop()
