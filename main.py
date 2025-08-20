import pgzrun
from pygame import Rect

WIDTH = 800
HEIGHT = 600
GRAVITY = 0.5
GROUND_Y = HEIGHT - 100

# Class Player
class Player:
    def __init__(self, pos):
        self.x, self.y = pos
        self.vx = 0
        self.vy = 0
        self.speed = 4
        self.jump_strength = -10
        self.on_ground = True

        self.state = "idle"  # Self State to track player state
        self.frame = 0

        # Sprites right
        self.idle_right = [f"idle_{i}.png" for i in range(1, 5)]
        self.run_right = [f"run_{i}.png" for i in range(1, 11)]
        self.jump_right = [f"jump_{i}.png" for i in range(1, 4)]
        self.jump_fall_right = [f"jump_fall_{i}.png" for i in range(1, 3)]

        # Sprites left
        self.idle_left = [f"idle_left_{i}.png" for i in range(1, 5)]
        self.run_left = [f"run_left_{i}.png" for i in range(1, 11)]
        self.jump_left = [f"jump_left_{i}.png" for i in range(1, 4)]
        self.jump_fall_left = [f"jump_fall_left_{i}.png" for i in range(1, 3)]

        self.width = 50
        self.height = 50
        self.facing_right = True

    def update(self):
        self.vx = 0
        keys_pressed = keyboard

        # horizontal movement
        if keys_pressed.a:
            self.vx = -self.speed
            self.facing_right = False
        elif keys_pressed.d:
            self.vx = self.speed
            self.facing_right = True

        # Jump
        if keys_pressed.w and self.on_ground:
            self.vy = self.jump_strength
            self.on_ground = False

        # Gravity movement
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        # Ground collision
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0
            self.on_ground = True

        # State management
        if not self.on_ground:
            if self.vy < 0:
                self.state = "jump"
            else:
                self.state = "fall"
        else:
            if self.vx != 0:
                self.state = "run"
            else:
                self.state = "idle"

        # Update frame for animation
        self.frame += 0.2
        if self.state == "idle":
            frames = self.idle_right if self.facing_right else self.idle_left
            if self.frame >= len(frames):
                self.frame = 0
        elif self.state == "run":
            frames = self.run_right if self.facing_right else self.run_left
            if self.frame >= len(frames):
                self.frame = 0
        elif self.state == "jump":
            frames = self.jump_right if self.facing_right else self.jump_left
            if self.frame >= len(frames):
                self.frame = len(frames) - 1
        elif self.state == "fall":
            frames = self.jump_fall_right if self.facing_right else self.jump_fall_left
            if self.frame >= len(frames):
                self.frame = len(frames) - 1

    def draw(self):
        # Select the correct frames based on the state and facing direction
        if self.state == "idle":
            frames = self.idle_right if self.facing_right else self.idle_left
        elif self.state == "run":
            frames = self.run_right if self.facing_right else self.run_left
        elif self.state == "jump":
            frames = self.jump_right if self.facing_right else self.jump_left
        elif self.state == "fall":
            frames = self.jump_fall_right if self.facing_right else self.jump_fall_left
        else:
            frames = self.idle_right if self.facing_right else self.idle_left

        img = frames[int(self.frame)]
        screen.blit(img, (self.x, self.y))

# Innitialize player
player = Player((WIDTH//2, GROUND_Y))

# -----------------------------
# Update and Draw
# -----------------------------
def update():
    player.update()

def draw():
    screen.fill((150, 200, 255))
    # Draw ground
    screen.draw.filled_rect(Rect((0, GROUND_Y + 50), (WIDTH, HEIGHT - GROUND_Y)), (100, 200, 100))
    player.draw()

pgzrun.go()
