import pgzrun
import math
import random
from pygame import Rect 

# Tela
WIDTH = 800
HEIGHT = 600
TITLE = "Knights and Monsters"

# Cores
COLOR_BACKGROUND_MENU = (176, 196, 222) # Azul acinzentado
COLOR_BACKGROUND_PLAY = (135, 206, 235) # Azul
COLOR_PLATFORM = (100, 60, 30) # Marrom
COLOR_TEXT = (255, 255, 255) # Branco
COLOR_BUTTON = (0, 150, 0) # Verde 
COLOR_BUTTON_TEXT = (255, 255, 255) # Branco
COLOR_BUTTON_EXIT = (200, 0, 0) # Vermelho 
COLOR_HUD_TEXT = (10, 10, 10) # Preto
COLOR_VICTORY_BG = (30, 180, 30) # Verde 
COLOR_VICTORY_TEXT = (255, 255, 0) # Amarelo 
COLOR_CONTROLS_BG = (119, 136, 153) # Cinza

# Paginas do jogo
GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_GAME_OVER = "game_over"
GAME_STATE_VICTORY = "victory"
GAME_STATE_CONTROLS = "controls" 
game_state = GAME_STATE_MENU

# Configurações de música e som
music_on = True
sounds_on = True

# --- Assets ---
# Sons
SOUND_JUMP_FILENAME = "jump" 
SOUND_HURT_FILENAME = "hurt"
SOUND_CLICK_FILENAME = "click"
SOUND_ENEMY_DEFEAT_FILENAME = "enemy_defeat"
MUSIC_BACKGROUND = "music_theme.ogg" 
MUSIC_MENU = "music_menu.ogg" 
MUSIC_VICTORY_FILENAME = "music_victory.ogg" 

# Player
PLAYER_IDLE_R_FRAMES = ["player_idle_r_0", "player_idle_r_1", "player_idle_r_2"]
PLAYER_IDLE_L_FRAMES = ["player_idle_l_0", "player_idle_l_1", "player_idle_l_2"]
PLAYER_RUN_R_FRAMES = ["player_run_r_0", "player_run_r_1", "player_run_r_2", "player_run_r_3"]
PLAYER_RUN_L_FRAMES = ["player_run_l_0", "player_run_l_1", "player_run_l_2", "player_run_l_3"]
PLAYER_JUMP_R_FRAME = "player_jump_r"
PLAYER_JUMP_L_FRAME = "player_jump_l"
PLAYER_HURT_R_FRAME = "player_hurt_r" 
PLAYER_HURT_L_FRAME = "player_hurt_l" 

# Slime
ENEMY_IDLE_R_FRAMES = ["slime_idle_r_0", "slime_idle_r_1"]
ENEMY_IDLE_L_FRAMES = ["slime_idle_l_0", "slime_idle_l_1"]
ENEMY_WALK_R_FRAMES = ["slime_walk_r_0", "slime_walk_r_1", "slime_walk_r_2"]
ENEMY_WALK_L_FRAMES = ["slime_walk_l_0", "slime_walk_l_1", "slime_walk_l_2"]

# Outras Imagens
PLATFORM_IMAGE = "platform_block" 
BACKGROUND_IMAGE_PLAY = "background_sky" 

# Constantes 
GRAVITY = 0.7
PLAYER_SPEED = 3.5
PLAYER_JUMP_STRENGTH = -14 
PLAYER_MAX_HEALTH = 3
ENEMY_PATROL_SPEED = 1.0
ANIMATION_FRAME_DURATION = 0.1 #
PLAYER_IDLE_ANIMATION_FRAME_DURATION = 0.1
ENEMY_HALF_HEIGHT = 7 
PLAYER_HURT_FRAME_DURATION = 0.3 

# --- Classes ---

