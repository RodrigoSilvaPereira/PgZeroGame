import pgzrun
import os
from pgzero.rect import Rect

os.environ['SDL_VIDEO_CENTERED'] = '1'

WIDTH, HEIGHT = 800, 600
GRAVITY, TILE_SIZE, SPAWN_OFFSET = 0.5, 64, 10

FLOORS = [
    (HEIGHT, WIDTH, 0, False),
    (HEIGHT - 1.5 * TILE_SIZE, 700, 0, False),
    (HEIGHT - 3.0 * TILE_SIZE, 700, WIDTH, True),
    (HEIGHT - 4.5 * TILE_SIZE, 700, 0, False),
    (HEIGHT - 6.0 * TILE_SIZE, 700, WIDTH, True),
    (HEIGHT - 7.5 * TILE_SIZE, 700, 0, False),
]

HITBOX_WIDTH, HITBOX_HEIGHT = 30, 70
HITBOX_OFFSET_Y = 20

show_hitboxes = True

def get_floor_bounds(floor_y, length, start_x, invert):
    if invert:
        return start_x - length, start_x
    return start_x, start_x + length

# ===================== PLAYER =====================
class Player:
    def __init__(self, pos):
        self.x, self.y = pos
        self.vx = self.vy = 0
        self.speed, self.jump_strength = 4, -11
        self.on_ground, self.facing_right = False, True
        self.state, self.frame = "idle", 0

        def seq(prefix, count, left=False):
            side = "_left" if left else ""
            return [f"{prefix}{side}_{i}.png" for i in range(1, count + 1)]

        self.animations = {
            "idle_right": seq("idle", 4),
            "idle_left": seq("idle", 4, left=True),
            "run_right": seq("run", 10),
            "run_left": seq("run", 10, left=True),
            "jump_right": seq("jump", 3),
            "jump_left": seq("jump_left", 3),
            "fall_right": seq("jump_fall", 2),
            "fall_left": seq("jump_fall_left", 2),
            "attack_right": seq("attacknomovement", 4),
            "attack_left": seq("attacknomovement", 4, left=True),
            "death_right": seq("deathnomovement", 9),
            "death_left": seq("deathnomovement", 9, left=True),
            "hit_right": ["hit.png"],
            "hit_left": ["hit_left.png"],
        }

        self.action_keys = {
            "attack": keys.SPACE,
            "hit": keys.J,
            "death": keys.K
        }

    def update(self):
        self.handle_input()
        self.apply_gravity()
        self.handle_collisions()
        self.update_state()
        self.keep_within_screen()

    def handle_input(self):
        if self.state not in ["attack", "hit", "death"]:
            self.vx = 0
            if keyboard.a:
                self.vx, self.facing_right = -self.speed, False
            elif keyboard.d:
                self.vx, self.facing_right = self.speed, True

            if keyboard.w and self.on_ground:
                self.vy, self.on_ground = self.jump_strength, False

            if keyboard[self.action_keys["attack"]]:
                self.state = "attack"
                self.frame = 0
            elif keyboard[self.action_keys["hit"]]:
                self.state = "hit"
                self.frame = 0
            elif keyboard[self.action_keys["death"]]:
                self.state = "death"
                self.frame = 0
        else:
            self.vx = 0

        self.x += self.vx

    def apply_gravity(self):
        self.vy += GRAVITY
        self.prev_y, self.y = self.y, self.y + self.vy

    def handle_collisions(self):
        self.on_ground = False
        hitbox = self.get_hitbox()
        player_left, player_right = hitbox.left, hitbox.right

        for floor_y, length, start_x, invert in FLOORS:
            floor_left, floor_right = get_floor_bounds(floor_y, length, start_x, invert)
            if player_right > floor_left and player_left < floor_right:
                if self.vy > 0 and self.prev_y + HITBOX_HEIGHT <= floor_y <= self.y + HITBOX_HEIGHT:
                    self.y, self.vy, self.on_ground = floor_y - HITBOX_HEIGHT, 0, True
                elif self.vy < 0 and self.prev_y >= floor_y >= self.y:
                    self.y, self.vy = floor_y, 0

    def update_state(self):
        if self.state not in ["attack", "hit", "death"]:
            self.state = "jump" if self.vy < 0 else "fall" if not self.on_ground else "run" if self.vx else "idle"

        frames = self.get_current_frames()
        self.frame += 0.2
        if self.frame >= len(frames):
            if self.state in ["idle", "run"]:
                self.frame = 0
            elif self.state in ["attack", "hit"]:
                self.frame = 0
                self.state = "idle"
            elif self.state == "death":
                self.frame = len(frames) - 1

    def get_current_frames(self):
        side = 'right' if self.facing_right else 'left'
        return self.animations[f"{self.state}_{side}"]

    def draw(self):
        frames = self.get_current_frames()
        index = min(int(self.frame), len(frames) - 1)
        screen.blit(frames[index], (self.x, self.y))

    def get_hitbox(self):
        hitbox_x = self.x + (TILE_SIZE - HITBOX_WIDTH) / 2 - 20
        hitbox_y = self.y + TILE_SIZE - HITBOX_HEIGHT - HITBOX_OFFSET_Y
        return Rect((hitbox_x, hitbox_y), (HITBOX_WIDTH, HITBOX_HEIGHT))

    def draw_hitbox(self):
        if show_hitboxes:
            screen.draw.rect(self.get_hitbox(), (255, 0, 0))

    def keep_within_screen(self):
        hitbox = self.get_hitbox()
        if hitbox.left < 0:
            self.x += -hitbox.left
        if hitbox.right > WIDTH:
            self.x += WIDTH - hitbox.right

