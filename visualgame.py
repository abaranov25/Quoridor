import pygame
import sys

sys.path.append('./Implementation')
from v1 import Game

# Initialize pygame
pygame.init()

# Constants for the game
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 800 
BOARD_LEN = 600
BOARD_OFFSET_X = (SCREEN_WIDTH - BOARD_LEN) // 2  # Horizontally centered
BOARD_OFFSET_Y = 50  # Closer to the top
BOARD_SIZE = 9
SQUARE_SIZE = BOARD_LEN // BOARD_SIZE
PAWN_SIZE = SQUARE_SIZE // 4
WALL_WIDTH = SQUARE_SIZE // 8
LINE_WIDTH = WALL_WIDTH
FRAME_WIDTH = 50  # Width of the frame around the board
WALL_COLOR = (0, 255, 0)  # Bright green color for walls
BACKGROUND_COLOR = (140, 140, 140)  # Gray background
PAWN_COLORS = [(255, 0, 0), (0, 0, 255)]  # Red and Blue for two players
HIGHLIGHT_COLOR = (255, 223, 0)  # Golden color for highlight
WALL_SELECTION_AREA_HEIGHT = 100  # Height for the wall selection area
SELECTED_WALL_COLOR = (255, 255, 0)  # Color for the selected wall
wall_selected = None  # Keep track of the selected wall
potential_wall_positions = []  # Keep track of potential positions for placing the wall


# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Quoridor Game Visualization')


def draw_board(game):
    """Draws the Quoridor board."""
    screen.fill(BACKGROUND_COLOR)  # Gray background
    for row in range(1, BOARD_SIZE + 1):
        for col in range(1, BOARD_SIZE + 1):
            # Adjust for 1-based indexing of the tiles
            rect = ((col - 1) * SQUARE_SIZE + BOARD_OFFSET_X, (row - 1) * SQUARE_SIZE + BOARD_OFFSET_Y, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, (60, 60, 60), rect, LINE_WIDTH)

