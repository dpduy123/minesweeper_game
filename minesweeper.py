import pygame
import random
import sys
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500
GRID_SIZE = 10
CELL_SIZE = 30
GRID_WIDTH = GRID_SIZE * CELL_SIZE
GRID_HEIGHT = GRID_SIZE * CELL_SIZE
MARGIN_X = (WINDOW_WIDTH - GRID_WIDTH) // 2
MARGIN_Y = (WINDOW_HEIGHT - GRID_HEIGHT) // 2 + 50  # Extra space for UI elements at the top

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
DARK_RED = (128, 0, 0)
DARK_BLUE = (0, 0, 128)
DARK_GREEN = (0, 128, 0)
BROWN = (128, 64, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 128, 128)
YELLOW = (128, 128, 0)

# Number colors
NUMBER_COLORS = {
    1: BLUE,
    2: GREEN,
    3: RED,
    4: DARK_BLUE,
    5: DARK_RED,
    6: DARK_GREEN,
    7: BLACK,
    8: GRAY
}

# Game states
GAME_RUNNING = 0
GAME_WON = 1
GAME_LOST = 2

class Cell:
    def __init__(self):
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0

class Minesweeper:
    def __init__(self, width, height, num_mines):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.mines_left = num_mines
        self.game_state = GAME_RUNNING
        self.first_click = True
        self.start_time = 0
        self.elapsed_time = 0
        self.grid = [[Cell() for _ in range(width)] for _ in range(height)]
        self.font = pygame.font.SysFont('Arial', 18)
        self.large_font = pygame.font.SysFont('Arial', 24, bold=True)
        
    def place_mines(self, first_x, first_y):
        # Place mines randomly, but avoid the first clicked cell and its neighbors
        safe_cells = []
        for y in range(self.height):
            for x in range(self.width):
                # Check if the cell is not the first clicked cell or its neighbors
                if abs(x - first_x) > 1 or abs(y - first_y) > 1:
                    safe_cells.append((x, y))
        
        # Place mines
        mine_positions = random.sample(safe_cells, min(self.num_mines, len(safe_cells)))
        for x, y in mine_positions:
            self.grid[y][x].is_mine = True
        
        # Calculate adjacent mines for each cell
        for y in range(self.height):
            for x in range(self.width):
                if not self.grid[y][x].is_mine:
                    self.grid[y][x].adjacent_mines = self.count_adjacent_mines(x, y)
    
    def count_adjacent_mines(self, x, y):
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx].is_mine:
                    count += 1
        return count
    
    def reveal_cell(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        
        cell = self.grid[y][x]
        
        # If it's the first click, place mines
        if self.first_click:
            self.first_click = False
            self.place_mines(x, y)
            self.start_time = pygame.time.get_ticks()
        
        # Don't reveal flagged cells or already revealed cells
        if cell.is_flagged or cell.is_revealed:
            return
        
        # Reveal the cell
        cell.is_revealed = True
        
        # If it's a mine, game over
        if cell.is_mine:
            self.game_state = GAME_LOST
            return
        
        # If it's a cell with no adjacent mines, reveal neighbors
        if cell.adjacent_mines == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    self.reveal_cell(x + dx, y + dy)
        
        # Check if the game is won
        self.check_win()
    
    def toggle_flag(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        
        cell = self.grid[y][x]
        
        # Can't flag revealed cells
        if cell.is_revealed:
            return
        
        # Toggle flag
        if cell.is_flagged:
            cell.is_flagged = False
            self.mines_left += 1
        else:
            cell.is_flagged = True
            self.mines_left -= 1
    
    def check_win(self):
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                # If there's a non-mine cell that's not revealed, the game is not won yet
                if not cell.is_mine and not cell.is_revealed:
                    return
        
        # All non-mine cells are revealed, game is won
        self.game_state = GAME_WON
    
    def reveal_all_mines(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x].is_mine:
                    self.grid[y][x].is_revealed = True
    
    def reset_game(self):
        self.__init__(self.width, self.height, self.num_mines)

def main():
    # Set up the window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Minesweeper')
    
    # Create game instance
    game = Minesweeper(GRID_SIZE, GRID_SIZE, 15)  # 15 mines
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            if game.game_state == GAME_RUNNING:
                if event.type == MOUSEBUTTONDOWN:
                    # Get mouse position and convert to grid coordinates
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x = (mouse_x - MARGIN_X) // CELL_SIZE
                    grid_y = (mouse_y - MARGIN_Y) // CELL_SIZE
                    
                    # Left click to reveal cell
                    if event.button == 1:
                        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                            game.reveal_cell(grid_x, grid_y)
                    
                    # Right click to flag cell
                    elif event.button == 3:
                        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                            game.toggle_flag(grid_x, grid_y)
            
            # Reset game with R key
            if event.type == KEYDOWN and event.key == K_r:
                game.reset_game()
        
        # Update game time if game is running
        if game.game_state == GAME_RUNNING and not game.first_click:
            game.elapsed_time = (pygame.time.get_ticks() - game.start_time) // 1000
        
        # Draw the game
        screen.fill(WHITE)
        
        # Draw UI elements
        # Timer
        timer_text = game.font.render(f"Time: {game.elapsed_time}", True, BLACK)
        screen.blit(timer_text, (20, 20))
        
        # Mines left
        mines_text = game.font.render(f"Mines: {game.mines_left}", True, BLACK)
        screen.blit(mines_text, (WINDOW_WIDTH - 100, 20))
        
        # Game state message
        if game.game_state == GAME_WON:
            message = game.large_font.render("You Win!", True, GREEN)
            screen.blit(message, (WINDOW_WIDTH // 2 - 50, 20))
            game.reveal_all_mines()
        elif game.game_state == GAME_LOST:
            message = game.large_font.render("Game Over!", True, RED)
            screen.blit(message, (WINDOW_WIDTH // 2 - 60, 20))
            game.reveal_all_mines()
        
        # Draw grid
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell = game.grid[y][x]
                rect = pygame.Rect(
                    MARGIN_X + x * CELL_SIZE,
                    MARGIN_Y + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                
                # Draw cell background
                if cell.is_revealed:
                    pygame.draw.rect(screen, WHITE, rect)
                else:
                    pygame.draw.rect(screen, GRAY, rect)
                
                # Draw cell border
                pygame.draw.rect(screen, BLACK, rect, 1)
                
                # Draw cell content
                if cell.is_revealed:
                    if cell.is_mine:
                        # Draw mine
                        pygame.draw.circle(
                            screen,
                            BLACK,
                            rect.center,
                            CELL_SIZE // 3
                        )
                    elif cell.adjacent_mines > 0:
                        # Draw number
                        number_text = game.font.render(
                            str(cell.adjacent_mines),
                            True,
                            NUMBER_COLORS.get(cell.adjacent_mines, BLACK)
                        )
                        text_rect = number_text.get_rect(center=rect.center)
                        screen.blit(number_text, text_rect)
                elif cell.is_flagged:
                    # Draw flag
                    pygame.draw.polygon(
                        screen,
                        RED,
                        [
                            (rect.centerx - CELL_SIZE // 4, rect.centery - CELL_SIZE // 4),
                            (rect.centerx + CELL_SIZE // 4, rect.centery - CELL_SIZE // 8),
                            (rect.centerx - CELL_SIZE // 4, rect.centery)
                        ]
                    )
                    pygame.draw.line(
                        screen,
                        BLACK,
                        (rect.centerx - CELL_SIZE // 4, rect.centery - CELL_SIZE // 4),
                        (rect.centerx - CELL_SIZE // 4, rect.centery + CELL_SIZE // 4),
                        2
                    )
        
        # Draw reset instructions
        reset_text = game.font.render("Press R to reset", True, BLACK)
        screen.blit(reset_text, (WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT - 30))
        
        # Update the display
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
