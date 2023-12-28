# RANDOM BOT # 

import random
import math

class RandomBot:
    def __init__(self, game, player_id):
        self.game = game
        self.player_id = player_id
        self.bot = self.game.players[self.player_id]

    def make_move(self):
        # Check if it's the bot's turn
        if self.game.cur_player != self.player_id:
            return False
    
        done = False
        while not done:
            if random.choice(["move", "wall"]) == "move":
                done = self.make_move_decision()
            else:
                done = self.make_wall_decision()
        return done

    def make_move_decision(self):
        # Example: Move towards the goal
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (-1,-1), (1, -1), (1, 1), (2,0), (-2,0), (0,2), (0,-2)]  # Possible directions
        direction = random.choice(directions)
        return self.game.perform_action(self.bot, "move", direction)

    def make_wall_decision(self):
        # Example: Place a wall randomly
        wall_position = (math.ceil(8*random.uniform(0, 1))+0.5, math.ceil(8*random.uniform(0, 1))+0.5)
        wall_orientation = random.choice(["horizontal", "vertical"])
        return self.game.perform_action(self.bot, "wall", (wall_position, wall_orientation))