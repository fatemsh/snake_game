import pygame
import sys
import random
import time
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Snake colors
COLORS = {
    "Green": GREEN,
    "Red": RED,
    "Blue": BLUE,
    "Yellow": YELLOW,
    "Purple": PURPLE,
    "Cyan": CYAN
}

# Difficulty levels
DIFFICULTY = {
    "Easy": 10,
    "Medium": 15,
    "Hard": 25,
    "Expert": 40
}

class Snake:
    def __init__(self, color):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.length = 1
        self.color = color
        self.score = 0
        self.level = 1
        
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)
        
        if new_head in self.positions[1:]:
            return False  # Game over
        
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()
            
        return True
    
    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.length = 1
        self.score = 0
        self.level = 1
    
    def render(self, surface):
        for i, p in enumerate(self.positions):
            if i == 0:
                pygame.draw.rect(surface, WHITE, 
                                (p[0] * GRID_SIZE, p[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(surface, self.color, 
                                (p[0] * GRID_SIZE + 2, p[1] * GRID_SIZE + 2, GRID_SIZE - 4, GRID_SIZE - 4))
            else:
                intensity = 1.0 - (i / self.length) * 0.7
                r = min(255, int(self.color[0] * intensity))
                g = min(255, int(self.color[1] * intensity))
                b = min(255, int(self.color[2] * intensity))
                body_color = (r, g, b)
                pygame.draw.rect(surface, body_color, 
                                (p[0] * GRID_SIZE, p[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(surface, (r//2, g//2, b//2), 
                                (p[0] * GRID_SIZE, p[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()
        
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    
    def render(self, surface):
        pygame.draw.rect(surface, self.color, 
                        (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.draw.circle(surface, (200, 0, 0), 
                          (self.position[0] * GRID_SIZE + GRID_SIZE // 2, 
                           self.position[1] * GRID_SIZE + GRID_SIZE // 2), 
                          GRID_SIZE // 2 - 2)
        pygame.draw.ellipse(surface, GREEN, 
                           (self.position[0] * GRID_SIZE + GRID_SIZE // 2, 
                            self.position[1] * GRID_SIZE - 2, 
                            GRID_SIZE // 3, GRID_SIZE // 2))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 30)
        self.big_font = pygame.font.SysFont("arial", 60)
        self.small_font = pygame.font.SysFont("arial", 20)
        
        self.snake_color = GREEN
        self.difficulty = "Medium"
        self.speed = DIFFICULTY[self.difficulty]
        
        self.snake = Snake(self.snake_color)
        self.food = Food()
        self.game_over = False
        self.paused = False
        self.in_menu = True
        
        try:
            self.eat_sound = mixer.Sound("eat.wav")
            self.game_over_sound = mixer.Sound("game_over.wav")
        except:
            self.eat_sound = mixer.Sound(buffer=bytearray(100))
            self.game_over_sound = mixer.Sound(buffer=bytearray(100))
        
        try:
            mixer.music.load("background.mp3")
            mixer.music.set_volume(0.5)
            mixer.music.play(-1)
        except:
            pass
    
    def draw_text(self, text, font, color, x, y, centered=False):
        text_surface = font.render(text, True, color)
        if centered:
            text_rect = text_surface.get_rect(center=(x, y))
        else:
            text_rect = text_surface.get_rect(topleft=(x, y))
        self.screen.blit(text_surface, text_rect)
        return text_rect
    
    def show_menu(self):
        self.screen.fill(BLACK)
        
        self.draw_text("Snake Game", self.big_font, GREEN, WIDTH // 2, HEIGHT // 4, True)
        
        self.draw_text("Snake Color:", self.font, WHITE, WIDTH // 2 - 200, HEIGHT // 2 - 50)
        
        color_buttons = []
        for i, (color_name, color_value) in enumerate(COLORS.items()):
            btn_rect = pygame.Rect(WIDTH // 2 + 50 + (i % 3) * 100, HEIGHT // 2 - 60 + (i // 3) * 50, 80, 40)
            pygame.draw.rect(self.screen, color_value, btn_rect)
            pygame.draw.rect(self.screen, WHITE, btn_rect, 2)
            if self.snake_color == color_value:
                pygame.draw.rect(self.screen, WHITE, btn_rect, 4)
            self.draw_text(color_name, self.small_font, WHITE, btn_rect.centerx, btn_rect.centery, True)
            color_buttons.append((btn_rect, color_value))
        
        self.draw_text("Difficulty:", self.font, WHITE, WIDTH // 2 - 200, HEIGHT // 2 + 100)
        
        diff_buttons = []
        for i, (diff_name, diff_value) in enumerate(DIFFICULTY.items()):
            btn_rect = pygame.Rect(WIDTH // 2 + 50 + i * 120, HEIGHT // 2 + 100, 100, 40)
            pygame.draw.rect(self.screen, GRAY, btn_rect)
            pygame.draw.rect(self.screen, WHITE, btn_rect, 2)
            if self.difficulty == diff_name:
                pygame.draw.rect(self.screen, GREEN, btn_rect, 4)
            self.draw_text(diff_name, self.small_font, WHITE, btn_rect.centerx, btn_rect.centery, True)
            diff_buttons.append((btn_rect, diff_name))
        
        start_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)
        pygame.draw.rect(self.screen, GREEN, start_rect)
        pygame.draw.rect(self.screen, WHITE, start_rect, 3)
        self.draw_text("Start Game", self.font, BLACK, start_rect.centerx, start_rect.centery, True)
        
        pygame.display.flip()
        
        return color_buttons, diff_buttons, start_rect
    
    def show_game_over(self):
        self.screen.fill(BLACK)
        
        self.draw_text("Game Over!", self.big_font, RED, WIDTH // 2, HEIGHT // 3, True)
        self.draw_text(f"Score: {self.snake.score}", self.font, WHITE, WIDTH // 2, HEIGHT // 2, True)
        self.draw_text(f"Level: {self.snake.level}", self.font, WHITE, WIDTH // 2, HEIGHT // 2 + 50, True)
        
        restart_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 150, 300, 50)
        pygame.draw.rect(self.screen, GREEN, restart_rect)
        pygame.draw.rect(self.screen, WHITE, restart_rect, 3)
        self.draw_text("Play Again", self.font, BLACK, restart_rect.centerx, restart_rect.centery, True)
        
        menu_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 80, 300, 50)
        pygame.draw.rect(self.screen, BLUE, menu_rect)
        pygame.draw.rect(self.screen, WHITE, menu_rect, 3)
        self.draw_text("Main Menu", self.font, BLACK, menu_rect.centerx, menu_rect.centery, True)
        
        pygame.display.flip()
        
        return restart_rect, menu_rect
    
    def run(self):
        while True:
            if self.in_menu:
                color_buttons, diff_buttons, start_rect = self.show_menu()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        
                        for rect, color in color_buttons:
                            if rect.collidepoint(mouse_pos):
                                self.snake_color = color
                                self.snake.color = color
                        
                        for rect, diff_name in diff_buttons:
                            if rect.collidepoint(mouse_pos):
                                self.difficulty = diff_name
                                self.speed = DIFFICULTY[self.difficulty]
                        
                        if start_rect.collidepoint(mouse_pos):
                            self.in_menu = False
                            self.game_over = False
                            self.snake.reset()
            
            elif self.game_over:
                restart_rect, menu_rect = self.show_game_over()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        
                        if restart_rect.collidepoint(mouse_pos):
                            self.game_over = False
                            self.snake.reset()
                        
                        if menu_rect.collidepoint(mouse_pos):
                            self.in_menu = True
                            self.game_over = False
            
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.paused = not self.paused
                        
                        if not self.paused:
                            if event.key == pygame.K_UP and self.snake.direction != (0, 1):
                                self.snake.direction = (0, -1)
                            elif event.key == pygame.K_DOWN and self.snake.direction != (0, -1):
                                self.snake.direction = (0, 1)
                            elif event.key == pygame.K_LEFT and self.snake.direction != (1, 0):
                                self.snake.direction = (-1, 0)
                            elif event.key == pygame.K_RIGHT and self.snake.direction != (-1, 0):
                                self.snake.direction = (1, 0)
                
                if not self.paused and not self.game_over:
                    if not self.snake.update():
                        self.game_over = True
                        try:
                            self.game_over_sound.play()
                        except:
                            pass
                    
                    if self.snake.get_head_position() == self.food.position:
                        try:
                            self.eat_sound.play()
                        except:
                            pass
                        self.snake.length += 1
                        self.snake.score += 10 * self.snake.level
                        
                        if self.snake.length % 3 == 0:
                            self.snake.level += 1
                            self.speed += 2
                        
                        self.food.randomize_position()
                        while self.food.position in self.snake.positions:
                            self.food.randomize_position()
                    
                    self.screen.fill(BLACK)
                    
                    for x in range(0, WIDTH, GRID_SIZE):
                        pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT))
                    for y in range(0, HEIGHT, GRID_SIZE):
                        pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y))
                    
                    self.snake.render(self.screen)
                    self.food.render(self.screen)
                    
                    self.draw_text(f"Score: {self.snake.score}", self.font, WHITE, 10, 10)
                    self.draw_text(f"Level: {self.snake.level}", self.font, WHITE, 10, 50)
                    self.draw_text(f"Speed: {self.difficulty}", self.font, WHITE, 10, 90)
                    
                    if self.paused:
                        self.draw_text("Paused", self.big_font, WHITE, WIDTH // 2, HEIGHT // 2, True)
                    
                    pygame.display.flip()
                    self.clock.tick(self.speed)

if __name__ == "__main__":
    game = Game()
    game.run()
