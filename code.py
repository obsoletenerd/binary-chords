"""
"Binary Chords" Keyboard
An 8-key chording binary keyboard. Because why not?
Type like piano-chords to enter binary values that represent characters in the ASCII table.

For CircuitPython on a Raspberry Pi Pico 2 W
Requires Adafruit_HID: https://github.com/adafruit/Adafruit_CircuitPython_HID/
"""

import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
import time

# Configuration
CHORD_WINDOW_MS = 100  # Time window in milliseconds to collect chord presses
DEBUG = True  # Set to False to disable serial debug output

# Pin configuration (MSB to LSB, bits 7-0)
KEY_PINS = [
    board.GP16, board.GP17, board.GP18, board.GP19,  # Bits 7-4
    board.GP12, board.GP13, board.GP14, board.GP15,  # Bits 3-0
]

# Initialize keyboard and keys
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

keys = []
for pin in KEY_PINS:
    key = digitalio.DigitalInOut(pin)
    key.direction = digitalio.Direction.INPUT
    key.pull = digitalio.Pull.UP  # Pullup means pressed = False (grounded)
    keys.append(key)

# State tracking
last_key_states = [False] * 8  # False = not pressed
chord_active = False
chord_start_time = 0

def debug_print(message):
    """Print debug message if DEBUG is enabled"""
    if DEBUG:
        print(message)

def get_pressed_keys():
    """Read current state of all keys. Returns list of booleans (True = pressed)"""
    return [not key.value for key in keys]  # Invert because pullup

def keys_to_value(key_states):
    """Convert list of key states to binary value"""
    return sum(pressed << (7 - i) for i, pressed in enumerate(key_states))

def format_binary(value):
    """Format binary representation with spacing for readability"""
    binary = f"{value:08b}"
    return f"{binary[:4]} {binary[4:]}"

def get_char_description(value):
    """Get human-readable description of ASCII value"""
    special_chars = {
        8: "'\\b' (backspace)",
        9: "'\\t' (tab)",
        10: "'\\n' (newline)",
        13: "'\\r' (carriage return)",
        32: "' ' (space)",
    }

    if value in special_chars:
        return special_chars[value]
    elif 32 <= value <= 126:
        return f"'{chr(value)}'"
    else:
        return "(non-printable)"

def process_chord(value):
    """Process completed chord and send as ASCII character"""
    debug_print(">>> Chord complete! <<<")
    debug_print(f"Binary:    {format_binary(value)}")
    debug_print(f"Decimal:   {value}")
    debug_print(f"Hex:       0x{value:02X}")
    debug_print(f"Character: {get_char_description(value)}")

    # Send the character via USB HID
    try:
        layout.write(chr(value))
        debug_print(f"✓ Sent character to computer")
    except Exception as e:
        debug_print(f"✗ Error sending character: {e}")

    debug_print("---")

# Startup message
debug_print("=" * 50)
debug_print("Binary Chords Keyboard Initialized!")
debug_print("Press keys to form binary values (MSB on left)")
debug_print("Bit values: 128-64-32-16-8-4-2-1")
debug_print(f"Chord window: {CHORD_WINDOW_MS}ms")
debug_print("=" * 50)

# Main loop
while True:
    current_keys = get_pressed_keys()
    any_pressed = any(current_keys)

    # Detect newly pressed keys
    newly_pressed = [curr and not last for curr, last in zip(current_keys, last_key_states)]

    if any(newly_pressed):
        if not chord_active:
            chord_active = True
            chord_start_time = time.monotonic()
            debug_print(">>> Chord started <<<")

        # Log newly pressed keys
        for i, pressed in enumerate(newly_pressed):
            if pressed:
                bit_value = 1 << (7 - i)
                debug_print(f"Key pressed: Bit {7 - i} (value: {bit_value})")

    # Process active chord
    if chord_active:
        elapsed_ms = (time.monotonic() - chord_start_time) * 1000

        # End chord if window expired or all keys released
        if elapsed_ms >= CHORD_WINDOW_MS or not any_pressed:
            chord_value = keys_to_value(current_keys if any_pressed else last_key_states)
            if chord_value > 0:
                process_chord(chord_value)
            chord_active = False

    last_key_states = current_keys
    time.sleep(0.001)  # 1ms debounce delay