class AnimatedActor:
    """Classe para personagens com animação de sprite."""
    def __init__(self, initial_image_name, pos, animation_sets):
        self.actor = Actor(initial_image_name, pos)
        self.animations = animation_sets
        self.current_action = None
        self.current_frame_index = 0
        self.animation_timer = 0
        self.facing_direction = 1 
        self.is_animating = True 

    def set_action(self, action_name):
        action_key_with_direction = f"{action_name}_{'r' if self.facing_direction == 1 else 'l'}"

        if action_key_with_direction not in self.animations and action_name in self.animations:
            action_to_set = action_name 
        elif action_key_with_direction in self.animations:
            action_to_set = action_key_with_direction
        else: 
            default_action_key = "idle_r" 
            if default_action_key not in self.animations and self.animations: 
                default_action_key = list(self.animations.keys())[0]
            elif not self.animations: 
                print(f"Nenhuma animação definida para {self.__class__.__name__}. Ação '{action_key_with_direction}' ou '{action_name}' não encontrada.")
                if self.animations and list(self.animations.values()) and list(self.animations.values())[0]:
                     self.actor.image = list(self.animations.values())[0][0]
                return

            print(f"Ação '{action_key_with_direction}' ou '{action_name}' não encontrada. Usando '{default_action_key}'.")
            action_to_set = default_action_key


        if self.current_action != action_to_set:
            self.current_action = action_to_set
            self.current_frame_index = 0
            self.animation_timer = 0
            if self.current_action in self.animations and self.animations[self.current_action]: 
                 self.actor.image = self.animations[self.current_action][0]

    def update_animation(self, dt, specific_frame_duration=None): 
        if not self.is_animating or not self.current_action or \
           self.current_action not in self.animations or not self.animations[self.current_action]:
            return

        duration_to_use = specific_frame_duration if specific_frame_duration is not None else ANIMATION_FRAME_DURATION

        self.animation_timer += dt
        if self.animation_timer >= duration_to_use:
            self.animation_timer -= duration_to_use 
            num_frames = len(self.animations[self.current_action])
            if num_frames > 0:
                self.current_frame_index = (self.current_frame_index + 1) % num_frames
                self.actor.image = self.animations[self.current_action][self.current_frame_index]

    def draw(self):
        self.actor.draw()

    def reset_position(self, pos):
        self.actor.pos = pos


