from copy import deepcopy

# MINIMAX BOT # 

import random
import math

class nMiniMaxBot:
    def __init__(self, game, player_id, n):
        self.game = game
        self.player_id = player_id
        self.bot = self.game.players[self.player_id]
        self.player = self.game.players[1 - self.player_id]
        self.n = n # how many moves ahead we look
        self.stored_states = {}

    def make_move(self):
        # Check if it's the bot's turn
        if self.game.cur_player != self.player_id:
            return False
        self.stored_states = {}
        max_depth = self.n
        best_score, best_move = self.minimax(self.game, max_depth, maximizing_score = True)
        print(best_score)
        self.game.perform_action(self.bot, best_move[0], best_move[1])

    

    def minimax(self, game, depth, maximizing_score):
        if depth == 0 or game.winner:
            return self.heuristic(game, self.bot, self.player), None

        best_score = None
        cur_player = game.players[game.cur_player]
        for action_type, action in self.generate_all_moves():
            if game.perform_action(cur_player, action_type, action):
                gamestate = self.hash_game_state(game)
                if gamestate in self.stored_states:
                    score = self.stored_states[gamestate]
                else:
                    score, _ = self.minimax(game, depth - 1, not maximizing_score)
                    self.stored_states[gamestate] = score
                if maximizing_score and (not best_score or score > best_score):
                    best_score = score
                    best_move = (action_type, action)
                elif not maximizing_score and (not best_score or score < best_score):
                    best_score = score
                    best_move = (action_type, action)
                game.undo_last_move()
        
        return best_score, best_move
    
                
    
    def generate_all_moves(self):
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (-1,-1), (1, -1), (1, 1), (2,0), (-2,0), (0,2), (0,-2)]  # Possible directions
        walls_pos = [(i+1.5, j+1.5) for i in range(8) for j in range(8)]
        for dir in directions:
            yield "move", dir

        for wall_pos in walls_pos:
            yield "wall", (wall_pos, "vertical")
            yield "wall", (wall_pos, "horizontal")



    def heuristic(self, game, bot, player):
        if game.winner == bot.player_id:
            return 10000
        elif game.winner == player.player_id:
            return -10000

        bot_path_len = game.check_path_to_end(bot)[1]
        player_path_len = game.check_path_to_end(player)[1]
        bot_mobility = self.num_legal_moves(game, bot)
        player_mobility = self.num_legal_moves(game, player)
        distance_to_opponent = game.dist(bot.pos, player.pos)
        turns_taken = len(game.actions)

        return (
            -1.5 * bot_path_len * 1.025 ** turns_taken + 2 * player_path_len * 1.05 ** turns_taken # Prioritize reaching the goal and blocking opponent
            + 1 * bot.remaining_walls - 0.5 * player.remaining_walls * 1.025 ** turns_taken # Wall count
            + 0.1 * (bot_mobility - player_mobility)  # Mobility
            - 0.05 * distance_to_opponent  # Distance to opponent
        )
    


    def hash_game_state(self, game):
        # Initialize an empty string
        hash_string = ''

        # Add player positions
        for player in game.players:
            hash_string += f'P{player.player_id}:{player.pos}'

        # Add walls
        for wall in sorted(game.walls):
            hash_string += f'W:{wall}'

        # Add current player
        hash_string += f'Current:{game.cur_player}'

        # Use a hash function (e.g., hash(), md5, etc.)
        return hash(hash_string)  # Simple Python hash function
    


    def num_legal_moves(self, game, player):
        count = 0
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (-1,-1), (1, -1), (1, 1), (2,0), (-2,0), (0,2), (0,-2)]  # Immediate moves only
        wall_positions = self.strategic_wall_positions(player)  # A subset of wall positions

        for dir in directions:
            if game.is_legal_move(player, dir):
                count += 1

        for wall_pos in wall_positions:
            if game.is_legal_wall(player, wall_pos, "vertical", undo_successful_wall=True):
                count += 1
            if game.is_legal_wall(player, wall_pos, "horizontal", undo_successful_wall=True):
                count += 1

        return count

    def strategic_wall_positions(self, player):
        # Example: Return wall positions near the player and along central paths
        x, y = player.pos
        return [(x + dx, y + dy) for dx in range(-1, 2) for dy in range(-1, 2) if 1.5 <= x + dx <= 8.5 and 1.5 <= y + dy <= 8.5]
