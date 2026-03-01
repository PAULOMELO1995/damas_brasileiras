import pygame
import os
import sys
import random
from copy import deepcopy

# Configurações do Pygame
pygame.init()
pygame.mixer.init()

# Sons
SOUNDS = {}
try:
    SOUNDS['move'] = pygame.mixer.Sound("sounds/move.wav")
    SOUNDS['capture'] = pygame.mixer.Sound("sounds/capture.wav")
    SOUNDS['win'] = pygame.mixer.Sound("sounds/win.wav")
    SOUNDS['menu'] = pygame.mixer.Sound("sounds/menu.wav")
except:
    print("Sons não encontrados, continuando sem áudio")

# Configurações do jogo
WIDTH, HEIGHT = 800, 900
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 100, 200)
RED = (200, 0, 0)
GREEN = (0, 180, 0)
GOLD = (255, 215, 0)
YELLOW = (255, 255, 0)
HIGHLIGHT = (100, 255, 100)
MENU_BG = (50, 50, 80)
BUTTON_COLOR = (70, 70, 120)
BUTTON_HOVER = (100, 100, 150)

class Button:
    def __init__(self, x, y, width, height, text, font_size=30):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont('Arial', font_size)
        self.normal_color = BUTTON_COLOR
        self.hover_color = BUTTON_HOVER
        self.current_color = self.normal_color
        self.text_color = WHITE

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.current_color = self.hover_color if self.rect.collidepoint(pos) else self.normal_color
        return self.rect.collidepoint(pos)

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Piece:
    def __init__(self, row, col, team, image):
        self.row = row
        self.col = col
        self.team = team
        self.king = False
        self.x = col * SQUARE_SIZE + SQUARE_SIZE // 2
        self.y = row * SQUARE_SIZE + SQUARE_SIZE // 2
        self.target_x = self.x
        self.target_y = self.y
        self.image = image
        self.animating = False
        self.animation_speed = 0.3  # Velocidade da animação ajustada

    def update(self):
        if self.animating:
            # Movimento mais suave com interpolação linear
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = (dx**2 + dy**2)**0.5
            
            if distance < 2:  # Limite para considerar que chegou no destino
                self.x = self.target_x
                self.y = self.target_y
                self.animating = False
            else:
                # Movimento suave com velocidade constante
                speed = min(self.animation_speed * distance, distance)
                angle = pygame.math.Vector2(dx, dy).angle_to((1, 0))
                self.x += speed * pygame.math.Vector2(1, 0).rotate(-angle).x
                self.y += speed * pygame.math.Vector2(1, 0).rotate(-angle).y

    def draw(self, screen, selected=False):
        pos = (self.x - SQUARE_SIZE//2 + 10, self.y - SQUARE_SIZE//2 + 10)
        
        if self.image:
            screen.blit(self.image, pos)
        else:
            color = RED if self.team == 'red' else BLACK
            pygame.draw.ellipse(screen, color, (pos[0], pos[1], SQUARE_SIZE - 20, SQUARE_SIZE - 20))
        
        if self.king:
            pygame.draw.ellipse(screen, GOLD, (self.x-15, self.y-15, 30, 30))
        
        if selected:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), SQUARE_SIZE//2 - 5, 2)