class Player(AnimatedActor):
    """Classe para o jogador."""
    def __init__(self, x, y):
        animations = {
            "idle_r": PLAYER_IDLE_R_FRAMES, "idle_l": PLAYER_IDLE_L_FRAMES,
            "run_r": PLAYER_RUN_R_FRAMES, "run_l": PLAYER_RUN_L_FRAMES,
            "jump_r": [PLAYER_JUMP_R_FRAME], "jump_l": [PLAYER_JUMP_L_FRAME] 
        }
        super().__init__(animations["idle_r"][0], (x, y), animations)
        self.start_pos = (x, y)
        self.velocity_y = 0
        self.on_ground = False
        self.is_jumping = False
        self.health = PLAYER_MAX_HEALTH
        self.is_moving_x = False
        self.invincibility_timer = 0 
        self.hurt_frame_display_timer = 0 

    def _set_standard_animation_action(self):
        """Define a ação de animação padrão baseada no estado do jogador."""
        if not self.on_ground:
            self.set_action("jump")
        elif self.is_moving_x:
            self.set_action("run")
        else:
            self.set_action("idle")

    def update(self, dt, platforms_list):
        if self.health <= 0:
            return

        # Movimento e colisão
        prev_x, prev_y = self.actor.pos
        self.is_moving_x = False
        if keyboard.left:
            self.actor.x -= PLAYER_SPEED
            self.facing_direction = -1
            self.is_moving_x = True
        if keyboard.right:
            self.actor.x += PLAYER_SPEED
            self.facing_direction = 1
            self.is_moving_x = True

        for plat in platforms_list:
            if self.actor.colliderect(plat):
                self.actor.x = prev_x 
                break

        if not self.on_ground:
            self.velocity_y += GRAVITY
            self.actor.y += self.velocity_y

        self.on_ground = False 
        for plat in platforms_list:
            if self.actor.colliderect(plat):
                if self.velocity_y > 0: 
                    self.actor.bottom = plat.top
                    self.on_ground = True
                    self.is_jumping = False
                    self.velocity_y = 0
                elif self.velocity_y < 0: 
                    self.actor.top = plat.bottom
                    self.velocity_y = 0 
                break

        if keyboard.space and self.on_ground and not self.is_jumping:
            self.velocity_y = PLAYER_JUMP_STRENGTH
            self.on_ground = False
            self.is_jumping = True
            if sounds_on: getattr(sounds, SOUND_JUMP_FILENAME).play()
        
        # Invencibilidade e cooldown
        if self.invincibility_timer > 0:
            self.invincibility_timer -= dt
            self.actor.opacity = 0.5 if (int(self.invincibility_timer * 10) % 2 == 0) else 1.0
        else:
            self.actor.opacity = 1.0

        # Frame de dano
        if self.hurt_frame_display_timer > 0:
            self.hurt_frame_display_timer -= dt
            try:
                if self.facing_direction == 1:
                    self.actor.image = PLAYER_HURT_R_FRAME
                else:
                    self.actor.image = PLAYER_HURT_L_FRAME
            except NameError: 
                print("AVISO: PLAYER_HURT_R_FRAME ou PLAYER_HURT_L_FRAME não definidos. Usando animação padrão.")
                self._set_standard_animation_action()
                current_frame_duration = ANIMATION_FRAME_DURATION
                if self.current_action and self.current_action.startswith("idle"):
                    current_frame_duration = PLAYER_IDLE_ANIMATION_FRAME_DURATION
                super().update_animation(dt, specific_frame_duration=current_frame_duration)
        else:
            # Se não estiver exibindo frame de dano, processa animação normal
            self._set_standard_animation_action()
            current_frame_duration = ANIMATION_FRAME_DURATION
            if self.current_action and self.current_action.startswith("idle"):
                current_frame_duration = PLAYER_IDLE_ANIMATION_FRAME_DURATION
            super().update_animation(dt, specific_frame_duration=current_frame_duration)


        # Limites da tela 
        if self.actor.left < 0: self.actor.left = 0
        if self.actor.right > WIDTH: self.actor.right = WIDTH
        if self.actor.top < 0: self.actor.top = 0; self.velocity_y = 0 
        if self.actor.top > HEIGHT + self.actor.height: 
            self.take_damage(self.health) 


    def take_damage(self, amount):
        global game_state
        if self.invincibility_timer <= 0: 
            self.health -= amount
            if sounds_on: getattr(sounds, SOUND_HURT_FILENAME).play()
            
            self.invincibility_timer = 1.5 
            self.hurt_frame_display_timer = PLAYER_HURT_FRAME_DURATION 

            if self.health <= 0:
                self.health = 0
                game_state = GAME_STATE_GAME_OVER
                if music_on: music.stop()

    def reset(self):
        super().reset_position(self.start_pos)
        self.health = PLAYER_MAX_HEALTH
        self.velocity_y = 0
        self.on_ground = False
        self.is_jumping = False
        self.facing_direction = 1
        self.invincibility_timer = 0
        self.hurt_frame_display_timer = 0 
        self.actor.opacity = 1.0
        self.set_action("idle")


class Enemy(AnimatedActor):
    """Classe para os inimigos."""
    def __init__(self, x, y, platform_left_edge, platform_right_edge): 
        animations = {
            "idle_r": ENEMY_IDLE_R_FRAMES, "idle_l": ENEMY_IDLE_L_FRAMES,
            "walk_r": ENEMY_WALK_R_FRAMES, "walk_l": ENEMY_WALK_L_FRAMES,
        }
        initial_frame_key = "walk_r" if "walk_r" in animations and animations["walk_r"] else "idle_r"
        initial_image = "slime_idle_r_0" 
        if initial_frame_key in animations and animations[initial_frame_key]:
            initial_image = animations[initial_frame_key][0]
        elif animations and list(animations.values()) and list(animations.values())[0]: 
            initial_image = list(animations.values())[0][0]
            print(f"Aviso: Animação inicial '{initial_frame_key}' para Enemy não encontrada ou vazia. Usando '{initial_image}'.")
        else:
            print(f"Aviso Crítico: Nenhuma animação válida encontrada para Enemy. Usando fallback '{initial_image}'.")


        super().__init__(initial_image, (x, y), animations)
        self.start_pos = (x,y)
        self.patrol_min_x = platform_left_edge
        self.patrol_max_x = platform_right_edge
        self.speed = ENEMY_PATROL_SPEED
        self.is_active = True 
        self.set_action("walk") 
        self.pause_timer = 0 

    def update(self, dt, platforms_list): 
        if not self.is_active:
            return

        if self.pause_timer > 0:
            self.pause_timer -= dt
            self.set_action("idle") 
        else:
            self.set_action("walk")
            self.actor.x += self.speed * self.facing_direction

            if self.facing_direction == 1 and self.actor.right >= self.patrol_max_x:
                self.actor.right = self.patrol_max_x 
                self.facing_direction = -1
                self.pause_timer = random.uniform(0.5, 2.0) 
            elif self.facing_direction == -1 and self.actor.left <= self.patrol_min_x:
                self.actor.left = self.patrol_min_x 
                self.facing_direction = 1
                self.pause_timer = random.uniform(0.5, 2.0)

        super().update_animation(dt) 


    def defeat(self):
        self.is_active = False
        self.actor.opacity = 0 
        if sounds_on: getattr(sounds, SOUND_ENEMY_DEFEAT_FILENAME).play()


    def reset(self):
        super().reset_position(self.start_pos)
        self.is_active = True
        self.facing_direction = random.choice([-1, 1]) 
        self.pause_timer = 0
        self.actor.opacity = 1.0
        if self.actor.left < self.patrol_min_x:
            self.actor.left = self.patrol_min_x
        if self.actor.right > self.patrol_max_x:
            self.actor.right = self.patrol_max_x
        self.set_action("walk")


