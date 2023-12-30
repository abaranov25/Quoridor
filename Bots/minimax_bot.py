from copy import deepcopy

# MINIMAX BOT # 

import random
import math

class MiniMaxBot:
    def __init__(self, game, player_id):
        self.game = game
        self.player_id = player_id
        self.bot = self.game.players[self.player_id]
        self.player = self.game.players[1 - self.player_id]

    def make_move(self):
        # Check if it's the bot's turn
        if self.game.cur_player != self.player_id:
            return False

        max_min_max_h = None
        best_move = None
        for move in self.generate_all_legal_moves(self.game, self.bot):
            self.game.perform_action(self.bot, move[0], move[1])
            min_max_h = None
            for response in self.generate_all_legal_moves(self.game, self.player):
                self.game.perform_action(self.player, response[0], response[1])
                max_h = None
                for next_move in self.generate_all_legal_moves(self.game, self.bot):
                    self.game.perform_action(self.bot, next_move[0], next_move[1])
                    x = self.heuristic(self.game, self.bot, self.player)
                    if max_h == None or max_h < x:
                        max_h = x
                    self.game.undo_last_move()
                if min_max_h == None or min_max_h > max_h:
                    min_max_h = max_h
                self.game.undo_last_move()
            if max_min_max_h == None or (max_min_max_h < min_max_h):
                best_move = move
                max_min_max_h = min_max_h
            self.game.undo_last_move()
        print(max_min_max_h)
        
        self.game.perform_action(self.bot, best_move[0], best_move[1])
                
    
    def generate_all_legal_moves(self, game, player):
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (-1,-1), (1, -1), (1, 1), (2,0), (-2,0), (0,2), (0,-2)]  # Possible directions
        walls_pos = [(i+1.5, j+1.5) for i in range(8) for j in range(8)]
        for dir in directions:
            if game.is_legal_move(player, dir):
                yield "move", dir

        for wall_pos in walls_pos:
            if game.is_legal_wall(player, wall_pos, "vertical", undo_successful_wall = True):
                yield "wall", (wall_pos, "vertical")
            if game.is_legal_wall(player, wall_pos, "horizontal", undo_successful_wall = True):
                yield "wall", (wall_pos, "horizontal")

    def heuristic(self, game, bot, player):
        return game.check_path_to_end(player)[1]**2 - game.check_path_to_end(bot)[1] + abs(bot.remaining_walls - player.remaining_walls) ** 1.5