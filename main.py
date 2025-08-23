import pgzrun, os, random, time
from pgzero.rect import Rect

os.environ['SDL_VIDEO_CENTERED'] = '1'

WIDTH, HEIGHT, GRAVITY, TILE_SIZE, SPAWN_OFFSET = 800, 600, 0.5, 64, 10
HITBOX_WIDTH, HITBOX_HEIGHT, HITBOX_OFFSET_Y = 30, 70, 20
HITBOX_WIDTH_ENEMY, HITBOX_HEIGHT_ENEMY, HITBOX_OFFSET_Y_ENEMY = 30, 70, 20

show_hitboxes, music_on = True, True
FLOORS = [(HEIGHT, WIDTH, 0, False),(HEIGHT-1.5*TILE_SIZE,700,0,False),(HEIGHT-3.0*TILE_SIZE,700,WIDTH,True),
          (HEIGHT-4.5*TILE_SIZE,700,0,False),(HEIGHT-6.0*TILE_SIZE,700,WIDTH,True),(HEIGHT-7.5*TILE_SIZE,700,0,False)]

def get_floor_bounds(y,l,s,invert): return (s-l,s) if invert else (s,s+l)

class Player:
    def __init__(self,pos):
        self.x,self.y = pos; self.vx=self.vy=0; self.speed,self.jump_strength=4,-11
        self.on_ground,self.facing_right=False,True; self.state,self.frame="idle",0
        self.lives, self.dead_timer=2,None
        seq=lambda p,c,l=False:[f"{p}{'_left' if l else ''}_{i}.png" for i in range(1,c+1)]
        self.animations={
            "idle_right": seq("idle",4),"idle_left":seq("idle",4,True),
            "run_right": seq("run",10),"run_left": seq("run",10,True),
            "jump_right": seq("jump",3),"jump_left":seq("jump_left",3),
            "fall_right": seq("jump_fall",2),"fall_left":seq("jump_fall_left",2),
            "attack_right": seq("attacknomovement",4),"attack_left":seq("attacknomovement",4,True),
            "death_right": seq("deathnomovement",9),"death_left":seq("deathnomovement",9,True),
            "hit_right":["hit.png"],"hit_left":["hit_left.png"]
        }

    def update(self):
        if self.state=="death":
            self.vx=self.vy=0; self.frame=len(self.get_current_frames())-1
            if self.dead_timer and time.time()-self.dead_timer>=3: reset_game(); set_game_state_menu()
            return
        self.handle_input(); self.apply_gravity(); self.handle_collisions(); self.keep_within_screen(); self.update_state()

    def handle_input(self):
        if self.state in ["hit","death"]: self.vx=0; return
        self.vx = 0 if self.state=="attack" else (-self.speed if keyboard.a else self.speed if keyboard.d else 0)
        if self.vx: self.facing_right=self.vx>0
        if keyboard.w and self.on_ground: self.vy,self.on_ground=self.jump_strength,False
        if keyboard.space:
            if game_phase=="waiting_to_start": start_game()
            else: self.state,self.frame="attack",0
        self.x+=self.vx

    def take_hit(self,_): 
        if self.state not in ["hit","death","attack"]:
            self.state="hit"; self.frame=0; self.lives-=1; self.vx=-10 if self.facing_right else 10; self.vy=-8
            if self.lives<=0: self.state="death"; self.dead_timer=time.time()

    def respawn(self):
        self.lives=3; self.state="idle"; self.frame=0
        self.x,self.y=WIDTH//2,FLOORS[0][0]-TILE_SIZE-SPAWN_OFFSET

    def apply_gravity(self): self.vy+=GRAVITY; self.prev_y,self.y=self.y,self.y+self.vy

    def handle_collisions(self):
        self.on_ground=False; hb=self.get_hitbox(); pl,pr=hb.left,hb.right
        for y,l,s,i in FLOORS:
            fl,fr=get_floor_bounds(y,l,s,i)
            if pr>fl and pl<fr:
                if self.vy>0 and self.prev_y+HITBOX_HEIGHT<=y<=self.y+HITBOX_HEIGHT: self.y,self.vy,self.on_ground=y-HITBOX_HEIGHT,0,True
                elif self.vy<0 and self.prev_y>=y>=self.y: self.y,self.vy=y,0

    def update_state(self):
        if self.state not in ["attack","hit","death"]:
            self.state="jump" if self.vy<0 else "fall" if not self.on_ground else "run" if self.vx else "idle"
        frames=self.get_current_frames(); self.frame+=0.2
        if self.frame>=len(frames):
            if self.state in ["idle","run"]: self.frame=0
            elif self.state in ["attack","hit"]: self.frame,self.state=0,"idle"

    def get_current_frames(self):
        return self.animations[f"{self.state}_{'right' if self.facing_right else 'left'}"]

    def draw(self):
        frames=self.get_current_frames(); idx=min(int(self.frame),len(frames)-1)
        offset=40 if self.state=="attack" and not self.facing_right else 0
        screen.blit(frames[idx],(self.x-offset,self.y))
        self.draw_lives()
        if self.state=="death": screen.draw.text("You Died", center=(WIDTH//2,HEIGHT//2),fontsize=60,color="red",owidth=2,ocolor="black")

    def get_hitbox(self):
        x=self.x+(TILE_SIZE-HITBOX_WIDTH)/2-20; y=self.y+TILE_SIZE-HITBOX_HEIGHT-HITBOX_OFFSET_Y; w=HITBOX_WIDTH
        if self.state=="attack": w+=40; x-=0 if self.facing_right else 40
        return Rect((x,y),(w,HITBOX_HEIGHT))

    def draw_lives(self): 
        for i in range(self.lives): screen.draw.filled_circle((20+i*25,20),10,"red")

    def keep_within_screen(self): 
        hb=self.get_hitbox(); 
        if hb.left<0: self.x+=-hb.left
        if hb.right>WIDTH: self.x+=WIDTH-hb.right

class Enemy:
    def __init__(self,pos,x_min=200,x_max=600):
        self.x,self.y=pos; self.vx=random.choice([-1,1])*random.uniform(1,2)
        self.facing_right=self.vx>0; self.state,self.frame="idle",0; self.lives=2; self.dead_timer=None
        self.x_min,self.x_max=x_min,x_max
        seq=lambda p,c,l=False:[f"{p}{'_left' if l else ''}_{i}.png" for i in range(1,c+1)]
        self.animations={
            "idle_right": seq("idlemonster",4),"idle_left":seq("idlemonster",4,True),
            "run_right": seq("monsterrun",8),"run_left":seq("monsterrun",8,True),
            "attack_right": seq("monsterattack",5),"attack_left":seq("monsterattack",5,True),
            "death_right": seq("monsterdeath",4),"death_left":seq("monsterdeath",4,True),
            "hit_right": seq("monstertakehit",4),"hit_left":seq("monstertakehit",4,True)
        }

    def update(self):
        if self.state=="death":
            if self.frame<len(self.get_current_frames())-1: self.frame+=0.2
            else:
                if self.dead_timer is None: self.dead_timer=time.time()
                elif time.time()-self.dead_timer>=0.5 and self in enemies: enemies.remove(self)
            return
        if self.state=="hit":
            if self.frame<len(self.get_current_frames())-1: self.frame+=0.2
            else: self.state="run"; self.frame=0
            return
        self.x+=self.vx
        if self.x<self.x_min or self.x>self.x_max: self.vx*=-1; self.facing_right=not self.facing_right
        self.state="run"; self.frame+=0.2; 
        if self.frame>=len(self.get_current_frames()): self.frame=0

    def take_hit(self):
        if self.state not in ["death","hit"]:
            self.lives-=1
            if self.lives<=0: self.state="death"; self.frame=0; self.dead_timer=None
            else: self.state="hit"; self.frame=0

    def get_current_frames(self):
        return self.animations[f"{self.state}_{'right' if self.facing_right else 'left'}"]

    def draw(self):
        frames=self.get_current_frames(); idx=min(int(self.frame),len(frames)-1)
        screen.blit(frames[idx],(self.x,self.y))

    def get_hitbox(self):
        if self.state=="death": return Rect((0,0),(0,0))
        x=self.x+(TILE_SIZE-HITBOX_WIDTH_ENEMY)/2-20; y=self.y+TILE_SIZE-HITBOX_HEIGHT_ENEMY-HITBOX_OFFSET_Y_ENEMY
        return Rect((x,y),(HITBOX_WIDTH_ENEMY,HITBOX_HEIGHT_ENEMY))

game_state,game_phase="menu","waiting_to_start"
buttons={"start":Rect((WIDTH//2-100,200),(200,50)),
         "music":Rect((WIDTH//2-100,300),(200,50)),
         "exit":Rect((WIDTH//2-100,400),(200,50))}

def init_player_enemies():
    global player,enemies
    fy,*_ = FLOORS[0]; player=Player((WIDTH//2,fy-TILE_SIZE-SPAWN_OFFSET))
    enemies=[Enemy((random.randint(200,600),y-TILE_SIZE-SPAWN_OFFSET)) for y,*_ in FLOORS[1:]]

def reset_game(): init_player_enemies(); global game_phase; game_phase="waiting_to_start"
def start_game(): global game_phase; game_phase="playing"
def set_game_state_menu(): global game_state; game_state="menu"
def reset_game_and_menu(): reset_game(); set_game_state_menu()

init_player_enemies()
if music_on: music.set_volume(0.3); music.play("background.wav")

def draw_menu():
    screen.fill((50,50,80))
    screen.draw.text("PLATFORMER GAME", center=(WIDTH//2,100), fontsize=50, color="white")
    screen.draw.filled_rect(buttons["start"],"green"); screen.draw.text("Start Game",center=buttons["start"].center,fontsize=30,color="black")
    screen.draw.filled_rect(buttons["music"],"yellow"); screen.draw.text(f"Music {'On' if music_on else 'Off'}",center=buttons["music"].center,fontsize=30,color="black")
    screen.draw.filled_rect(buttons["exit"],"red"); screen.draw.text("Exit",center=buttons["exit"].center,fontsize=30,color="black")

def on_mouse_down(pos):
    global game_state, music_on, game_phase
    if game_state != "menu":
        return
    if buttons["start"].collidepoint(pos):
        game_state = "playing"
        game_phase = "waiting_to_start"
        if music_on:
            music.set_volume(0.6)
            music.play("background.wav")
    elif buttons["music"].collidepoint(pos):
        music_on = not music_on
        if music_on:
            music.set_volume(0.3 if game_state == "menu" else 0.6)
            music.play("background.wav")
        else:
            music.stop()
    elif buttons["exit"].collidepoint(pos):
        exit()


def update():
    global game_phase
    if game_state!="playing": return
    if game_phase=="waiting_to_start": player.handle_input(); return
    if game_phase=="playing":
        player.update()
        for e in enemies[:]:
            e.update()
            if player.state=="attack" and player.get_hitbox().colliderect(e.get_hitbox()): e.take_hit()
            elif player.get_hitbox().colliderect(e.get_hitbox()): player.take_hit(e); e.state="hit"; e.frame=0; d=5; player.vx,direction= (-d,d) if player.x<e.x else (d,-d); player.vx,direction=player.vx,d

        if not enemies: game_phase="won"; clock.schedule_unique(reset_game_and_menu,1)
    if music_on and not music.is_playing("background.wav"): music.set_volume(0.3 if game_state=="menu" else 0.6); music.play("background.wav")

def draw():
    if game_state=="menu": draw_menu()
    else:
        screen.fill((150,200,255))
        for y,l,s,i in FLOORS:
            fl,fr=get_floor_bounds(y,l,s,i)
            for x in range(fl,fr,TILE_SIZE): screen.blit("castlehalfmid.png",(x,y-TILE_SIZE))
        player.draw()
        for e in enemies: e.draw()
        if game_phase=="waiting_to_start":
            screen.draw.text("Derrote todos os inimigos", center=(WIDTH//2,HEIGHT//2-30),fontsize=50,color="white")
            screen.draw.text("Aperte SPACE para iniciar", center=(WIDTH//2,HEIGHT//2+30),fontsize=40,color="yellow")
        elif game_phase=="won": screen.draw.text("You Win", center=(WIDTH//2,HEIGHT//2),fontsize=60,color="green")

pgzrun.go()