# ===================== ENEMY =====================
class Enemy:
    def __init__(self, pos):
        self.x, self.y = pos
        self.vx = 1
        self.facing_right = True
        self.state, self.frame = "idle", 0

        def seq(prefix, count, left=False):
            side = "_left" if left else ""
            return [f"{prefix}{side}_{i}.png" for i in range(1, count + 1)]

        self.animations = {
            "idle_right": seq("idlemonster", 4),
            "idle_left": seq("idlemonster", 4, left=True),
            "run_right": seq("monsterrun", 8),
            "run_left": seq("monsterrun", 8, left=True),
            "attack_right": seq("monsterattack", 5),
            "attack_left": seq("monsterattack", 5, left=True),
            "death_right": seq("monsterdeath", 4),
            "death_left": seq("monsterdeath", 4, left=True),
            "hit_right": seq("monstertakehit", 4),
            "hit_left": seq("monstertakehit", 4, left=True),
        }

    def update(self):
        self.x += self.vx
        if self.x < 0 or self.x > WIDTH - TILE_SIZE:
            self.vx *= -1
            self.facing_right = not self.facing_right

        self.state = "run"
        self.frame += 0.2
        if self.frame >= len(self.get_current_frames()):
            self.frame = 0

    def get_current_frames(self):
        side = "right" if self.facing_right else "left"
        return self.animations[f"{self.state}_{side}"]

    def draw(self):
        frames = self.get_current_frames()
        index = min(int(self.frame), len(frames) - 1)
        screen.blit(frames[index], (self.x, self.y))

    def get_hitbox(self):
        return Rect((self.x + 10, self.y + 10), (40, 60))

    def draw_hitbox(self):
        if show_hitboxes:
            screen.draw.rect(self.get_hitbox(), (0, 0, 255))

# ===================== Inicialização =====================
first_floor_y, _, _, _ = FLOORS[0]
player = Player((WIDTH // 2, first_floor_y - TILE_SIZE - SPAWN_OFFSET))
enemy = Enemy((WIDTH // 4, first_floor_y - TILE_SIZE - SPAWN_OFFSET))

def update():
    player.update()
    enemy.update()

def draw():
    screen.fill((150, 200, 255))
    for floor_y, length, start_x, invert in FLOORS:
        floor_left, floor_right = get_floor_bounds(floor_y, length, start_x, invert)
        for x in range(floor_left, floor_right, TILE_SIZE):
            screen.blit("castlehalfmid.png", (x, floor_y - TILE_SIZE))
        if show_hitboxes:
            screen.draw.rect(Rect((floor_left, floor_y - TILE_SIZE), (length, TILE_SIZE)), (0, 255, 0))
    player.draw()
    player.draw_hitbox()
    enemy.draw()
    enemy.draw_hitbox()

def on_key_down(key):
    global show_hitboxes
    if key == keys.H:
        show_hitboxes = not show_hitboxes

pgzrun.go()
