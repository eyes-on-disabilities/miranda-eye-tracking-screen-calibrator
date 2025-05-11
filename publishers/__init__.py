from publishers.udp_publisher import UdpPublisher
from misc import resource_path
from guis.tkinter.main_menu_window import MainMenuOption
from publishers.mouse_publisher import MousePublisher
from publishers.mouse_scroll_publisher import MouseScrollPublisher

publishers: dict[MainMenuOption] = {
    "udp": MainMenuOption(
        key="udp",
        title="UDP-Publisher",
        description="Publish the gaze results over UDP in a simple JSON format.",
        icon=resource_path("assets/publisher_udp.png"),
        clazz=UdpPublisher,
    ),
    "mouse": MainMenuOption(
        key="mouse",
        title="Mouse Movement",
        description="Moves the mouse cursor according to the gaze.\nDoesn't work with the Mouse data source.",
        icon=resource_path("assets/publisher_mouse.png"),
        clazz=MousePublisher,
    ),
    "mouse_scroll": MainMenuOption(
        key="mouse_scroll",
        title="Mouse Scroll Areas",
        description="Scrolls up and down.",
        icon=resource_path("assets/publisher_mouse.png"),
        clazz=MouseScrollPublisher,
    )
}
