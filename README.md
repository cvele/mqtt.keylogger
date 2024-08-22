# MQTT Keylogger

This project is a simple Python-based keylogger that monitors specific keyboard events and publishes them to an MQTT broker. The configuration for the MQTT broker, watched keys, and other settings are loaded from a JSON configuration file.

## Features

- Monitors specific keys or key combinations on the keyboard.
- Publishes keypress events to a specified MQTT topic.
- Automatically reconnects to the MQTT broker if the connection is lost.
- Configuration is loaded from a `config.json` file, allowing easy customization.

## Requirements

- Python 3.7+
- `pynput` library for keyboard event listening
- `paho-mqtt` library for MQTT communication
- `asyncio` and `logging` modules (part of the Python standard library)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/mqtt-keylogger.git
    cd mqtt-keylogger
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `config.json` file in the project directory with the following content:
    ```json
    {
        "mqtt_broker": "mqtt_ip",
        "mqtt_port": 1883,
        "mqtt_topic": "mediacenter/keylogger",
        "mqtt_username": "your_username",
        "mqtt_password": "your_password",
        "reconnect_min_delay": 1,
        "reconnect_max_delay": 300,
        "watched_keys": [
            "Key.media_volume_mute",
            "Key.media_volume_up",
            "Key.media_volume_down",
            "Key.media_play_pause",
            "Key.media_next",
            "Key.media_previous",
            "Key.up",
            "Key.down",
            "Key.left",
            "Key.right",
            "Key.enter",
            "Key.esc",
            ["Key.alt_l", "Key.f4"]
        ]
    }
    ```

## Usage

1. Run the keylogger:
    ```bash
    python keylogger.py
    ```

2. The keylogger will start monitoring the keys specified in the `config.json` file. Any key press will be published to the MQTT topic specified.

## Configuration

- **MQTT Broker**: Update the `mqtt_broker` and `mqtt_port` fields in `config.json` to match your MQTT broker.
- **MQTT Credentials**: Set `mqtt_username` and `mqtt_password` with your MQTT broker's credentials.
- **Watched Keys**: Modify the `watched_keys` array to include the keys or key combinations you want to monitor. Use `Key.keyname` for individual keys and arrays of key names for combinations (e.g., `["Key.alt_l", "Key.f4"]`).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to submit issues or pull requests if you would like to contribute to this project.

