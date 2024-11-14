from publishers.udp_publisher import UdpPublisher
from misc import resource_path
from guis.tkinter.main_menu_window import MainMenuOption

publishers: dict[MainMenuOption] = {
    "udp": MainMenuOption(
        key="udp",
        title="UDP-Publisher",
        description="Publish the gaze results over\nUDP in a simple JSON format.",
        icon=resource_path("assets/publisher_udp.png"),
        clazz=UdpPublisher,
    )
}
