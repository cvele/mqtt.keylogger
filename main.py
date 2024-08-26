import asyncio
import logging
import signal
import socket
import json
from pynput import keyboard
import paho.mqtt.client as mqtt

# Global variable for the MQTT client and loop
client = None
loop = None

# Setup logging
logging.basicConfig(level=logging.INFO)

# Set to keep track of pressed keys
pressed_keys = set()

# Load configuration from file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# MQTT configurations
MQTT_BROKER = config.get('mqtt_broker')
MQTT_PORT = config.get('mqtt_port')
MQTT_TOPIC = config.get('mqtt_topic')
MQTT_USERNAME = config.get('mqtt_username')
MQTT_PASSWORD = config.get('mqtt_password')
RECONNECT_MIN_DELAY = config.get('reconnect_min_delay')
RECONNECT_MAX_DELAY = config.get('reconnect_max_delay')

# Convert watched keys from strings to actual key objects
WATCHED_KEYS = set()
for key in config.get('watched_keys', []):
    if isinstance(key, list):
        # It's a combination
        WATCHED_KEYS.add(frozenset(getattr(keyboard.Key, k) for k in key))
    else:
        if hasattr(keyboard.Key, key):
            WATCHED_KEYS.add(getattr(keyboard.Key, key))
        else:
            WATCHED_KEYS.add(keyboard.KeyCode.from_char(key))

async def mqtt_connect():
    global client
    delay = RECONNECT_MIN_DELAY
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
            logging.info("Connected to MQTT Broker")
            break
        except (socket.error, OSError) as e:
            logging.error(f"MQTT connection failed: {e}, retrying in {delay} seconds...")
            await asyncio.sleep(delay)
            delay = min(delay * 2, RECONNECT_MAX_DELAY)
        except Exception as e:
            logging.critical(f"Unexpected error: {e}")
            break

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logging.warning("Unexpected disconnection. Attempting to reconnect...")
        asyncio.run_coroutine_threadsafe(mqtt_connect(), loop)

async def publish_key(key_str):
    try:
        client.publish(MQTT_TOPIC, key_str, retain=False)
        logging.info(f"Published key: {key_str}")
    except Exception as e:
        logging.error(f"Failed to publish: {e}")

def on_press(key):
    print(f"Key pressed: {key}")
    global pressed_keys
    pressed_keys.add(key)

    if isinstance(key, keyboard.KeyCode):
        key_str = key.char
    else:
        key_str = str(key)

    if key in WATCHED_KEYS:
        asyncio.run_coroutine_threadsafe(publish_key(key_str), loop)

    # Handle key combinations
    for combo in [k for k in WATCHED_KEYS if isinstance(k, frozenset)]:
        if combo.issubset(pressed_keys):
            combo_str = "+".join([str(k) for k in combo])
            asyncio.run_coroutine_threadsafe(publish_key(combo_str), loop)

def on_release(key):
    global pressed_keys
    if key in pressed_keys:
        pressed_keys.remove(key)

def on_exit(signal_received, frame):
    logging.info("Exiting gracefully...")
    client.loop_stop()
    exit(0)

async def main():
    global client, loop
    try:
        client = mqtt.Client(client_id="", clean_session=True, protocol=mqtt.MQTTv311)
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        client.on_disconnect = on_disconnect
    except Exception as e:
        logging.critical(f"Failed to initialize MQTT client: {e}")
        exit(1)

    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    await mqtt_connect()

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
