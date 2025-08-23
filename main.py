import pgzrun, os, random, time
from pgzero.rect import Rect

os.environ['SDL_VIDEO_CENTERED'] = '1'

WIDTH, HEIGHT = 800, 600
GRAVITY, TILE_SIZE, SPAWN_OFFSET = 0.5, 64, 10
HITBOX_WIDTH, HITBOX_HEIGHT, HITBOX_OFFSET_Y = 30, 70, 20
HITBOX_WIDTH_ENEMY, HITBOX_HEIGHT_ENEMY, HITBOX_OFFSET_Y_ENEMY = 30, 70, 20
show_hitboxes = True
music_on = True

FLOORS = [
    (HEIGHT, WIDTH, 0, False),
    (HEIGHT - 1.5 * TILE_SIZE, 700, 0, False),
    (HEIGHT - 3.0 * TILE_SIZE, 700, WIDTH, True),
    (HEIGHT - 4.5 * TILE_SIZE, 700, 0, False),
    (HEIGHT - 6.0 * TILE_SIZE, 700, WIDTH, True),
    (HEIGHT - 7.5 * TILE_SIZE, 700, 0, False),
]

def get_floor_bounds(floor_y, length, start_x, invert):
    return (start_x - length, start_x) if invert else (start_x, start_x + length)

class Player:
    def __init__(self, pos):
        self.x, self.y = pos
        self.vx = self.vy = 0
        self.speed, self.jump_strength = 4, -11
        self.on_ground, self.facing_right = False, True
        self.state, self.frame = "idle", 0
        self.lives = 3
        self.dead_timer = None

        def seq(prefix, count, left=False):
            return [f"{prefix}{'_left' if left else ''}_{i}.png" for i in range(1, count + 1)]

        self.animations = {
            "idle_right": seq("idle", 4), "idle_left": seq("idle", 4, left=True),
            "run_right": seq("run", 10), "run_left": seq("run", 10, left=True),
            "jump_right": seq("jump", 3), "jump_left": seq("jump_left", 3),
            "fall_right": seq("jump_fall", 2), "fall_left": seq("jump_fall_left", 2),
            "attack_right": seq("attacknomovement", 4), "attack_left": seq("attacknomovement", 4, left=True),
            "death_right": seq("deathnomovement", 9), "death_left": seq("deathnomovement", 9, left=True),
            "hit_right": ["hit.png"], "hit_left": ["hit_left.png"],
        }

    def update(self):
        if self.state == "death":
            self.vx = self.vy = 0
            frames = self.get_current_frames()
            self.frame = len(frames) - 1
            if self.dead_timer and time.time() - self.dead_timer >= 3:
                self.respawn()
            return

        self.handle_input()
        self.apply_gravity()
        self.handle_collisions()
        self.keep_within_screen()
        self.update_state()

    def handle_input(self):
        if self.state in ["hit", "death"]:
            self.vx = 0
            return
        # Impede movimento durante ataque
        if self.state == "attack":
            self.vx = 0
        else:
            self.vx = (-self.speed if keyboard.a else self.speed if keyboard.d else 0)
            if self.vx != 0: self.facing_right = self.vx > 0
            if keyboard.w and self.on_ground: self.vy, self.on_ground = self.jump_strength, False
            if keyboard.SPACE: self.state, self.frame = "attack", 0
        self.x += self.vx

    def take_hit(self, enemy):
        if self.state not in ["hit", "death", "attack"]:
            self.state = "hit"
            self.frame = 0
            self.lives -= 1
            self.vx = -10 if self.facing_right else 10
            self.vy = -8
            if self.lives <= 0:
                self.state = "death"
                self.dead_timer = time.time()

    def respawn(self):
        global game_state
        self.lives = 3
        self.state = "idle"
        self.frame = 0
        self.x, self.y = WIDTH // 2, FLOORS[0][0] - TILE_SIZE - SPAWN_OFFSET
        game_state = "menu"
        self.dead_timer = None

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
            if self.state in ["idle", "run"]: self.frame = 0
            elif self.state in ["attack", "hit"]: self.frame, self.state = 0, "idle"

    def get_current_frames(self):
        side = 'right' if self.facing_right else 'left'
        return self.animations[f"{self.state}_{side}"]

    def draw(self):
        frames = self.get_current_frames()
        index = min(int(self.frame), len(frames) - 1)
        img = frames[index]
        offset_x = 40 if self.state == "attack" and not self.facing_right else 0
        screen.blit(img, (self.x - offset_x, self.y))
        self.draw_lives()
        if self.state == "death":
            screen.draw.text("You Died", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="red", owidth=2, ocolor="black")

    def get_hitbox(self):
        hitbox_x = self.x + (TILE_SIZE - HITBOX_WIDTH) / 2 - 20
        hitbox_y = self.y + TILE_SIZE - HITBOX_HEIGHT - HITBOX_OFFSET_Y
        width = HITBOX_WIDTH
        if self.state == "attack":
            attack_range = 40
            if self.facing_right:
                width += attack_range
            else:
                hitbox_x -= attack_range
                width += attack_range
        return Rect((hitbox_x, hitbox_y), (width, HITBOX_HEIGHT))

    def draw_hitbox(self):
        if show_hitboxes: screen.draw.rect(self.get_hitbox(), (255, 0, 0))

    def draw_lives(self):
        for i in range(self.lives):
            screen.draw.filled_circle((20 + i * 25, 20), 10, "red")

    def keep_within_screen(self):
        hitbox = self.get_hitbox()
        if hitbox.left < 0: self.x += -hitbox.left
        if hitbox.right > WIDTH: self.x += WIDTH - hitbox.right