class Menu:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Damas Brasileiras - Menu")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont('Arial', 50)
        self.font_medium = pygame.font.SysFont('Arial', 30)
        
        self.teams = {
            "Flamengo": "img/flamengo.png",
            "Corinthians": "img/corinthians.png",
            "Palmeiras": "img/palmeiras.png",
            "São Paulo": "img/saopaulo.png",
            "Cruzeiro": "img/cruzeiro.png",
            "Grêmio": "img/gremio.png"
        }
        
        self.difficulties = {
            "Fácil": 1,
            "Médio": 3,
            "Difícil": 5
        }
        
        self.selected_red = None
        self.selected_black = None
        self.selected_difficulty = "Médio"
        self.team_images = {}
        
        self.load_team_images()
        self.create_buttons()

    def load_team_images(self):
        for team, path in self.teams.items():
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path)
                    img = pygame.transform.scale(img, (60, 60))
                    self.team_images[team] = img
                else:
                    print(f"Arquivo não encontrado: {path}")
                    self.team_images[team] = None
            except Exception as e:
                print(f"Erro ao carregar imagem do time {team}: {e}")
                self.team_images[team] = None

    def create_buttons(self):
        button_width = 200
        button_height = 50
        center_x = WIDTH // 2 - button_width // 2
        
        self.start_button = Button(center_x, 750, button_width, button_height, "Iniciar Jogo")
        
        self.difficulty_buttons = []
        y_pos = 650
        for i, diff in enumerate(self.difficulties.keys()):
            btn = Button(center_x + (i-1)*(button_width + 20), y_pos, button_width, button_height, diff)
            self.difficulty_buttons.append(btn)
        
        self.team_buttons_red = []
        self.team_buttons_black = []
        
        team_list = list(self.teams.keys())
        half = len(team_list) // 2
        
        for i, team in enumerate(team_list[:half]):
            btn = Button(100, 200 + i*70, 250, 60, team)
            self.team_buttons_red.append(btn)
            
        for i, team in enumerate(team_list[half:]):
            btn = Button(450, 200 + i*70, 250, 60, team)
            self.team_buttons_black.append(btn)

    def draw(self):
        self.screen.fill(MENU_BG)
        
        title = self.font_large.render("DAMAS BRASILEIRAS", True, WHITE)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        subtitle_red = self.font_medium.render("Selecione seu time (Vermelho):", True, WHITE)
        self.screen.blit(subtitle_red, (100, 150))
        
        subtitle_black = self.font_medium.render("Selecione o time adversário (Preto):", True, WHITE)
        self.screen.blit(subtitle_black, (450, 150))
        
        subtitle_diff = self.font_medium.render("Nível de Dificuldade:", True, WHITE)
        self.screen.blit(subtitle_diff, (WIDTH//2 - subtitle_diff.get_width()//2, 600))
        
        for btn in self.team_buttons_red:
            btn.draw(self.screen)
            if self.team_images.get(btn.text):
                self.screen.blit(self.team_images[btn.text], (btn.rect.x + 180, btn.rect.y))
            
        for btn in self.team_buttons_black:
            btn.draw(self.screen)
            if self.team_images.get(btn.text):
                self.screen.blit(self.team_images[btn.text], (btn.rect.x + 180, btn.rect.y))
        
        for btn in self.difficulty_buttons:
            btn.draw(self.screen)
            if btn.text == self.selected_difficulty:
                pygame.draw.rect(self.screen, YELLOW, btn.rect, 3, border_radius=10)
        
        self.start_button.draw(self.screen)
        
        if self.selected_red:
            for btn in self.team_buttons_red:
                if btn.text == self.selected_red:
                    pygame.draw.rect(self.screen, RED, btn.rect, 3, border_radius=10)
        
        if self.selected_black:
            for btn in self.team_buttons_black:
                if btn.text == self.selected_black:
                    pygame.draw.rect(self.screen, BLACK, btn.rect, 3, border_radius=10)
        
        pygame.display.flip()

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            for btn in self.team_buttons_red:
                if btn.is_clicked(mouse_pos, event):
                    self.selected_red = btn.text
                    if 'menu' in SOUNDS: SOUNDS['menu'].play()
            
            for btn in self.team_buttons_black:
                if btn.is_clicked(mouse_pos, event):
                    if btn.text != self.selected_red:
                        self.selected_black = btn.text
                        if 'menu' in SOUNDS: SOUNDS['menu'].play()
            
            for btn in self.difficulty_buttons:
                if btn.is_clicked(mouse_pos, event):
                    self.selected_difficulty = btn.text
                    if 'menu' in SOUNDS: SOUNDS['menu'].play()
            
            if self.start_button.is_clicked(mouse_pos, event):
                if self.selected_red and self.selected_black:
                    if 'menu' in SOUNDS: SOUNDS['menu'].play()
                    return self.start_game()
        
        for btn in self.team_buttons_red + self.team_buttons_black + self.difficulty_buttons + [self.start_button]:
            btn.check_hover(mouse_pos)
        
        return None

    def start_game(self):
        red_img = None
        black_img = None
        
        try:
            red_path = self.teams[self.selected_red]
            if os.path.exists(red_path):
                red_img = pygame.image.load(red_path)
                red_img = pygame.transform.scale(red_img, (SQUARE_SIZE - 20, SQUARE_SIZE - 20))
        except Exception as e:
            print(f"Erro ao carregar imagem do time {self.selected_red}: {e}")
        
        try:
            black_path = self.teams[self.selected_black]
            if os.path.exists(black_path):
                black_img = pygame.image.load(black_path)
                black_img = pygame.transform.scale(black_img, (SQUARE_SIZE - 20, SQUARE_SIZE - 20))
        except Exception as e:
            print(f"Erro ao carregar imagem do time {self.selected_black}: {e}")
        
        difficulty = self.difficulties[self.selected_difficulty]
        
        return {
            'red_team': self.selected_red,
            'black_team': self.selected_black,
            'red_image': red_img,
            'black_image': black_img,
            'difficulty': difficulty
        }

    def run(self):
        while True:
            game_settings = self.handle_events()
            if game_settings:
                return game_settings
            self.draw()
            self.clock.tick(60)

class DamasGame:
    def __init__(self, red_team, black_team, red_image, black_image, difficulty):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"Damas Brasileiras: {red_team} vs {black_team}")
        self.clock = pygame.time.Clock()
        self.selected_piece = None
        self.valid_moves = {}
        self.turn = 'red'
        self.red_team = red_team
        self.black_team = black_team
        self.red_image = red_image
        self.black_image = black_image
        self.difficulty = difficulty
        self.setup_board()
        self.game_over = False
        self.winner = None
        self.animating_pieces = []  # Lista para controlar peças em animação
        
        self.menu_button = Button(20, 20, 150, 40, "Voltar ao Menu", 25)

    def setup_board(self):
        self.board = []
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    if row < 3:
                        self.board[row].append(Piece(row, col, "black", self.black_image))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, "red", self.red_image))
                    else:
                        self.board[row].append(None)
                else:
                    self.board[row].append(None)

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if self.menu_button.is_clicked(mouse_pos, event):
                if 'menu' in SOUNDS: SOUNDS['menu'].play()
                return "menu"
                
            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and self.turn == 'red' and not self.animating_pieces:
                pos = pygame.mouse.get_pos()
                col = int(pos[0] // SQUARE_SIZE)
                row = int(pos[1] // SQUARE_SIZE)
                
                if 0 <= row < ROWS and 0 <= col < COLS:
                    piece = self.board[row][col]
                    if piece and piece.team == 'red':
                        self.selected_piece = piece
                        self.valid_moves = self.get_valid_moves(piece)
                    elif self.selected_piece and (row, col) in self.valid_moves:
                        self.move_piece(self.selected_piece, row, col)
        
        self.menu_button.check_hover(mouse_pos)
        
        return True

    def move_piece(self, piece, row, col):
        # Atualiza posição alvo
        piece.target_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
        piece.target_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
        piece.animating = True
        self.animating_pieces.append(piece)
        
        # Verifica captura
        capture_pos = self.valid_moves.get((row, col))
        if capture_pos:
            cap_row, cap_col = capture_pos
            self.board[cap_row][cap_col] = None
            if 'capture' in SOUNDS: SOUNDS['capture'].play()
        else:
            if 'move' in SOUNDS: SOUNDS['move'].play()
        
        # Atualiza tabuleiro
        self.board[piece.row][piece.col] = None
        piece.row, piece.col = row, col
        self.board[row][col] = piece
        
        # Verifica se virou dama
        if (piece.team == 'red' and row == 0) or (piece.team == 'black' and row == ROWS-1):
            piece.king = True
            if 'win' in SOUNDS: SOUNDS['win'].play()
        
        self.turn = 'black' if self.turn == 'red' else 'red'
        self.selected_piece = None
        self.valid_moves = {}
        
        self.check_game_over()
        
        if self.turn == 'black' and not self.game_over:
            self.ai_move()

    def ai_move(self):
        pygame.time.delay(500 // self.difficulty)
        
        black_pieces = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece and piece.team == 'black':
                    black_pieces.append(piece)
        
        all_moves = {}
        for piece in black_pieces:
            moves = self.get_valid_moves(piece)
            if moves:
                all_moves[piece] = moves
        
        if all_moves:
            piece = random.choice(list(all_moves.keys()))
            move = random.choice(list(all_moves[piece].keys()))
            self.move_piece(piece, move[0], move[1])

    def get_valid_moves(self, piece):
        moves = {}
        directions = []
        
        if piece.team == 'red' or piece.king:
            directions.extend([(-1, -1), (-1, 1)])
        if piece.team == 'black' or piece.king:
            directions.extend([(1, -1), (1, 1)])
        
        for dr, dc in directions:
            r, c = piece.row + dr, piece.col + dc
            if 0 <= r < ROWS and 0 <= c < COLS:
                if self.board[r][c] is None:
                    moves[(r, c)] = None
                elif self.board[r][c].team != piece.team:
                    r2, c2 = r + dr, c + dc
                    if 0 <= r2 < ROWS and 0 <= c2 < COLS and self.board[r2][c2] is None:
                        moves[(r2, c2)] = (r, c)
        return moves

    def check_game_over(self):
        red_pieces = 0
        black_pieces = 0
        
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece:
                    if piece.team == 'red':
                        red_pieces += 1
                    else:
                        black_pieces += 1
        
        if red_pieces == 0:
            self.game_over = True
            self.winner = 'black'
            if 'win' in SOUNDS: SOUNDS['win'].play()
        elif black_pieces == 0:
            self.game_over = True
            self.winner = 'red'
            if 'win' in SOUNDS: SOUNDS['win'].play()

    def update(self):
        # Atualiza todas as peças em animação
        for piece in self.animating_pieces[:]:
            piece.update()
            if not piece.animating:
                self.animating_pieces.remove(piece)

    def draw(self):
        self.screen.fill(GRAY)
        
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    pygame.draw.rect(self.screen, WHITE, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        
        for row in self.board:
            for piece in row:
                if piece:
                    piece.draw(self.screen, piece == self.selected_piece)
        
        if self.selected_piece:
            for (r, c), capture in self.valid_moves.items():
                pygame.draw.ellipse(self.screen, HIGHLIGHT, (c*SQUARE_SIZE + 20, r*SQUARE_SIZE + 20, SQUARE_SIZE - 40, SQUARE_SIZE - 40))
        
        self.menu_button.draw(self.screen)
        
        font = pygame.font.SysFont('Arial', 24)
        red_text = font.render(f"Você: {self.red_team}", True, RED)
        black_text = font.render(f"Adversário: {self.black_team}", True, BLACK)
        diff_text = font.render(f"Dificuldade: {self.difficulty}", True, BLUE)
        
        self.screen.blit(red_text, (20, HEIGHT - 80))
        self.screen.blit(black_text, (20, HEIGHT - 50))
        self.screen.blit(diff_text, (WIDTH - 200, HEIGHT - 50))
        
        if self.game_over:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            self.screen.blit(s, (0, 0))
            
            font = pygame.font.SysFont('Arial', 50)
            winner = "VOCÊ VENCEU!" if self.winner == 'red' else "VOCÊ PERDEU!"
            color = RED if self.winner == 'red' else BLACK
            text = font.render(winner, True, color)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
            
            font = pygame.font.SysFont('Arial', 30)
            restart = font.render("Clique para voltar ao menu", True, WHITE)
            self.screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 20))
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            
            if running == "menu":
                return "menu"
                
            self.update()
            self.draw()
            self.clock.tick(60)

def main():
    while True:
        menu = Menu()
        game_settings = menu.run()
        
        game = DamasGame(
            game_settings['red_team'],
            game_settings['black_team'],
            game_settings['red_image'],
            game_settings['black_image'],
            game_settings['difficulty']
        )
        
        result = game.run()
        
        if result != "menu":
            break

if __name__ == '__main__':
    main()
    pygame.quit()
    sys.exit()