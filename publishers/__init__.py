from publishers.udp_publisher import UdpPublisher

publishers = {
    "udp": {
        "key": "udp",
        "title": "UDP-Publisher",
        "description": "Publish the gaze results over\nUDP in a simple JSON format.",
        "icon": "assets/publisher_udp.png",
        "class": UdpPublisher,
    },
}