class Enemy:
    def __init__(self, pos, x_min=200, x_max=600):
        self.x, self.y = pos
        self.vx = random.choice([-1, 1]) * random.uniform(1, 2)
        self.facing_right = self.vx > 0
        self.state, self.frame = "idle", 0
        self.lives = 2
        self.dead_timer = None
        self.x_min, self.x_max = x_min, x_max
        def seq(prefix, count, left=False): return [f"{prefix}{'_left' if left else ''}_{i}.png" for i in range(1, count + 1)]
        self.animations = {
            "idle_right": seq("idlemonster", 4), "idle_left": seq("idlemonster", 4, left=True),
            "run_right": seq("monsterrun", 8), "run_left": seq("monsterrun", 8, left=True),
            "attack_right": seq("monsterattack", 5), "attack_left": seq("monsterattack", 5, left=True),
            "death_right": seq("monsterdeath", 4), "death_left": seq("monsterdeath", 4, left=True),
            "hit_right": seq("monstertakehit", 4), "hit_left": seq("monstertakehit", 4, left=True),
        }

    def update(self):
        if self.state == "death":
            # animação de morte completa antes de sumir
            if self.frame < len(self.get_current_frames()) - 1:
                self.frame += 0.2
            else:
                if self.dead_timer is None: self.dead_timer = time.time()
                elif time.time() - self.dead_timer >= 0.1:  # tempo mínimo para sumir
                    enemies.remove(self)
            return

        self.x += self.vx
        if self.x < self.x_min or self.x > self.x_max:
            self.vx *= -1; self.facing_right = not self.facing_right
        if self.state != "hit": self.state = "run"
        self.frame += 0.2
        if self.frame >= len(self.get_current_frames()): self.frame = 0

    def take_hit(self):
        if self.state not in ["death", "hit"]:
            self.lives -= 1
            self.state = "hit"
            self.frame = 0
            if self.lives <= 0:
                self.state = "death"
                self.frame = 0
                self.dead_timer = None

    def get_current_frames(self):
        side = "right" if self.facing_right else "left"
        return self.animations[f"{self.state}_{side}"]

    def draw(self):
        frames = self.get_current_frames()
        index = min(int(self.frame), len(frames) - 1)
        screen.blit(frames[index], (self.x, self.y))

    def get_hitbox(self):
        if self.state == "death":  # hitbox desaparece ao morrer
            return Rect((0,0), (0,0))
        hitbox_x = self.x + (TILE_SIZE - HITBOX_WIDTH_ENEMY) / 2 - 20
        hitbox_y = self.y + TILE_SIZE - HITBOX_HEIGHT_ENEMY - HITBOX_OFFSET_Y_ENEMY
        return Rect((hitbox_x, hitbox_y), (HITBOX_WIDTH_ENEMY, HITBOX_HEIGHT_ENEMY))

    def draw_hitbox(self):
        if show_hitboxes and self.state != "death": screen.draw.rect(self.get_hitbox(), (0, 0, 255))

