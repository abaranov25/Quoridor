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
        return 10*game.check_path_to_end(player)[1]**0.5 - game.check_path_to_end(bot)[1] + bot.remaining_walls**2 - player.remaining_walls
    


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