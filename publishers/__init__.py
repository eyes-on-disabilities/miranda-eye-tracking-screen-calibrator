from publishers.udp_publisher import UdpPublisher
from misc import resource_path
from guis.tkinter.main_menu_window import MainMenuOption
from publishers.mouse_publisher import MousePublisher

publishers: dict[MainMenuOption] = {
    "udp": MainMenuOption(
        key="udp",
        title="UDP-Publisher",
        description="Publish the gaze results over\nUDP in a simple JSON format.",
        icon=resource_path("assets/publisher_udp.png"),
        clazz=UdpPublisher,
    ),
    "mouse": MainMenuOption(
        key="mouse",
        title="Mouse Movement",
        description="Moves the mouse cursor according to the gaze.",
        icon=resource_path("assets/publisher_mouse.png"),
        clazz=MousePublisher,
    )
}