# --- Setup ---
game_state = "menu"
buttons = {
    "start": Rect((WIDTH // 2 - 100, 200), (200, 50)),
    "music": Rect((WIDTH // 2 - 100, 300), (200, 50)),
    "exit": Rect((WIDTH // 2 - 100, 400), (200, 50)),
}

if music_on: music.set_volume(0.3); music.play("background.wav")
first_floor_y, _, _, _ = FLOORS[0]
player = Player((WIDTH // 2, first_floor_y - TILE_SIZE - SPAWN_OFFSET))
enemies = [Enemy((random.randint(200, 600), y - TILE_SIZE - SPAWN_OFFSET), x_min=200, x_max=600) for y, *_ in FLOORS[1:]]

def draw_menu():
    screen.fill((50, 50, 80))
    screen.draw.text("MY PLATFORMER GAME", center=(WIDTH//2, 100), fontsize=50, color="white")
    screen.draw.filled_rect(buttons["start"], "green"); screen.draw.text("Start Game", center=buttons["start"].center, fontsize=30, color="black")
    screen.draw.filled_rect(buttons["music"], "yellow"); status = "On" if music_on else "Off"
    screen.draw.text(f"Music {status}", center=buttons["music"].center, fontsize=30, color="black")
    screen.draw.filled_rect(buttons["exit"], "red"); screen.draw.text("Exit", center=buttons["exit"].center, fontsize=30, color="black")

def on_mouse_down(pos):
    global game_state, music_on
    if game_state == "menu":
        if buttons["start"].collidepoint(pos):
            game_state = "playing"; music.set_volume(0.6) if music_on else None; music.play("background.wav") if music_on else None
        elif buttons["music"].collidepoint(pos):
            music_on = not music_on; music.set_volume(0.3 if game_state=="menu" else 0.6) if music_on else music.stop()
            music.play("background.wav") if music_on else None
        elif buttons["exit"].collidepoint(pos): exit()

def update():
    if game_state == "playing":
        player.update()
        for enemy in enemies[:]:
            enemy.update()
            if player.state == "attack" and player.get_hitbox().colliderect(enemy.get_hitbox()):
                enemy.take_hit()
            if player.state != "attack" and player.get_hitbox().colliderect(enemy.get_hitbox()):
                player.take_hit(enemy)

    if music_on and not music.is_playing("background.wav"):
        music.set_volume(0.3 if game_state=="menu" else 0.6); music.play("background.wav")

def draw():
    if game_state == "menu": draw_menu()
    elif game_state == "playing":
        screen.fill((150, 200, 255))
        for y, length, start_x, invert in FLOORS:
            floor_left, floor_right = get_floor_bounds(y, length, start_x, invert)
            for x in range(floor_left, floor_right, TILE_SIZE): screen.blit("castlehalfmid.png", (x, y - TILE_SIZE))
            if show_hitboxes: screen.draw.rect(Rect((floor_left, y - TILE_SIZE), (length, TILE_SIZE)), (0, 255, 0))
        player.draw(); player.draw_hitbox()
        for enemy in enemies: enemy.draw(); enemy.draw_hitbox()

def on_key_down(key): 
    global show_hitboxes
    if key==keys.H: show_hitboxes = not show_hitboxes

pgzrun.go()
