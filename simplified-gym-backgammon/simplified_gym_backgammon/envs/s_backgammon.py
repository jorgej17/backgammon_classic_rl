import numpy as np
from collections import namedtuple
import itertools
import random

WHITE = 0
BLACK = 1
NUM_POINTS = 10
TOKEN = {WHITE: "O", BLACK: "X"}
COLORS = {WHITE: "White", BLACK: "Black"}

BackgammonState = namedtuple('BackgammonState', ['board', 'off', 'players_positions'])

def init_board():
    board = [([0 for i in range(3)], None)] * NUM_POINTS
    # BLACK
    board[0] = ([1, 0, 0], BLACK)
    board[3] = ([1, 1, 0], BLACK)
    board[6] = ([1, 1, 1], BLACK)
    # WHITE
    board[2] = ([1, 1, 1], WHITE)
    board[5] = ([1, 1, 0], WHITE)
    board[8] = ([1, 0, 0], WHITE)

    return board

def get_opponent_color(current_player):
    return WHITE if current_player is BLACK else BLACK

class Simplified_Backgammon:
    def __init__(self):
        self.board = init_board()
        self.off = [[0 for i in range(6)], [0 for i in range(6)]]
        self.players_home_positions = {WHITE: [6, 7, 8], BLACK: [0, 1, 2]}
        self.players_positions = self.get_players_positions()
        self.state = self.save_state()

    def get_players_positions(self):
        player_positions = [[], []]
        for key, (checkers, player) in enumerate(self.board):
            if player is not None and key not in player_positions:
                player_positions[player].append(key)
        return player_positions

    def save_state(self):
        return BackgammonState(self.board, self.off, self.players_positions)

    def is_valid(self, player, target):
        if 0 <= target < NUM_POINTS - 1:
            return sum(self.board[target][0]) < 2 or (sum(self.board[target][0]) < 3 and self.board[target][1] == player)
        return False

    def find_available_spot(self, player):
        spots = None
        if player == WHITE:
            # Home is 6, 7, 8
            spots = reversed(range(9))
        else:
            # Home is 0, 1, 2
            spots = range(9)

        for spot in spots:
            print(f"Checking spot {spot}")
            if self.is_valid(player, spot):
                return spot
        
        print("Did not find available spot")
        return None

    def add_checker(self, src, player):
        if self.board[src][0] == [0, 0, 0]:
            self.board[src] = ([1, 0, 0], player)
        elif self.board[src][0] == [1, 0, 0]:
            self.board[src] = ([1, 1, 0], player)
        elif self.board[src][0] == [1, 1, 0]:
            self.board[src] = ([1, 1, 1], player)
        else:
            print(f"ERROR: Too many checkers at {src}, terminating")
            exit(1)

    def remove_checker(self, src, player):
        if self.board[src][0] == [1, 0, 0]:
            self.board[src] = ([0, 0, 0], None)
        elif self.board[src][0] == [1, 1, 0]:
            self.board[src] = ([1, 0, 0], player)
        elif self.board[src][0] == [1, 1, 1]:
            self.board[src] = ([1, 1, 0], player)
        else:
            print(f"ERROR: Too few checkers at {src}, terminating")
            exit(1)

    def move_knocked_player(self, player):
        available_spot = self.find_available_spot(player)
        if self.board[available_spot][1] == None:
            self.add_checker(available_spot, player)
        elif self.board[available_spot][1] == player:
            self.add_checker(available_spot, player)
        elif self.board[available_spot][1] != player and sum(self.board[available_spot][0]) < 2:
            self.move_knocked_player(self.board[available_spot][1])
            self.add_checker(available_spot, player)


    def execute_play(self, current_player, action):
        if action:
            tmp = self.board[:]
            knocked_checkers_count = 0
            for move in action:
                src, target = move
                if 0 <= target < NUM_POINTS:
                    checkers_on_target, player_on_target = self.board[target]
                    if current_player != player_on_target and player_on_target is not None and sum(checkers_on_target) < 2:
                        knocked_checkers_count += 1
                        self.remove_checker(target, player_on_target)
                        self.add_checker(9, player_on_target)

                    self.remove_checker(src, current_player)
                    self.add_checker(target, current_player)
                    
            for _ in range(knocked_checkers_count):
                self.execute_play(get_opponent_color(current_player), [(9, self.find_available_spot(get_opponent_color(current_player)))])
            self.players_positions = self.get_players_positions()

    
    def get_normal_plays(self, player, roll):
        # Generate normal legal plays (not bear off moves)
        plays = set()

        positions = self.players_positions[player]
        combinations_positions = set(itertools.combinations(positions, 2))

        for s in positions:
            if sum(self.board[s][0]) > 1:
                combinations_positions.add((s, s))

            if self.is_valid(player, s + roll[0]) and self.is_valid(player, s + roll[0] + roll[1]):
                plays.add(((s, s + roll[0]), (s + roll[0], s + roll[0] + roll[1])))

            if self.is_valid(player, s + roll[1]) and self.is_valid(player, s + roll[0] + roll[1]):
                plays.add(((s, s + roll[1]), (s + roll[1], s + roll[0] + roll[1])))

        for (s1, s2) in combinations_positions:
            t1 = s1 + roll[0]
            t2 = s1 + roll[1]
            t3 = s2 + roll[0]
            t4 = s2 + roll[1]
            t_far1 = s1 + roll[0] + roll[1]
            t_far2 = s2 + roll[0] + roll[1]

            if self.is_valid(player, t1) and self.is_valid(player, t4):
                plays.add(((s1, t1), (s2, t4)))

            if s1 != s2 and self.is_valid(player, t2) and self.is_valid(player, t3):  # if (s1 == s2) => (target1 == target3 and target2 == target4). Same move as before, but swapped
                plays.add(((s1, t2), (s2, t3)))

            if self.is_valid(player, t1) and self.is_valid(player, t_far1):
                plays.add(((s1, t1), (t1, t_far1)))

            if self.is_valid(player, t2) and self.is_valid(player, t_far1):
                plays.add(((s1, t2), (t2, t_far1)))

            if s1 != s2 and self.is_valid(player, t3) and self.is_valid(player, t_far2):  # if (s1 == s2) => (target_far1 == target_far2)
                plays.add(((s2, t3), (t3, t_far2)))

            if s1 != s2 and self.is_valid(player, t4) and self.is_valid(player, t_far2):  # if (s1 == s2) => (target_far1 == target_far2)
                plays.add(((s2, t4), (t4, t_far2)))

        if len(plays) == 0:
            r = min(roll) if player == WHITE else max(roll)
            single_moves = self.get_single_moves(player, r)

            if len(single_moves) == 0:
                # get the other roll
                r = max(roll) if player == WHITE else min(roll)
                single_moves = self.get_single_moves(player, r)

            for move in single_moves:
                plays.add((move,))

        return [list(play) for play in plays]

    def get_normal_plays_double(self, player, roll):
        plays = set()
        r = roll[0]

        sources = {
            1: [p for p in self.players_positions[player] if sum(self.board[p][0]) > 0],
            2: [p for p in self.players_positions[player] if sum(self.board[p][0]) > 1],
            3: [p for p in self.players_positions[player] if sum(self.board[p][0]) > 2],
            4: [p for p in self.players_positions[player] if sum(self.board[p][0]) > 3],
        }

        combo2 = set(itertools.combinations(sources[1], 2))
        combo3 = set(itertools.combinations(sources[1], 3))

        for s1 in sources[4]:
            if self.is_valid(player, s1 + r):
                plays.add(((s1, s1 + r), (s1, s1 + r), (s1, s1 + r), (s1, s1 + r)))

        for s1 in sources[3]:
            if self.is_valid(player, s1 + r):
                plays.add(((s1, s1 + r), (s1, s1 + r), (s1, s1 + r)))

                for s2 in sources[1]:
                    if s1 != s2 and self.is_valid(player, s2 + r):
                        plays.add(((s1, s1 + r), (s1, s1 + r), (s1, s1 + r), (s2, s2 + r)))

                target_far = s1 + r + r
                if self.is_valid(player, target_far):
                    plays.add(((s1, s1 + r), (s1, s1 + r), (s1, s1 + r), (s1 + r, target_far)))

        for s1 in sources[2]:
            if self.is_valid(player, s1 + r):
                plays.add(((s1, s1 + r), (s1, s1 + r)))

                for (s2, s3) in combo2:
                    if s1 != s2 and s1 != s3 and self.is_valid(player, s2 + r) and self.is_valid(player, s3 + r):
                        plays.add(((s1, s1 + r), (s1, s1 + r), (s2, s2 + r), (s3, s3 + r)))

                for s2 in sources[2]:
                    if s1 != s2 and self.is_valid(player, s2 + r):
                        plays.add(((s1, s1 + r), (s1, s1 + r), (s2, s2 + r), (s2, s2 + r)))

                for s2 in sources[1]:
                    if s1 != s2 and self.is_valid(player, s2 + r):
                        plays.add(((s1, s1 + r), (s1, s1 + r), (s2, s2 + r)))

                        target_far = s1 + r + r
                        if self.is_valid(player, target_far):
                            plays.add(((s1, s1 + r), (s1, s1 + r), (s1 + r, target_far), (s2, s2 + r)))

                        target_far = s2 + r + r
                        if self.is_valid(player, target_far):
                            plays.add(((s1, s1 + r), (s1, s1 + r), (s2, s2 + r), (s2 + r, target_far)))

                target_far = s1 + r + r
                if self.is_valid(player, target_far):
                    plays.add(((s1, s1 + r), (s1, s1 + r), (s1 + r, target_far), (s1 + r, target_far)))

                    target_far2 = s1 + r + r + r
                    if self.is_valid(player, target_far2):
                        plays.add(((s1, s1 + r), (s1, s1 + r), (s1 + r, target_far), (target_far, target_far2)))

        for s1 in sources[1]:
            if self.is_valid(player, s1 + r):
                plays.add(((s1, s1 + r),))

                target_far1 = s1 + r + r
                target_far2 = s1 + r + r + r
                target_far3 = s1 + r + r + r + r

                if self.is_valid(player, target_far1):
                    plays.add(((s1, s1 + r), (s1 + r, target_far1)))

                    if self.is_valid(player, target_far2):
                        plays.add(((s1, s1 + r), (s1 + r, target_far1), (target_far1, target_far2)))

                        if self.is_valid(player, target_far3):
                            plays.add(((s1, s1 + r), (s1 + r, target_far1), (target_far1, target_far2), (target_far2, target_far3)))

                        for s2 in sources[1]:
                            if s2 != s1 and self.is_valid(player, s2 + r):
                                plays.add(((s1, s1 + r), (s1 + r, target_far1), (target_far1, target_far2), (s2, s2 + r)))

                    for s2 in sources[1]:
                        if s1 != s2 and self.is_valid(player, s2 + r):
                            plays.add(((s1, s1 + r), (s1 + r, target_far1), (s2, s2 + r)))

                            s2_target_far1 = s2 + r + r

                            if self.is_valid(player, s2_target_far1):
                                plays.add(((s1, s1 + r), (s1 + r, target_far1), (s2, s2 + r), (s2 + r, s2_target_far1)))

                for s2 in sources[1]:
                    if s1 != s2 and self.is_valid(player, s2 + r):
                        plays.add(((s1, s1 + r), (s2, s2 + r)))

                for (s2, s3, s4) in combo3:
                    if s1 != s2 and s1 != s3 and s1 != s4 \
                            and self.is_valid(player, s2 + r) and self.is_valid(player, s3 + r) and self.is_valid(player, s4 + r):
                        plays.add(((s1, s1 + r), (s2, s2 + r), (s3, s3 + r), (s4, s4 + r)))

                for (s2, s3) in combo2:
                    if s1 != s2 and s1 != s3 and self.is_valid(player, s2 + r) and self.is_valid(player, s3 + r):
                        plays.add(((s1, s1 + r), (s2, s2 + r), (s3, s3 + r)))

                        if self.is_valid(player, target_far1):
                            plays.add(((s1, s1 + r), (s1 + r, target_far1), (s2, s2 + r), (s3, s3 + r)))
        return [list(play) for play in plays]
    def get_single_moves(self, player, roll, other_move_target=None, player_src=None):
        if player_src is not None:
            moves = set((s, s + roll) for s in player_src if self.is_valid(player, s + roll))
        else:
            moves = set((s, s + roll) for s in list(self.players_positions[player]) if self.is_valid(player, s + roll))

        if other_move_target is not None and self.is_valid(player, other_move_target + roll):
            moves.add((other_move_target, other_move_target + roll))

        return moves

    def get_double_moves(self, player, roll, single_moves):
        moves = set()
        if len(single_moves) > 0:
            moves = set(((s, t), (t, t + roll)) for (s, t) in single_moves if self.is_valid(player, t + roll))
            moves.update(list(itertools.combinations(single_moves, 2)))
            moves.update([((s, t), (s, t)) for (s, t) in single_moves if self.board[s][0] >= 2])
        return moves

    def get_triple_moves(self, player, roll, double_moves):
        moves = set()
        reverse = player == WHITE
        if len(double_moves) > 0:
            for (m1, m2) in double_moves:
                s1, t1 = m1
                s2, t2 = m2

                if self.is_valid(player, t1 + roll) and ((t1 != s2) or (self.board[t1][0] > 0 and self.board[t1][1] == player)):
                    moves.add((m1, (t1, t1 + roll), m2))

                if self.is_valid(player, t2 + roll) and (t2 != s1):
                    moves.add((m1, m2, (t2, t2 + roll)))

                for s in self.players_positions[player]:
                    t = s + roll
                    if self.is_valid(player, t):
                        if (self.board[s][0] > 2 and ((s, t) == m1 or (s, t) == m2)) or ((s, t) != m1 and (s, t) != m2):
                            moves.add((m1, m2, (s, t)))

                        if (m1 != m2) and self.board[s][0] > 1 and ((s, t) == m1 or (s, t) == m2):
                            moves.add((m1, m2, (s, t)))

        moves = set(tuple(sorted(play, reverse=reverse)) for play in moves)
        return moves 


game = Simplified_Backgammon()

agent = random.choice([WHITE, BLACK])

for i in range(5):
    print(game.board)
    roll = (random.randint(1, 3), random.randint(1, 3)) if agent == BLACK else (-random.randint(1, 3), -random.randint(1, 3))
    plays = None
    if roll[0] == roll[1]:
        plays = game.get_normal_plays_double(agent, roll)
    else:
        plays = game.get_normal_plays(agent, roll)
    print(roll)
    print(agent)
    print()
    if len(plays) > 0:
        play = random.choice(plays)
        print(play)
        game.execute_play(agent, play)
    agent = get_opponent_color(agent)