def draw_wall_counters(game):
    """Displays the number of walls each player has left."""
    font = pygame.font.Font(None, 36)

    # Player 1 Wall Counter
    p1_counter_rect = pygame.Rect(BOARD_OFFSET_X, 0, 50, 50)
    pygame.draw.circle(screen, PAWN_COLORS[0], p1_counter_rect.center, p1_counter_rect.width // 3)
    p1_counter_text = font.render(f'x{game.players[0].remaining_walls}', True, (0, 0, 0))
    screen.blit(p1_counter_text, (p1_counter_rect.x + 60, p1_counter_rect.y + 15))

    # Player 2 Wall Counter
    p2_counter_rect = pygame.Rect(BOARD_OFFSET_X + BOARD_LEN - 50, 0, 50, 50)
    pygame.draw.circle(screen, PAWN_COLORS[1], p2_counter_rect.center, p2_counter_rect.width // 3)
    p2_counter_text = font.render(f'x{game.players[1].remaining_walls}', True, (0, 0, 0))
    screen.blit(p2_counter_text, (p2_counter_rect.x - 50, p2_counter_rect.y + 15))


def draw_selectable_walls():
    """Draws buttons for selecting horizontal and vertical walls."""
    font = pygame.font.Font(None, 36)
    button_height = WALL_SELECTION_AREA_HEIGHT // 2

    # Horizontal Wall Button
    hor_button_rect = pygame.Rect(BOARD_OFFSET_X, SCREEN_HEIGHT - WALL_SELECTION_AREA_HEIGHT, BOARD_LEN // 4, button_height)
    pygame.draw.rect(screen, (120,0,120), hor_button_rect)
    hor_text = font.render('Horizontal', True, (255, 255, 255))
    screen.blit(hor_text, (hor_button_rect.x + 14, hor_button_rect.y + 13))

    # Vertical Wall Button
    ver_button_rect = pygame.Rect(SCREEN_WIDTH - BOARD_OFFSET_X - BOARD_LEN // 4, SCREEN_HEIGHT - WALL_SELECTION_AREA_HEIGHT, BOARD_LEN // 4, button_height)
    pygame.draw.rect(screen, (120,0,120), ver_button_rect)
    ver_text = font.render('Vertical', True, (255, 255, 255))
    screen.blit(ver_text, (ver_button_rect.x + 28, ver_button_rect.y + 13))

def highlight_potential_wall_positions(potential_wall_positions):
    """Highlights potential positions for placing the selected wall."""
    circle_radius = SQUARE_SIZE // 8  # Radius of the circle
    for pos in potential_wall_positions:
        # Calculate the center position of the intersection on the screen
        screen_x = (pos[0] - 1) * SQUARE_SIZE + BOARD_OFFSET_X + SQUARE_SIZE
        screen_y = (BOARD_SIZE - pos[1]) * SQUARE_SIZE + BOARD_OFFSET_Y

        # Draw an unfilled circle at each potential wall position
        pygame.draw.circle(screen, SELECTED_WALL_COLOR, (screen_x, screen_y), circle_radius, 3)

def get_potential_wall_positions(game):
    """Calculates potential positions for placing the selected wall."""
    positions = []
    for i in range(1, BOARD_SIZE):
        for j in range(1, BOARD_SIZE):
            if ((i, j), 'horizontal') not in game.walls and ((i, j), 'vertical') not in game.walls:
                positions.append((i, j))
    return positions

def is_wall_selected(mouse_pos):
    """
    Checks if a selectable wall area is clicked.

    Args:
    mouse_pos (tuple): The position of the mouse click.

    Returns:
    bool: True if a wall area is clicked, False otherwise.
    """
    # Check if the mouse click is within either of the wall selection areas
    return horizontal_wall_rect.collidepoint(mouse_pos) or vertical_wall_rect.collidepoint(mouse_pos)

def is_move_clicked(move, mouse_pos):
    move_rect = pygame.Rect(
        (move[0] - 1) * SQUARE_SIZE + BOARD_OFFSET_X,
        (BOARD_SIZE - move[1]) * SQUARE_SIZE + BOARD_OFFSET_Y,
        SQUARE_SIZE, SQUARE_SIZE
    )
    return move_rect.collidepoint(mouse_pos)

def draw_pawns(game):
    """Draws the pawns on the board."""
    pawn_positions = [player.pos for player in game.players]
    for i, pos in enumerate(pawn_positions):
        # Adjust pawn position to be 1-based from the bottom left
        center = ((pos[0] - 1) * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_OFFSET_X,
                  (BOARD_SIZE - pos[1]) * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_OFFSET_Y)
        pygame.draw.circle(screen, PAWN_COLORS[i], center, PAWN_SIZE)

def draw_walls(wall_positions):
    """Draws the walls on the board."""
    for wall in game.walls:
        # Calculate wall center position based on 1-based indexing
        center_x = (wall[0][0] - 1.5) * SQUARE_SIZE + SQUARE_SIZE + BOARD_OFFSET_X
        center_y = (BOARD_SIZE - wall[0][1] + .5) * SQUARE_SIZE + SQUARE_SIZE // 2 - SQUARE_SIZE // 2 + BOARD_OFFSET_Y
        
        if wall[1] == 'horizontal':
            # Draw horizontal wall centered on the line
            x = center_x - SQUARE_SIZE + LINE_WIDTH
            y = center_y - WALL_WIDTH // 2
            pygame.draw.rect(screen, WALL_COLOR, (x, y, 2 * SQUARE_SIZE - 2*LINE_WIDTH, WALL_WIDTH))
        elif wall[1] == 'vertical':
            # Draw vertical wall centered on the line
            x = center_x - WALL_WIDTH // 2
            y = center_y - SQUARE_SIZE + LINE_WIDTH
            pygame.draw.rect(screen, WALL_COLOR, (x, y, WALL_WIDTH, 2 * SQUARE_SIZE - 2 * LINE_WIDTH))

def draw_highlighted_squares(pawn, legal_moves):
    """Highlights legal move squares for the selected pawn."""
    for move in legal_moves:
        center = ((move[0] - 1) * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_OFFSET_X,
                  (BOARD_SIZE - move[1]) * SQUARE_SIZE + SQUARE_SIZE // 2+ BOARD_OFFSET_Y)
        pygame.draw.circle(screen, HIGHLIGHT_COLOR, center, PAWN_SIZE)

def get_legal_moves(game, player):
    """Gets the legal moves for the selected player."""
    legal_moves = []
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (-1,-1), (1, -1), (1, 1), (2,0), (-2,0), (0,2), (0,-2)]  # Possible directions
    for d in directions:
        if game.is_legal_move(player, d):
            new_pos = (player.pos[0] + d[0], player.pos[1] + d[1])
            legal_moves.append(new_pos)
    return legal_moves

def is_pawn_clicked(pawn, mouse_pos):
    """Checks if a pawn is clicked."""
    center = ((pawn[0] - 1) * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_OFFSET_X,
              (BOARD_SIZE - pawn[1]) * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_OFFSET_Y)
    radius = PAWN_SIZE
    distance = ((center[0] - mouse_pos[0]) ** 2 + (center[1] - mouse_pos[1]) ** 2) ** 0.5
    return distance < radius


def main():
    selected_player = None
    selected_wall = None
    legal_moves = []
    potential_wall_positions = []
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                button_height = WALL_SELECTION_AREA_HEIGHT // 2
                hor_button_rect = pygame.Rect(BOARD_OFFSET_X, SCREEN_HEIGHT - WALL_SELECTION_AREA_HEIGHT, BOARD_LEN // 4, button_height)
                ver_button_rect = pygame.Rect(SCREEN_WIDTH - BOARD_OFFSET_X - BOARD_LEN // 4, SCREEN_HEIGHT - WALL_SELECTION_AREA_HEIGHT, BOARD_LEN // 4, button_height)
                if hor_button_rect.collidepoint(mouse_pos):
                    selected_wall = 'horizontal'
                    potential_wall_positions = get_potential_wall_positions(game)
                    selected_player = None
                    legal_moves = []
                elif ver_button_rect.collidepoint(mouse_pos):
                    selected_wall = 'vertical'
                    potential_wall_positions = get_potential_wall_positions(game)
                    selected_player = None
                    legal_moves = []
                elif selected_wall:
                    # Check for wall placement
                    circle_radius = SQUARE_SIZE // 8
                    for pos in potential_wall_positions:
                        screen_x = (pos[0] - 1) * SQUARE_SIZE + BOARD_OFFSET_X + SQUARE_SIZE
                        screen_y = (BOARD_SIZE - pos[1]) * SQUARE_SIZE + BOARD_OFFSET_Y
                        wall_rect = pygame.Rect(screen_x - circle_radius, screen_y - circle_radius, circle_radius * 2, circle_radius * 2)
                        if wall_rect.collidepoint(mouse_pos):
                            pos = (pos[0] + 0.5, pos[1] + 0.5)
                            if game.perform_action(game.players[game.cur_player], "wall", (pos, selected_wall)):
                                selected_wall = None
                                potential_wall_positions = []
                                break
                    selected_wall = None
                    potential_wall_positions = []

                else:
                    # Check for pawn movement
                    for player in game.players:
                        if player.player_id == game.cur_player:
                            if is_pawn_clicked(player.pos, mouse_pos):
                                selected_player = player
                                legal_moves = get_legal_moves(game, player)
                                break
                    else:
                        if selected_player:
                            for move in legal_moves:
                                if is_move_clicked(move, mouse_pos):
                                    game.perform_action(selected_player, "move", (move[0] - selected_player.pos[0], move[1] - selected_player.pos[1]))
                                    selected_player = None
                                    legal_moves = []
                                    break

        draw_board(game)
        draw_pawns(game)
        draw_walls(game)
        draw_selectable_walls()
        draw_wall_counters(game)
        if legal_moves:
            draw_highlighted_squares(game, legal_moves)
        if potential_wall_positions:
            highlight_potential_wall_positions(potential_wall_positions)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    game = Game()
    main()

    

if __name__ == "__main__":
    game = Game()
    main()

