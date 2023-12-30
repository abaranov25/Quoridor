import networkx as nx

class Player():
    def __init__(self, player_id, pos, remaining_walls):
        ''' 
        Creates a helpful wrapper to store player information
        for neater code in the Game class.
        '''
        self.player_id = player_id
        self.pos = pos
        self.remaining_walls = remaining_walls


class Game():
    def __init__(self):
        '''
        Initializes the board, players, and walls for a 
        game of Quoridor. The board is a 9x9 grid where the
        x-axis is horizontal and the y-axis is vertical, and 
        the bottom left corner is (1,1). The players are 
        initialized using instances of the Player class. The 
        walls are stored as a set of tuples for wall positions.
        '''
        # initialize board
        self.graph = nx.Graph()
        for i in range(1,10):
            for j in range(1,10):
                self.graph.add_node((i,j))
                if i > 1:
                    self.graph.add_edge((i,j),(i-1,j))
                if j > 1:
                    self.graph.add_edge((i,j),(i,j-1))

        # initialize players and walls
        self.players = [Player(0, (5,1), 10), Player(1, (5,9), 10)]
        self.walls = set()
        self.cur_player = 0
        self.winner = None
        self.actions = []
        
        

    def perform_action(self, player, action_type, action):
        '''
        Performs an action by updating the state of the game if the
        move is legal. Otherwise, returns False and does not perform
        any move.

        player:         Current player (Player)
        action_type:    Specifies between wall placements or player movement actions (str)
        action:         Provides details on the action. For wall placements, provide the position and 
                        orientation of the wall as ((float, float), str). For player movements, provide
                        the direction as (int, int).
        '''
        if player.player_id != self.cur_player or self.winner != None:
            #print("Player not allowed to move")
            return False
        if action_type == "move":
            dir = action
            if self.is_legal_move(player, dir):
                player.pos = (player.pos[0] + dir[0], player.pos[1] + dir[1])
                #print("Moved player {p} to position ({x},{y})".format(p = player.player_id, x = player.pos[0], y = player.pos[1]))
            else:
                #print("Invalid move for player {p}".format(p = player.player_id))
                return False
        
        elif action_type == "wall":
            pos, orientation = action
            if self.is_legal_wall(player, pos, orientation):
                self.walls.add(action)
                player.remaining_walls -= 1
                #print("{o} wall at ({p0},{p1}) placed successfully.".format(o=orientation, p0=pos[0], p1=pos[1]))
            else:
                #print("Invalid wall placement")
                return False
            
        self.cur_player = 1 - self.cur_player
        self.check_win_condition()
        self.actions.append((action_type, action))
        return True
    


    def undo_last_move(self):
        if self.actions == []:
            #print("No action to undo")
            return False
        if self.winner != None:
            self.winner = None
        action_type, last_action = self.actions.pop(-1)
        self.cur_player = 1 - self.cur_player
        player = self.players[self.cur_player]
        if action_type == "move":
            dir = last_action
            player.pos = (player.pos[0] - dir[0], player.pos[1] - dir[1])
        elif action_type == "wall":
            pos, orientation = last_action
            surrounding_nodes = [(pos[0] - 0.5, pos[1] - 0.5), (pos[0] + 0.5, pos[1] - 0.5), (pos[0] + 0.5, pos[1] + 0.5), (pos[0] - 0.5, pos[1] + 0.5)]
            if orientation == "horizontal":
                connections = ((surrounding_nodes[0], surrounding_nodes[3]), (surrounding_nodes[1], surrounding_nodes[2]))
            elif orientation == "vertical":
                connections = ((surrounding_nodes[0], surrounding_nodes[1]), (surrounding_nodes[2], surrounding_nodes[3]))
            self.graph.add_edge(connections[0][0], connections[0][1])
            self.graph.add_edge(connections[1][0], connections[1][1])
            self.walls.remove((pos, orientation))
            player.remaining_walls += 1
        else:
            #print("Illegal action was previously taken")
            return False
        return True



    def is_legal_move(self, player, dir):
        '''
        Checks if a player's proposed move is in accordance with the 
        rules of Quoridor. Specifically makes sure that the player
        moves within the grid, and deals with edge cases such as being 
        immediately adjacent to an opponent. Used in perform_action.

        player:     Current player (Player)
        dir:        Direction of movement, also can think of it as a 
                    displacement vector (int, int)
        '''
        new_player_pos = (player.pos[0] + dir[0], player.pos[1] + dir[1])
        if new_player_pos not in self.graph.nodes:
            return False
        other_player = self.players[1 - player.player_id]
        if self.dist(player.pos, new_player_pos) == 1:
            return new_player_pos != other_player.pos and self.graph.has_edge(player.pos, new_player_pos)

        elif self.dist(player.pos, new_player_pos) == 2:
            behind_opponent = (2 * other_player.pos[0] - player.pos[0], 2 * other_player.pos[1] - player.pos[1])
            diagonal_right = (other_player.pos[0] + other_player.pos[1] - player.pos[1], 
                             other_player.pos[1] + other_player.pos[0] - player.pos[0])
            diagonal_left = (other_player.pos[0] - other_player.pos[1] + player.pos[1], 
                             other_player.pos[1] - other_player.pos[0] + player.pos[0])
            if not self.graph.has_edge(player.pos, other_player.pos):
                return False
            if self.graph.has_edge(other_player.pos, behind_opponent):
                return new_player_pos == behind_opponent
            elif behind_opponent[0] in list(range(1,10)) and behind_opponent[1] in list(range(1,10)):
                if new_player_pos == diagonal_right:
                    return self.graph.has_edge(other_player.pos, diagonal_right) 
                elif new_player_pos == diagonal_left:
                    return self.graph.has_edge(other_player.pos, diagonal_left)   
            return False
        else:
            return False
        


    def is_legal_wall(self, player, pos, orientation, undo_successful_wall = False):
        '''
        Checks if a wproposed wall from a player is in accordance
        with the rules of Quoridor. Specifically makes sure that
        the wall does not overlap with other walls and is fully on 
        the board, as well as checks to see that the proposed wall
        does not prevent either player from escaping.

        player:         Current player (Player)
        pos:            Position of center of wall (float, float)
        orientation:    Specified horizontal or vertical wall (str)
        '''
        if player.remaining_walls == 0:
            return False

        allowed_pos = [x + 0.5 for x in list(range(1,10))]
        if pos[0] not in allowed_pos or pos[1] not in allowed_pos or (pos, "horizontal") in self.walls or (pos, "vertical") in self.walls:
            return False

        surrounding_nodes = [(pos[0] - 0.5, pos[1] - 0.5), (pos[0] + 0.5, pos[1] - 0.5), (pos[0] + 0.5, pos[1] + 0.5), (pos[0] - 0.5, pos[1] + 0.5)]
        if orientation == "horizontal":
            connections = ((surrounding_nodes[0], surrounding_nodes[3]), (surrounding_nodes[1], surrounding_nodes[2]))
        elif orientation == "vertical":
            connections = ((surrounding_nodes[0], surrounding_nodes[1]), (surrounding_nodes[2], surrounding_nodes[3]))
        else:
            return False
        
        if connections[0] not in self.graph.edges or connections[1] not in self.graph.edges:
            return False
        self.graph.remove_edge(connections[0][0], connections[0][1])
        self.graph.remove_edge(connections[1][0], connections[1][1])
        legal = self.check_path_to_end(self.players[0])[0] and self.check_path_to_end(self.players[1])[0]
        if not legal or undo_successful_wall:
            self.graph.add_edge(connections[0][0], connections[0][1])
            self.graph.add_edge(connections[1][0], connections[1][1])
        return legal



    def check_win_condition(self):
        '''
        Checks to see if either player has made it to
        the other side of the board.
        '''
        if self.players[0].pos[1] == 9:
            self.winner = 0
            return True
        elif self.players[1].pos[1] == 1:
            self.winner = 1
            return True
        else:
            return False
        


    def check_path_to_end(self, player): # BUG: DOESNT TAKE INTO ACCOUNT DOUBLE HOPS
        '''
        Uses BFS to determine whether a certain player
        can make it to the other side of the board given
        current wall placements. Returns True if the
        player can, and False if the player can not. 

        player:     Current player (Player)
        '''
        goal_row = 9 - 8 * player.player_id
        visited = set(player.pos,)
        queue = [player.pos]
        lens = [0]
        while len(queue) > 0:
            cur = queue.pop(0)
            path_len = lens.pop(0)
            for neighbor in self.graph.neighbors(cur):
                if neighbor[1] == goal_row:
                    return True, path_len
                elif neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)
                    lens.append(path_len + 1)
        return False, None



    def dist(self, pos1, pos2): 
        ''' 
        Calculates the Manhattan distance between two points

        pos1:   First position (int, int)
        pos2:   Second position (int, int)
        '''
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])    