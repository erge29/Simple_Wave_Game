#  WAVE GAME
# =========================================================

import pygame
import random
import math
import json
import os
import sys

pygame.init()


#  KONSTANTA


SCREEN_W  = 1280
SCREEN_H  = 720
FPS       = 60
TITLE     = "Wave Game - 45 Degree Precision"

TRAIL_LENGTH    = 45
OBS_SPEED_BASE  = 6.0

OBS_SPAWN_TICK  = 75

SPEED_SCALE     = 0.07   
GAP_SCALE       = 0.55   

SCORE_PER_FRAME = 0.025  
SCORE_PER_PASS  = 5      

SCORE_FILE = "scores.json"
MAX_SCORES = 10          

C_BG        = (10, 10, 18)
C_GRID      = (20, 22, 35)
C_WHITE     = (230, 230, 240)
C_CYAN      = (0, 230, 255)
C_RED       = (255, 60, 60)
C_ORANGE    = (255, 160, 40)
C_YELLOW    = (255, 230, 50)
C_GREEN     = (50, 220, 100)
C_GRAY      = (100, 105, 120)
C_DARK_GRAY = (30, 32, 45)


#  INISIALISASI LAYAR


screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_W, SCREEN_H = screen.get_size()
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Scale factor relatif terhadap resolusi referensi 900x500
REF_W, REF_H = 900, 500
SCALE = min(SCREEN_W / REF_W, SCREEN_H / REF_H)

def S(val):
    """Scale nilai berdasarkan resolusi layar."""
    return int(val * SCALE)

# Override konstanta gameplay dengan versi scaled
PLAYER_X      = S(130)
PLAYER_RADIUS = S(7)
OBS_GAP_BASE  = S(175)
OBS_GAP_MIN   = S(85)

try:
    font_big   = pygame.font.SysFont("Consolas", S(42), bold=True)
    font_med   = pygame.font.SysFont("Consolas", S(26))
    font_small = pygame.font.SysFont("Consolas", S(18))
except:
    font_big   = pygame.font.SysFont(None, S(42))
    font_med   = pygame.font.SysFont(None, S(26))
    font_small = pygame.font.SysFont(None, S(18))


#  FILE HANDLING


def load_scores():
    try:
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

def save_score(name, score_val):
    scores = load_scores()
    new_entry = {"name": name.upper(), "score": int(score_val)}
    scores.append(new_entry)

    for i in range(1, len(scores)):
        key = scores[i]
        j = i - 1
        while j >= 0 and scores[j]["score"] < key["score"]:
            scores[j + 1] = scores[j]
            j -= 1
        scores[j + 1] = key

    scores = scores[:MAX_SCORES]
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f, indent=2)
    return scores

def search_rank(scores, score_val):
    lo, hi = 0, len(scores) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if scores[mid]["score"] == score_val:
            return mid + 1
        elif scores[mid]["score"] > score_val:
            lo = mid + 1
        else:
            hi = mid - 1
    return lo + 1

def get_best_score(scores):
    if not scores:
        return 0
    return scores[0]["score"]


#  KELAS OBSTACLE 


