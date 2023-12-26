import pygame
import sys

sys.path.append('./Implementation')
from v1 import Game

# Initialize pygame
pygame.init()

# Constants for the game
SCREEN_SIZE = 600
BOARD_SIZE = 9
SQUARE_SIZE = SCREEN_SIZE // BOARD_SIZE
PAWN_SIZE = SQUARE_SIZE // 4
WALL_WIDTH = SQUARE_SIZE // 8
LINE_WIDTH = WALL_WIDTH
WALL_COLOR = (0, 255, 0)  # Bright green color for walls
BACKGROUND_COLOR = (128, 128, 128)  # Gray background
PAWN_COLORS = [(255, 0, 0), (0, 0, 255)]  # Red and Blue for two players
HIGHLIGHT_COLOR = (255, 223, 0)  # Golden color for highlight

# Set up the display
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption('Quoridor Game Visualization')

def draw_frame():
    """Draws the frame around the board."""
    frame_rect = pygame.Rect(0, 0, total_screen_width, FRAME_WIDTH)
    pygame.draw.rect(screen, FRAME_COLOR, frame_rect)
    frame_rect = pygame.Rect(0, FRAME_WIDTH + SCREEN_SIZE, total_screen_width, WALL_SELECTION_SIZE)
    pygame.draw.rect(screen, FRAME_COLOR, frame_rect)
    frame_rect = pygame.Rect(0, 0, FRAME_WIDTH, total_screen_height)
    pygame.draw.rect(screen, FRAME_COLOR, frame_rect)
    frame_rect = pygame.Rect(SCREEN_SIZE + FRAME_WIDTH, 0, FRAME_WIDTH, total_screen_height)
    pygame.draw.rect(screen, FRAME_COLOR, frame_rect)

def draw_selectable_walls():
    """Draws selectable walls below the game board."""
    # Draw horizontal wall
    hor_wall_rect = pygame.Rect(FRAME_WIDTH, SCREEN_SIZE + FRAME_WIDTH + WALL_SELECTION_SIZE // 4, SCREEN_SIZE, WALL_WIDTH)
    pygame.draw.rect(screen, WALL_COLOR, hor_wall_rect)

    # Draw vertical wall
    ver_wall_rect = pygame.Rect(FRAME_WIDTH + WALL_SELECTION_SIZE // 4, SCREEN_SIZE + FRAME_WIDTH + WALL_SELECTION_SIZE // 2, WALL_WIDTH, SCREEN_SIZE)
    pygame.draw.rect(screen, WALL_COLOR, ver_wall_rect)

def draw_board(game):
    """Draws the Quoridor board."""
    screen.fill(BACKGROUND_COLOR)  # Gray background
    for row in range(1, BOARD_SIZE + 1):
        for col in range(1, BOARD_SIZE + 1):
            # Adjust for 1-based indexing of the tiles
            rect = ((col - 1) * SQUARE_SIZE, (row - 1) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, (64, 64, 64), rect, LINE_WIDTH)

def draw_pawns(game):
    """Draws the pawns on the board."""
    pawn_positions = [player.pos for player in game.players]
    for i, pos in enumerate(pawn_positions):
        # Adjust pawn position to be 1-based from the bottom left
        center = ((pos[0] - 1) * SQUARE_SIZE + SQUARE_SIZE // 2,
                  (BOARD_SIZE - pos[1]) * SQUARE_SIZE + SQUARE_SIZE // 2)
        pygame.draw.circle(screen, PAWN_COLORS[i], center, PAWN_SIZE)

def draw_walls(wall_positions):
    """Draws the walls on the board."""
    for wall in game.walls:
        # Calculate wall center position based on 1-based indexing
        center_x = (wall[0][0] - 1.5) * SQUARE_SIZE + SQUARE_SIZE
        center_y = (BOARD_SIZE - wall[0][1] + .5) * SQUARE_SIZE + SQUARE_SIZE // 2 - SQUARE_SIZE // 2
        
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
        center = ((move[0] - 1) * SQUARE_SIZE + SQUARE_SIZE // 2,
                  (BOARD_SIZE - move[1]) * SQUARE_SIZE + SQUARE_SIZE // 2)
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
    center = ((pawn[0] - 1) * SQUARE_SIZE + SQUARE_SIZE // 2,
              (BOARD_SIZE - pawn[1]) * SQUARE_SIZE + SQUARE_SIZE // 2)
    radius = PAWN_SIZE
    distance = ((center[0] - mouse_pos[0]) ** 2 + (center[1] - mouse_pos[1]) ** 2) ** 0.5
    return distance < radius


def main():
    game.perform_action(game.players[0], "wall", ((1.5,2.5), "horizontal"))
    selected_player = None
    legal_moves = []
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for player in game.players:
                    if player.player_id == game.cur_player:
                        pawn_rect = pygame.Rect(
                            (player.pos[0] - 1) * SQUARE_SIZE,
                            (BOARD_SIZE - player.pos[1]) * SQUARE_SIZE,
                            SQUARE_SIZE, SQUARE_SIZE
                        )
                        if pawn_rect.collidepoint(mouse_pos):
                            selected_player = player
                            legal_moves = get_legal_moves(game, player)
                            break
                else:
                    if selected_player:
                        for move in legal_moves:
                            move_rect = pygame.Rect(
                                (move[0] - 1) * SQUARE_SIZE,
                                (BOARD_SIZE - move[1]) * SQUARE_SIZE,
                                SQUARE_SIZE, SQUARE_SIZE
                            )
                            if move_rect.collidepoint(mouse_pos):
                                game.perform_action(selected_player, "move", (move[0] - selected_player.pos[0], move[1] - selected_player.pos[1]))
                                selected_player = None
                                legal_moves = []
                                break

        draw_board(game)
        draw_pawns(game)
        draw_walls(game)
        if legal_moves:
            draw_highlighted_squares(game, legal_moves)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    game = Game()
    main()

