"""
"Binary Chords - The Game" by ObsoleteNerd

A small game for practicing using my Binary Chords keyboard.
Use your normal keyboard to practice the finger positions so you're ready for the Binary Chords keyboard.
"""

import pygame
import random
import time
import sys

# Initialize Pygame
pygame.init()

# Game configuration
WIDTH = 800
HEIGHT = 600
COLUMNS = 8
COLUMN_WIDTH = WIDTH // COLUMNS
FALL_SPEED = 50  # pixels per second
SPAWN_RATE = 5.0  # seconds between spawns
TARGET_Y = HEIGHT - 100  # Where player needs to input the character
HIT_ZONE = 30  # Tolerance for hitting the target

# Colours
BLACK = (20, 20, 40)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 100, 100)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (150, 150, 150)
LIGHT_GREEN = (200, 255, 200)

# Game state
score = 0
game_time = 0
last_spawn = 0
falling_chars = []
current_binary_input = [False] * 8  # Current binary chord being held
zone_is_red = False
zone_red_start_time = 0

# ASCII characters used in the game (A-Z, a-z, 0-9)
CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

# Key mappings (1-8 keys to bits 7-0)
KEY_MAP = {
    pygame.K_a: 0, pygame.K_s: 1, pygame.K_d: 2, pygame.K_f: 3,
    pygame.K_h: 4, pygame.K_j: 5, pygame.K_k: 6, pygame.K_l: 7
}

class FallingChar:
    def __init__(self, char, y_pos):
        self.char = char
        self.ascii_value = ord(char)
        self.binary = format(self.ascii_value, '08b')  # 8-bit binary string
        self.y = y_pos
        self.hit = False
        self.missed = False

    def update(self, dt):
        self.y += FALL_SPEED * dt

        # Check if it's in the hit zone
        if abs(self.y - TARGET_Y) <= HIT_ZONE:
            return True  # In hit zone

        # Check if it's missed (past the target)
        if self.y > TARGET_Y + HIT_ZONE:
            self.missed = True
            return False

        return False

def draw_falling_char(screen, font_large, font_medium, char_obj):
    # Draw the character letter above the binary representation
    char_x = WIDTH // 2
    char_surface = font_large.render(char_obj.char, True, YELLOW)
    char_rect = char_surface.get_rect(center=(char_x, char_obj.y - 40))
    screen.blit(char_surface, char_rect)

    # Draw binary representation across columns
    for i, bit in enumerate(char_obj.binary):
        x = i * COLUMN_WIDTH + COLUMN_WIDTH // 2
        if bit == '1':
            # Draw filled circle for 1
            pygame.draw.circle(screen, RED, (x, int(char_obj.y)), 15)
        else:
            # Draw empty circle for 0
            pygame.draw.circle(screen, BLUE, (x, int(char_obj.y)), 15, 2)

def draw_current_input(screen, font_small):
    # Draw current binary input state at bottom
    input_y = HEIGHT - 60

    for i in range(COLUMNS):
        x = i * COLUMN_WIDTH + COLUMN_WIDTH // 2
        if current_binary_input[i]:
            # Key is pressed - show filled
            pygame.draw.circle(screen, GREEN, (x, input_y), 20)
        else:
            # Key not pressed - show empty
            pygame.draw.circle(screen, GRAY, (x, input_y), 20, 2)

def spawn_character():
    # Pick random character
    char = random.choice(CHARS)
    # Spawn at top of screen
    falling_chars.append(FallingChar(char, -50))

def check_input_match(char_obj):
    # Convert current binary input to ASCII value
    input_value = 0
    for i, pressed in enumerate(current_binary_input):
        if pressed:
            input_value += 2**(7-i)  # MSB to LSB

    return input_value == char_obj.ascii_value

def main():
    global score, game_time, last_spawn, falling_chars, current_binary_input, zone_is_red, zone_red_start_time

    # Create display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Binary Chords Typing Tutor")

    # Create fonts
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)

    # Game clock
    clock = pygame.time.Clock()

    # Spawn first character
    spawn_character()

    # Main game loop
    running = True
    last_time = time.time()

    while running:
        # Calculate delta time
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        game_time += dt

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in KEY_MAP:
                    current_binary_input[KEY_MAP[event.key]] = True
            elif event.type == pygame.KEYUP:
                if event.key in KEY_MAP:
                    current_binary_input[KEY_MAP[event.key]] = False
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # Update game logic

        # Update zone color (reset red to green after 0.5 seconds)
        if zone_is_red and game_time - zone_red_start_time > 0.5:
            zone_is_red = False

        # Spawn new characters
        if game_time - last_spawn > SPAWN_RATE:
            spawn_character()
            last_spawn = game_time

        # Update falling characters
        chars_to_remove = []
        for char_obj in falling_chars:
            in_hit_zone = char_obj.update(dt)

            if in_hit_zone and not char_obj.hit:
                # Check if current input matches the character
                if check_input_match(char_obj):
                    char_obj.hit = True
                    score += 100
                    chars_to_remove.append(char_obj)

            # Check if character was missed (past the zone without being hit)
            if char_obj.missed and not char_obj.hit:
                zone_is_red = True
                zone_red_start_time = game_time

            # Remove missed or hit characters
            if char_obj.missed or char_obj.hit or char_obj.y > HEIGHT + 50:
                chars_to_remove.append(char_obj)

        # Remove processed characters
        for char_obj in chars_to_remove:
            if char_obj in falling_chars:
                falling_chars.remove(char_obj)

        # Draw everything
        screen.fill(BLACK)

        # Draw column separators
        for i in range(1, COLUMNS):
            x = i * COLUMN_WIDTH
            pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))

        # Draw bit labels at top
        for i in range(COLUMNS):
            bit_value = 2**(7-i)  # MSB to LSB
            x = i * COLUMN_WIDTH + COLUMN_WIDTH // 2
            bit_surface = font_small.render(str(bit_value), True, LIGHT_GRAY)
            bit_rect = bit_surface.get_rect(center=(x, 30))
            screen.blit(bit_surface, bit_rect)

        # Draw target zone as semi-transparent rectangle (green or red)
        target_start = TARGET_Y - HIT_ZONE
        target_end = TARGET_Y + HIT_ZONE
        zone_height = target_end - target_start

        # Create a surface for the semi-transparent rectangle
        zone_surface = pygame.Surface((WIDTH, zone_height))
        zone_surface.set_alpha(128)  # 50% opacity (128 out of 255)

        # Choose color based on zone state
        zone_color = RED if zone_is_red else GREEN
        zone_surface.fill(zone_color)
        screen.blit(zone_surface, (0, target_start))

        # Draw falling characters
        for char_obj in falling_chars:
            draw_falling_char(screen, font_large, font_medium, char_obj)

        # Draw current binary input state at bottom
        draw_current_input(screen, font_small)

        # Draw UI
        score_surface = font_medium.render(f"Score: {score}", True, WHITE)
        screen.blit(score_surface, (10, 10))

        instruction_surface = font_small.render(
            "Hold the correct binary combination when character enters green zone!",
            True, LIGHT_GRAY
        )
        instruction_rect = instruction_surface.get_rect(center=(WIDTH//2, HEIGHT - 30))
        screen.blit(instruction_surface, instruction_rect)

        # Draw key mapping help
        help_y = 60
        help_surface = font_small.render("Keys: A=128, S=64, D=32, F=16, H=8, J=4, K=2, L=1", True, LIGHT_GRAY)
        help_rect = help_surface.get_rect(center=(WIDTH//2, help_y))
        screen.blit(help_surface, help_rect)

        # Update display
        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