class Obstacle:
    def __init__(self, gap_size, speed):
        margin = S(100)
        self.center_y = random.randint(margin, SCREEN_H - margin)
        self.x        = float(SCREEN_W + 10)
        self.speed    = speed
        self.gap      = gap_size
        self.passed   = False
        
        self.top_h    = self.center_y - self.gap // 2
        self.bot_h    = SCREEN_H - (self.center_y + self.gap // 2)
        self.width    = max(self.top_h, self.bot_h) * 2

    def update(self):
        self.x -= self.speed

    def draw(self, surf):
        x      = int(self.x)
        w      = int(self.width)
        mid_x  = x + w // 2
        top_y  = self.center_y - self.gap // 2
        bot_y  = self.center_y + self.gap // 2

        brightness = max(0, min(255, int(255 - (self.x / SCREEN_W) * 60)))
        color = (brightness, 55, 55)

        top_tri = [
            (mid_x - top_y, 0),
            (mid_x + top_y, 0),
            (mid_x, top_y)
        ]
        pygame.draw.polygon(surf, color, top_tri)
        pygame.draw.polygon(surf, C_RED, top_tri, 2)

        bot_tri = [
            (mid_x - self.bot_h, SCREEN_H),
            (mid_x + self.bot_h, SCREEN_H),
            (mid_x, bot_y)
        ]
        pygame.draw.polygon(surf, color, bot_tri)
        pygame.draw.polygon(surf, C_RED, bot_tri, 2)

    def is_off_screen(self):
        return self.x + self.width < -200

    def check_collision(self, px, py, radius):
        top_y = self.center_y - self.gap // 2
        bot_y = self.center_y + self.gap // 2
        w     = int(self.width)
        mid_x = self.x + w // 2

        if mid_x - top_y <= px <= mid_x + top_y:
            dx = abs(px - mid_x)
            roof_y = top_y - dx
            if py - radius < roof_y:
                return True

        if mid_x - self.bot_h <= px <= mid_x + self.bot_h:
            dx = abs(px - mid_x)
            roof_y = bot_y + dx
            if py + radius > roof_y:
                return True

        return False


#  KELAS PARTICLE


class Particle:
    def __init__(self, x, y):
        angle  = random.uniform(0, 2 * math.pi)
        speed  = random.uniform(2, 7)
        self.vx  = math.cos(angle) * speed
        self.vy  = math.sin(angle) * speed
        self.x   = float(x)
        self.y   = float(y)
        self.life = random.randint(25, 50)
        self.max_life = self.life
        self.radius = random.randint(2, 5)
        colors = [C_CYAN, C_ORANGE, C_YELLOW, C_WHITE]
        self.color = random.choice(colors)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha_ratio = self.life / self.max_life
        r = max(1, int(self.radius * alpha_ratio))
        col = tuple(int(c * alpha_ratio) for c in self.color)
        pygame.draw.circle(surf, col, (int(self.x), int(self.y)), r)

    def is_dead(self):
        return self.life <= 0


#  KELAS PLAYER


class Player:
    def __init__(self):
        self.x     = PLAYER_X
        self.y     = float(SCREEN_H // 2)
        self.trail = [] 
        self.alive = True

    def update(self, going_up, current_speed):
        if going_up:
            self.y -= current_speed
        else:
            self.y += current_speed

        self.y = max(float(PLAYER_RADIUS), min(float(SCREEN_H - PLAYER_RADIUS), self.y))
        self.trail.append([self.x, int(self.y)])

        for t in self.trail:
            t[0] -= current_speed

        if len(self.trail) > TRAIL_LENGTH:
            self.trail.pop(0)

    def draw(self, surf):
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                ratio = i / len(self.trail)
                thickness = max(1, int(S(5) * ratio))
                col = (int(C_CYAN[0] * ratio), int(C_CYAN[1] * ratio), int(C_CYAN[2] * ratio))
                
                pygame.draw.line(surf, col, 
                                 (int(self.trail[i][0]), int(self.trail[i][1])), 
                                 (int(self.trail[i+1][0]), int(self.trail[i+1][1])), 
                                 thickness)

        pygame.draw.circle(surf, C_CYAN, (int(self.x), int(self.y)), PLAYER_RADIUS)
        pygame.draw.circle(surf, C_WHITE, (int(self.x), int(self.y)), PLAYER_RADIUS, 2)


#  FUNGSI UTILITAS


def draw_text(surf, text, font, color, x, y, align="left"):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if align == "center":
        rect.centerx = x
        rect.y = y
    elif align == "right":
        rect.right = x
        rect.y = y
    else:
        rect.x = x
        rect.y = y
    surf.blit(rendered, rect)
    return rect

def draw_grid(surf, offset):
    grid_size = S(60)
    start_x = int(offset % grid_size) - grid_size
    for x in range(start_x, SCREEN_W + grid_size, grid_size):
        pygame.draw.line(surf, C_GRID, (x, 0), (x, SCREEN_H))
    for y in range(0, SCREEN_H, grid_size):
        pygame.draw.line(surf, C_GRID, (0, y), (SCREEN_W, y))


#  SCREEN MENU UTAMA


def screen_menu(scores):
    name_chars = list("PLAYER")
    active     = True
    blink      = 0

    while active:
        clock.tick(FPS)
        blink += 1

        screen.fill(C_BG)
        
        for x in range(0, SCREEN_W, 60):
            pygame.draw.line(screen, C_GRID, (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, 60):
            pygame.draw.line(screen, C_GRID, (0, y), (SCREEN_W, y))

        draw_text(screen, "WAVE GAME", font_big, C_CYAN, SCREEN_W // 2, S(60), "center")
        draw_text(screen, "45° precision mechanic", font_small, C_GRAY, SCREEN_W // 2, S(115), "center")
        draw_text(screen, "NAMA PEMAIN:", font_small, C_GRAY, SCREEN_W // 2, S(165), "center")

        name_str = "".join(name_chars)
        cursor   = "|" if (blink // 20) % 2 == 0 else " "
        draw_text(screen, name_str + cursor, font_med, C_WHITE, SCREEN_W // 2, S(190), "center")

        draw_text(screen, "TAHAN klik / SPACE  ->  naik (45)", font_small, C_GRAY, SCREEN_W // 2, S(250), "center")
        draw_text(screen, "LEPAS               ->  turun (45)", font_small, C_GRAY, SCREEN_W // 2, S(275), "center")
        draw_text(screen, "P  ->  pause    ESC  ->  keluar", font_small, C_GRAY, SCREEN_W // 2, S(300), "center")

        draw_text(screen, "TOP SCORES", font_small, C_ORANGE, SCREEN_W // 2, S(340), "center")
        for i, entry in enumerate(scores[:4]):
            col = C_YELLOW if i == 0 else C_WHITE
            draw_text(screen, f"#{i+1}  {entry['name']:<8}  {entry['score']:>6}", font_small, col, SCREEN_W // 2, S(365) + i * S(22), "center")

        if (blink // 30) % 2 == 0:
            draw_text(screen, "[ ENTER ] untuk mulai", font_med, C_GREEN, SCREEN_W // 2, S(450), "center")

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name_chars:
                    return "".join(name_chars)
                elif event.key == pygame.K_BACKSPACE:
                    if name_chars:
                        name_chars.pop()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif len(name_chars) < 8:
                    ch = event.unicode
                    if ch.isalpha() or ch.isdigit():
                        name_chars.append(ch.upper())


#  SCREEN GAME OVER


def screen_game_over(score_val, player_name, scores):
    new_scores = save_score(player_name, score_val)
    rank       = search_rank(new_scores, int(score_val))
    best       = get_best_score(new_scores)

    active = True
    while active:
        clock.tick(FPS)
        screen.fill(C_BG)
        for x in range(0, SCREEN_W, 60):
            pygame.draw.line(screen, C_GRID, (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, 60):
            pygame.draw.line(screen, C_GRID, (0, y), (SCREEN_W, y))

        draw_text(screen, "GAME OVER", font_big, C_RED, SCREEN_W // 2, S(80), "center")
        draw_text(screen, f"Pemain  :  {player_name}", font_med, C_WHITE,  SCREEN_W // 2, S(160), "center")
        draw_text(screen, f"Score   :  {int(score_val)}", font_med, C_CYAN,   SCREEN_W // 2, S(195), "center")
        draw_text(screen, f"Best    :  {best}",           font_med, C_YELLOW, SCREEN_W // 2, S(230), "center")
        draw_text(screen, f"Ranking :  #{rank}",          font_med, C_ORANGE, SCREEN_W // 2, S(265), "center")

        draw_text(screen, "[ SPACE ]  main lagi", font_med, C_GREEN, SCREEN_W // 2, S(340), "center")
        draw_text(screen, "[ M ]      menu utama", font_med, C_GRAY,  SCREEN_W // 2, S(375), "center")
        draw_text(screen, "[ ESC ]    keluar",     font_med, C_GRAY,  SCREEN_W // 2, S(410), "center")

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True 
                if event.key == pygame.K_m:
                    return False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    return False


#  SCREEN PAUSE


def screen_pause():
    while True:
        clock.tick(FPS)
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        draw_text(screen, "PAUSE", font_big, C_WHITE, SCREEN_W // 2, S(180), "center")
        draw_text(screen, "[ P ]    lanjutkan", font_med, C_GREEN, SCREEN_W // 2, S(270), "center")
        draw_text(screen, "[ ESC ]  keluar",    font_med, C_GRAY,  SCREEN_W // 2, S(310), "center")

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return True 
                if event.key == pygame.K_ESCAPE:
                    return False


#  LOOP GAME UTAMA


def run_game(player_name):
    player      = Player()
    obstacles   = []
    particles   = []
    score       = 0.0
    spawn_timer = 0
    paused      = False
    bg_offset   = 0.0

    obs_speed  = OBS_SPEED_BASE
    gap_size   = float(OBS_GAP_BASE)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return score
                if event.key == pygame.K_p:
                    paused = True

        if paused:
            result = screen_pause()
            if not result:
                return score
            paused = False

        mouse_pressed = pygame.mouse.get_pressed()[0]
        keys_pressed  = pygame.key.get_pressed()
        going_up      = mouse_pressed or keys_pressed[pygame.K_SPACE]

        player.update(going_up, obs_speed)
        
        bg_offset -= obs_speed

        spawn_timer += 1
        if spawn_timer >= OBS_SPAWN_TICK:
            obstacles.append(Obstacle(int(gap_size), obs_speed))
            spawn_timer = 0

        for obs in obstacles:
            obs.update()

            if obs.check_collision(player.x, player.y, PLAYER_RADIUS):
                for _ in range(40):
                    particles.append(Particle(player.x, player.y))
                return score 

            if not obs.passed and obs.x + (obs.width / 2) < player.x:
                obs.passed = True
                score     += SCORE_PER_PASS

        obstacles = [o for o in obstacles if not o.is_off_screen()]
        score += SCORE_PER_FRAME

        obs_speed  = OBS_SPEED_BASE + score * SPEED_SCALE
        gap_size   = max(OBS_GAP_MIN, OBS_GAP_BASE - score * GAP_SCALE)

        for p in particles:
            p.update()
        particles = [p for p in particles if not p.is_dead()]

        screen.fill(C_BG)
        draw_grid(screen, bg_offset)

        for obs in obstacles:
            obs.draw(screen)

        player.draw(screen)

        for p in particles:
            p.draw(screen)

        draw_text(screen, f"SCORE  {int(score):>6}", font_med, C_CYAN,   S(20), S(15))
        draw_text(screen, f"SPEED  {obs_speed:.1f}x", font_small, C_GRAY, S(20), S(50))
        draw_text(screen, f"GAP    {int(gap_size)}px",  font_small, C_GRAY, S(20), S(72))
        draw_text(screen, player_name,                 font_small, C_GRAY, SCREEN_W - S(20), S(15), "right")
        draw_text(screen, "P = pause",                 font_small, C_DARK_GRAY, SCREEN_W - S(20), S(40), "right")

        speed_ratio = min(1.0, (obs_speed - OBS_SPEED_BASE) / 8.0)
        bar_w = S(120)
        pygame.draw.rect(screen, C_DARK_GRAY, (S(20), S(95), bar_w, S(8)), border_radius=4)
        pygame.draw.rect(screen, C_ORANGE,    (S(20), S(95), int(bar_w * speed_ratio), S(8)), border_radius=4)
        draw_text(screen, "SPEED", font_small, C_GRAY, S(20), S(108))

        pygame.display.flip()


#  ENTRY POINT


def main():
    scores      = load_scores()
    player_name = screen_menu(scores)

    while True:
        final_score = run_game(player_name)
        scores      = load_scores() 
        play_again = screen_game_over(final_score, player_name, scores)

        if not play_again:
            scores      = load_scores()
            player_name = screen_menu(scores)

if __name__ == "__main__":
    main()