# --- Variáveis Globais do Jogo ---
player_entity = None
list_of_platforms = []
list_of_enemies = []
background_play_actor = None

# Botões do Menu
BUTTON_WIDTH = 220
BUTTON_HEIGHT = 50
BUTTON_SPACING = 15 
BUTTON_Y_START = HEIGHT // 2 - BUTTON_HEIGHT * 2 - int(BUTTON_SPACING * 1.5) 


start_button_rect = Rect(
    (WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_Y_START),
    (BUTTON_WIDTH, BUTTON_HEIGHT)
)
controls_button_rect = Rect(
    (WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_Y_START + BUTTON_HEIGHT + BUTTON_SPACING),
    (BUTTON_WIDTH, BUTTON_HEIGHT)
)
sound_button_rect = Rect(
    (WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_Y_START + (BUTTON_HEIGHT + BUTTON_SPACING) * 2),
    (BUTTON_WIDTH, BUTTON_HEIGHT)
)
exit_button_rect = Rect(
    (WIDTH // 2 - BUTTON_WIDTH // 2, BUTTON_Y_START + (BUTTON_HEIGHT + BUTTON_SPACING) * 3),
    (BUTTON_WIDTH, BUTTON_HEIGHT)
)

# Botão de Voltar (menu de controles)
back_button_rect = Rect(
    (WIDTH // 2 - (BUTTON_WIDTH - 50) // 2, HEIGHT - BUTTON_HEIGHT - 30), 
    (BUTTON_WIDTH - 50, BUTTON_HEIGHT)
)


# --- Funções de Configuração e Lógica do Jogo ---

def create_platform(x, y, image_name=PLATFORM_IMAGE, width_tiles=1, height_tiles=1):
    if image_name:
        try:
            platform = Actor(image_name, (x, y))
            return platform
        except Exception as e:
            print(f"Erro ao carregar imagem de plataforma '{image_name}.png': {e}. Usando Rect.")
            return Rect(x - 32, y - 16, 64 * width_tiles, 32 * height_tiles)
    else: 
        return Rect(x - 32, y - 16, 64 * width_tiles, 32 * height_tiles)


def setup_level_one():
    global player_entity, list_of_platforms, list_of_enemies, background_play_actor
    list_of_platforms.clear()
    list_of_enemies.clear()

    try:
        background_play_actor = Actor(BACKGROUND_IMAGE_PLAY)
        background_play_actor.pos = WIDTH // 2, HEIGHT // 2
    except Exception:
        background_play_actor = None 

    player_entity = Player(100, HEIGHT - 100)

    all_ground_blocks = []
    platform_ground_y = HEIGHT - 20 + 16 
    for i in range(WIDTH // 64 + 2):
        x_center = i * 64 - 32 + 32 
        p = create_platform(x_center, platform_ground_y)
        list_of_platforms.append(p)
        all_ground_blocks.append(p)

    target_x_for_enemy1_platform = 300
    platform_for_enemy1 = None
    if all_ground_blocks:
        platform_for_enemy1 = min(all_ground_blocks, key=lambda p: abs(p.centerx - target_x_for_enemy1_platform))
    else: 
        platform_for_enemy1 = create_platform(target_x_for_enemy1_platform, platform_ground_y)
        list_of_platforms.append(platform_for_enemy1)

    plat1_y_center = (HEIGHT - 120) + 16 
    platform_A_for_enemy3 = create_platform(200, plat1_y_center)
    list_of_platforms.append(platform_A_for_enemy3)
    platform_B_adj_to_A = create_platform(264, plat1_y_center) 
    list_of_platforms.append(platform_B_adj_to_A)

    plat2_y_center = (HEIGHT - 200) + 16
    platform_for_enemy2 = create_platform(400, plat2_y_center)
    list_of_platforms.append(platform_for_enemy2)

    plat3_y_center = (HEIGHT - 150) + 16
    platform_for_enemy4 = create_platform(550, plat3_y_center)
    list_of_platforms.append(platform_for_enemy4)
    
    plat4_y_center = (HEIGHT - 250) + 16
    platform_for_enemy5 = create_platform(WIDTH - 150, plat4_y_center)
    list_of_platforms.append(platform_for_enemy5)

    if platform_for_enemy1:
        enemy1_x = platform_for_enemy1.centerx
        enemy1_y = platform_for_enemy1.top - ENEMY_HALF_HEIGHT
        list_of_enemies.append(Enemy(enemy1_x, enemy1_y, platform_for_enemy1.left, platform_for_enemy1.right))

    enemy2_x = platform_for_enemy2.centerx
    enemy2_y = platform_for_enemy2.top - ENEMY_HALF_HEIGHT
    list_of_enemies.append(Enemy(enemy2_x, enemy2_y, platform_for_enemy2.left, platform_for_enemy2.right))

    enemy3_x = platform_A_for_enemy3.centerx
    enemy3_y = platform_A_for_enemy3.top - ENEMY_HALF_HEIGHT
    list_of_enemies.append(Enemy(enemy3_x, enemy3_y, platform_A_for_enemy3.left, platform_A_for_enemy3.right))

    enemy4_x = platform_for_enemy4.centerx
    enemy4_y = platform_for_enemy4.top - ENEMY_HALF_HEIGHT
    list_of_enemies.append(Enemy(enemy4_x, enemy4_y, platform_for_enemy4.left, platform_for_enemy4.right))

    enemy5_x = platform_for_enemy5.centerx
    enemy5_y = platform_for_enemy5.top - ENEMY_HALF_HEIGHT
    list_of_enemies.append(Enemy(enemy5_x, enemy5_y, platform_for_enemy5.left, platform_for_enemy5.right))


def start_new_game():
    global game_state
    setup_level_one() 
    if player_entity: player_entity.reset()
    game_state = GAME_STATE_PLAYING
    
    if music_on:
        try:
            music.stop() 
            music.play(MUSIC_BACKGROUND)
            music.set_volume(0.3)
        except Exception as e:
            print(f"Erro ao tocar música de fundo '{MUSIC_BACKGROUND}': {e}")

def manage_music_and_sounds():
    global music_on, sounds_on
    if music_on or sounds_on: 
        music_on = False
        sounds_on = False
        music.pause() 
    else: 
        music_on = True
        sounds_on = True
        
        music.unpause() 

        current_music_to_play = None
        if game_state == GAME_STATE_PLAYING:
            current_music_to_play = MUSIC_BACKGROUND
        elif game_state == GAME_STATE_MENU or game_state == GAME_STATE_CONTROLS: 
            current_music_to_play = MUSIC_MENU
        elif game_state == GAME_STATE_VICTORY:
            current_music_to_play = MUSIC_VICTORY_FILENAME
        
        if current_music_to_play:
            if isinstance(current_music_to_play, str) and current_music_to_play and not music.is_playing(current_music_to_play):
                try:
                    music.play(current_music_to_play)
                    music.set_volume(0.3) 
                except Exception as e:
                    print(f"Erro ao tentar tocar '{current_music_to_play}' ao ligar sons: {e}")

# --- Funções de Desenho (draw) ---

def draw_menu_ui():
    screen.fill(COLOR_BACKGROUND_MENU)
    screen.draw.text("Knights and Monsters", center=(WIDTH // 2, HEIGHT // 4), fontsize=50, color=COLOR_TEXT, owidth=1, ocolor="black")

    screen.draw.filled_rect(start_button_rect, COLOR_BUTTON)
    screen.draw.text("Começar Jogo", center=start_button_rect.center, fontsize=28, color=COLOR_BUTTON_TEXT)

    screen.draw.filled_rect(controls_button_rect, COLOR_BUTTON)
    screen.draw.text("Controles", center=controls_button_rect.center, fontsize=28, color=COLOR_BUTTON_TEXT)

    sound_status_text = "Música/Sons: LIGADO" if (music_on or sounds_on) else "Música/Sons: DESLIGADO"
    screen.draw.filled_rect(sound_button_rect, COLOR_BUTTON)
    screen.draw.text(sound_status_text, center=sound_button_rect.center, fontsize=22, color=COLOR_BUTTON_TEXT)

    screen.draw.filled_rect(exit_button_rect, COLOR_BUTTON_EXIT)
    screen.draw.text("Sair do Jogo", center=exit_button_rect.center, fontsize=28, color=COLOR_BUTTON_TEXT)

def draw_playing_state():
    if background_play_actor:
        background_play_actor.draw()
    else:
        screen.fill(COLOR_BACKGROUND_PLAY)

    for plat in list_of_platforms:
        if isinstance(plat, Actor): 
            plat.draw()
        else: 
            screen.draw.filled_rect(plat, COLOR_PLATFORM)

    if player_entity:
        player_entity.draw()
        screen.draw.text(f"Vida: {player_entity.health}", (20, 20), fontsize=30, color="white", background="purple", owidth=0.5, ocolor="gray")

    for enemy in list_of_enemies:
        if enemy.is_active: 
            enemy.draw()

def draw_game_over_screen():
    screen.fill((30, 30, 30)) 
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2 - 60), fontsize=70, color=(200,0,0), owidth=1.5, ocolor="white")
    screen.draw.text("Pressione ENTER para voltar ao Menu", center=(WIDTH // 2, HEIGHT // 2 + 20), fontsize=30, color=COLOR_TEXT)

def draw_victory_screen():
    screen.fill(COLOR_VICTORY_BG)
    screen.draw.text("VITÓRIA!", center=(WIDTH // 2, HEIGHT // 2 - 70), fontsize=70, color=COLOR_VICTORY_TEXT, owidth=1.5, ocolor="black")
    screen.draw.text("Você derrotou todos os inimigos!", center=(WIDTH // 2, HEIGHT // 2 -10), fontsize=35, color=COLOR_TEXT)
    screen.draw.text("Pressione ENTER para voltar ao Menu", center=(WIDTH // 2, HEIGHT // 2 + 40), fontsize=30, color=COLOR_TEXT)

def draw_controls_menu():
    screen.fill(COLOR_CONTROLS_BG)
    screen.draw.text("Controles do Jogo", center=(WIDTH // 2, HEIGHT // 6), fontsize=50, color=COLOR_TEXT, owidth=1, ocolor="black")

    control_text_y_start = HEIGHT // 3
    control_text_spacing = 40
    font_size_controls = 28

    screen.draw.text("Seta Esquerda: Mover para a Esquerda", (WIDTH // 4, control_text_y_start), fontsize=font_size_controls, color=COLOR_TEXT)
    screen.draw.text("Seta Direita: Mover para a Direita", (WIDTH // 4, control_text_y_start + control_text_spacing), fontsize=font_size_controls, color=COLOR_TEXT)
    screen.draw.text("Barra de Espaço: Pular", (WIDTH // 4, control_text_y_start + control_text_spacing * 2), fontsize=font_size_controls, color=COLOR_TEXT)
    screen.draw.text("ENTER (nos menus): Selecionar/Continuar", (WIDTH // 4, control_text_y_start + control_text_spacing * 3), fontsize=font_size_controls, color=COLOR_TEXT)
    screen.draw.text("ESC (nesta tela): Voltar ao Menu", (WIDTH // 4, control_text_y_start + control_text_spacing * 4), fontsize=font_size_controls, color=COLOR_TEXT)

    screen.draw.filled_rect(back_button_rect, COLOR_BUTTON)
    screen.draw.text("Voltar", center=back_button_rect.center, fontsize=28, color=COLOR_BUTTON_TEXT)


# --- Funções de Evento Principais do Pygame Zero ---

def draw():
    screen.clear()
    if game_state == GAME_STATE_MENU:
        draw_menu_ui()
    elif game_state == GAME_STATE_PLAYING:
        draw_playing_state()
    elif game_state == GAME_STATE_GAME_OVER:
        draw_game_over_screen()
    elif game_state == GAME_STATE_VICTORY: 
        draw_victory_screen()
    elif game_state == GAME_STATE_CONTROLS: 
        draw_controls_menu()


def update(dt):
    global game_state
    if game_state == GAME_STATE_PLAYING:
        if player_entity:
            player_entity.update(dt, list_of_platforms)

            if player_entity.health > 0 and player_entity.invincibility_timer <= 0:
                for enemy in list_of_enemies:
                    if enemy.is_active and player_entity.actor.colliderect(enemy.actor):
                        if player_entity.velocity_y > 0 and \
                           player_entity.actor.bottom < enemy.actor.centery + 10: 
                            enemy.defeat()
                            player_entity.velocity_y = PLAYER_JUMP_STRENGTH * 0.6 
                            if sounds_on: getattr(sounds, SOUND_ENEMY_DEFEAT_FILENAME).play()
                            
                            all_enemies_defeated = True
                            for e_check in list_of_enemies:
                                if e_check.is_active:
                                    all_enemies_defeated = False
                                    break
                            if all_enemies_defeated:
                                game_state = GAME_STATE_VICTORY
                                if music_on:
                                    music.stop()
                                    try:
                                        if MUSIC_VICTORY_FILENAME: 
                                            music.play(MUSIC_VICTORY_FILENAME)
                                            music.set_volume(0.4)
                                    except Exception as e:
                                        print(f"Erro ao tocar música de vitória '{MUSIC_VICTORY_FILENAME}': {e}")
                                return 
                        else: 
                            player_entity.take_damage(1)
                        break 

        for enemy in list_of_enemies:
            if enemy.is_active:
                enemy.update(dt, list_of_platforms)

    elif game_state == GAME_STATE_GAME_OVER or game_state == GAME_STATE_VICTORY:
        if keyboard.RETURN or keyboard.KP_ENTER:
            game_state = GAME_STATE_MENU
            if music_on: 
                try:
                    music.stop()
                    if MUSIC_MENU and not music.is_playing(MUSIC_MENU):
                         music.play(MUSIC_MENU); music.set_volume(0.3)
                except Exception as e:
                    print(f"Erro ao tocar música do menu (de {game_state}): {e}")
    
    elif game_state == GAME_STATE_CONTROLS:
        if keyboard.escape: 
            game_state = GAME_STATE_MENU
            if sounds_on: getattr(sounds, SOUND_CLICK_FILENAME).play()
            if music_on and MUSIC_MENU and not music.is_playing(MUSIC_MENU):
                try:
                    music.play(MUSIC_MENU); music.set_volume(0.3)
                except Exception as e:
                    print(f"Erro ao tocar música do menu (de controlos): {e}")


def on_mouse_down(pos, button):
    global game_state
    if game_state == GAME_STATE_MENU:
        if button == mouse.LEFT:
            clicked_on_button = False
            if start_button_rect.collidepoint(pos):
                start_new_game()
                clicked_on_button = True
            elif controls_button_rect.collidepoint(pos): 
                game_state = GAME_STATE_CONTROLS
                clicked_on_button = True
            elif sound_button_rect.collidepoint(pos):
                manage_music_and_sounds()
                clicked_on_button = True
            elif exit_button_rect.collidepoint(pos):
                exit() 
            
            if clicked_on_button and sounds_on:
                getattr(sounds, SOUND_CLICK_FILENAME).play()
    
    elif game_state == GAME_STATE_CONTROLS:
        if button == mouse.LEFT:
            if back_button_rect.collidepoint(pos):
                game_state = GAME_STATE_MENU
                if sounds_on: getattr(sounds, SOUND_CLICK_FILENAME).play()
                if music_on and MUSIC_MENU and not music.is_playing(MUSIC_MENU):
                    try:
                        music.play(MUSIC_MENU); music.set_volume(0.3)
                    except Exception as e:
                        print(f"Erro ao tocar música do menu (de control3s via botão): {e}")

# --- Iniciar Jogo ---
if music_on and MUSIC_MENU:
    try:
        music.play(MUSIC_MENU)
        music.set_volume(0.3)
    except Exception as e:
        print(f"Aviso: Não foi possível tocar a música do menu '{MUSIC_MENU}': {e}")

pgzrun.go() 
