import unittest
from v1 import Game

class TestQuoridorGame(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def test_basic_player_movement(self):
        player = self.game.players[0]
        self.assertTrue(self.game.perform_action(player, "move", (0, 1)))  # Move up
        self.assertEqual(player.pos, (5, 2))

    def test_basic_wall_placement(self):
        p0, p1 = self.game.players
        self.assertTrue(self.game.perform_action(p0, "wall", ((4.5, 8.5), "horizontal")))
        self.assertFalse(self.game.perform_action(p1, "wall", ((4.5, 8.5), "vertical"))) # place a wall on a wall
        self.assertTrue(self.game.perform_action(p1, "wall", ((5.5, 8.5), "vertical")))
        self.assertFalse(self.game.perform_action(p0, "wall", ((5.5, 7.5), "vertical"))) # place a wall that overlaps with a wall
        self.assertFalse(self.game.perform_action(p0, "wall", ((0.5, 0.5), "horizontal")))  # Out of bounds
        self.assertTrue(self.game.perform_action(p0, "wall", ((5.5, 1.5), "vertical")))  # Out of bounds

    def test_wall_blocking_movement(self):
        p0, p1 = self.game.players
        self.game.perform_action(p0, "wall", ((4.5, 8.5), "horizontal"))
        self.assertFalse(self.game.perform_action(p1, "move", (0, -1)))  # Move down into a wall

    def test_wall_blocks_player_from_winning(self):
        p0, p1 = self.game.players
        self.assertTrue(self.game.perform_action(p0, "wall", ((4.5,1.5), "horizontal")))
        self.assertTrue(self.game.perform_action(p1, "wall", ((3.5,1.5), "vertical")))
        self.assertFalse(self.game.perform_action(p0, "wall", ((5.5,1.5), "vertical")))

    def test_win_condition_1(self):
        p0,p1 = self.game.players
        print(p0.pos, p1.pos)
        for i in range(8):
            self.game.perform_action(p0, "move", (0, 1))  # Move right towards the goal
            self.game.perform_action(p1, "move", ((-1)**i,0))
        self.assertEqual(self.game.winner, 0)

    def test_win_condition_2(self):
        p0,p1 = self.game.players
        print(p0.pos, p1.pos)
        self.game.perform_action(p0, "move", (1,0))
        for i in range(8):
            self.game.perform_action(p1, "move", (0, -1))  # Move right towards the goal
            if i < 7: 
                self.game.perform_action(p0, "move", ((-1)**i,0))
        self.assertEqual(self.game.winner, 1)

    def test_illegal_move_out_of_turn(self):
        self.assertFalse(self.game.perform_action(self.game.players[1], "move", (0, 1)))  # Player 1 moving out of turn

    def test_jump_over_opponent_1(self):
        p0,p1 = self.game.players
        # Set up players for jumping
        p0.pos = (5, 4)
        p1.pos = (5, 5)
        self.assertTrue(self.game.perform_action(p0, "move", (0, 2)))  # Attempt to jump over opponent
        self.assertEqual(p0.pos, (5, 6))  # Check if player 0 jumped to the correct position

    def test_diagonal_hopping_2(self):
        # Setup players for diagonal hopping scenario
        p0, p1 = self.game.players
        p0.pos = (2, 2)
        p1.pos = (1, 2)
        self.assertFalse(self.game.perform_action(p0, "move", (-1, -1)))  # Move diagonally

    def test_place_more_than_10_walls(self):
        p0, p1 = self.game.players
        for i in range(10):
            self.assertTrue(self.game.perform_action(p0, "wall", ((1.5 + 2 * (i % 4), 1.5 + (i // 4)), "horizontal")))
            self.game.cur_player = 0
        self.assertFalse(self.game.perform_action(p0, "wall", ((7.5,7.5), "horizontal")))
        self.assertEqual(p0.remaining_walls, 0)  # Player should have 0 walls left

# Create a test suite combining all the test cases
def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestQuoridorGame))
    return test_suite

# Run the tests
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())