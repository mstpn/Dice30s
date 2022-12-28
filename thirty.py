import random

MAX_SCORE = 30
NUM_DICE = 6


class Player:
    def __init__(self, name, human=True):
        self.name = name
        self.score = 30
        self.human = human
        self.active = True
# End of player class


class Dice:
    def __init__(self):
        self.value = 0
        self.in_play = True

    def roll(self) -> int:
        self.value = random.randint(1, 6)
        return self.value
# End of dice class


class Dice_pool:
    def __init__(self):
        self.dice = []
        self.die_available = True
        for i in range(NUM_DICE):
            self.dice.append(Dice())

    def roll_all(self):
        for die in self.dice:
            die.roll()

    def roll_available(self):
        for die in self.dice:
            if die.in_play:
                die.roll()

    def remove_die(self, index: int):
        self.dice[index].in_play = False
        self.check_available()

    def check_available(self) -> bool:
        for die in self.dice:
            if die.in_play:
                self.die_available = True
                return self.die_available
        self.die_available = False
        return self.die_available

    def print_available(self):
        for index, die in enumerate(self.dice):
            if die.in_play:
                print("Die {}: {}".format(index + 1, die.value))

    def highest_available(self) -> int:
        '''
        Returns the highest value of the available dice
        Sets the highest die to not in play
        '''
        highest_value = 0
        for index, die in enumerate(self.dice):
            if die.in_play and die.value > highest_value:
                highest = index
                highest_value = die.value
        self.remove_die(highest)
        self.check_available()
        return highest_value

    def reset_dice(self):
        self.die_available = True
        for die in self.dice:
            die.in_play = True
# End of dice_pool class


class Board:
    def __init__(self):
        self.players = []
        self.num_players = 0
        self.active_players = self.num_players
        self.dice_pool = Dice_pool()
        self.curr_player = 0
        self.next_player = 1
        self.scores = []

    def add_player(self, player: Player = None):
        if player is None:
            name = input("Enter player name: ")
            human = input("Is {} a human player? (y/n): ".format(name))
            if human == "n":
                is_human = False
            self.players.append(Player(name), is_human)
        else:
            self.players.append(player)
        self.num_players += 1
        self.active_players = self.num_players

    def next_turn(self):
        self.curr_player += 1
        if self.curr_player == self.num_players:
            self.curr_player = 0
        self.next_player += 1
        if self.next_player == self.num_players:
            self.next_player = 0

    def update_current_player(self, score_diff: int) -> bool:
        self.players[self.curr_player].score += score_diff
        if self.players[self.curr_player].score <= 0:
            self.players[self.curr_player].active = False
            self.active_players -= 1
            self.players[self.curr_player].score = 0
        return not self.players[self.curr_player].active

    def update_next_player(self, score_diff: int) -> bool:
        self.players[self.next_player].score += score_diff
        if self.players[self.next_player].score <= 0:
            self.players[self.next_player].active = False
            self.active_players -= 1
            self.players[self.next_player].score = 0
        return not self.players[self.next_player].active

    def reset_players(self):
        for player in self.players:
            player.score = 30
            player.active = True
        self.active_players = self.num_players
# End of board class


def check_winner(board: Board) -> Player:
    if board.active_players == 1:
        for player in board.players:
            if player.active:
                return player
    return None


def turn(board: Board) -> Player:
    player = board.players[board.curr_player]
    if not player.active:
        return

    next_player = board.players[board.next_player]
    dice_pool = board.dice_pool
    elim = False
    dice_pool.reset_dice()
    turn_score = 0

    print("It is {}'s turn.".format(player.name))
    for roll_num in range(3):
        turn_score = score_roll(dice_pool, turn_score, roll_num, player.human)
    print("Your score for the turn is: {}".format(turn_score))
    # input()
    attack_num = turn_score - MAX_SCORE
    if attack_num > 0:
        print("You attack {} with {}s!".format(next_player.name, attack_num))
        attack_total = attack(dice_pool, next_player, attack_num)
        elim = board.update_next_player(-attack_total)
        print("After the attack, {} has {} points.".format(
            next_player.name, next_player.score))
    elif attack_num < 0:
        print("You lose {} points!".format(abs(attack_num)))
        elim = board.update_current_player(attack_num)
        print("You now have {} points.".format(player.score))
    else:
        print("You broke even and still have {} points.".format(player.score))

    if elim:
        print("{} is eliminated!".format(next_player.name))
    return check_winner(board)


def attack(dice_pool: Dice_pool, next_player: Player, attack_num: Player) -> bool:
    attack_total = 0
    attack_turn = 1
    dice_pool.reset_dice()

    while dice_pool.die_available:
        print("Attack {}...".format(attack_turn))
        current_attack = attack_roll(dice_pool, next_player, attack_num)
        if current_attack == 0:
            break
        attack_total += current_attack
        print("Hit for {} points!".format(current_attack))
    print("Total attack: {}".format(attack_total))

    return attack_total


def attack_roll(dice_pool: Dice_pool, next_player: Player, attack_num: Player) -> bool:
    attack_total = 0
    dice_pool.roll_available()
    dice_pool.print_available()
    for index, die in enumerate(dice_pool.dice):
        if die.in_play and die.value == attack_num:
            attack_total += attack_num
            dice_pool.remove_die(index)

    return attack_total


def score_roll(dice_pool: Dice_pool, turn_score: int, roll_num: int, human_player: bool):
    if not dice_pool.die_available:
        print("No dice available. Turn score: {}".format(turn_score))
        return turn_score
    print("Roll {}...".format(roll_num + 1))
    dice_pool.roll_available()
    dice_pool.print_available()

    if roll_num < 2:
        if (human_player):
            while True:
                print("Current turn score after {} rolls: {}".format(
                    roll_num, turn_score))
                print("Which dice to save? You must save at least 1 die.")
                save = input()
                at_least_one = False
                for number in save:
                    if number in "123456":
                        at_least_one = True
                        dice_pool.remove_die(int(number)-1)
                        turn_score += dice_pool.dice[int(number) - 1].value
                if at_least_one:
                    break
                else:
                    print("You MUST save at least 1 die.")
        else:
            at_least_one = False
            for index, die in enumerate(dice_pool.dice):
                if die.in_play and die.value >= 5:
                    at_least_one = True
                    dice_pool.remove_die(index)
                    turn_score += die.value
            if not at_least_one:
                turn_score += dice_pool.highest_available()
    else:  # Last roll must keep all dice
        for die in dice_pool.dice:
            if die.in_play:
                turn_score += die.value
    return turn_score


def play_game(board):
    winner = False
    while winner == False:
        winning_player = turn(board)
        if winning_player != None:
            winner = True
        board.next_turn()
    return winning_player


if __name__ == "__main__":
    board = Board()
    play = True

    # Add players
    while True:
        board.add_player()
        another = input("Another player? (y/n): ")
        if another == "n":
            if board.num_players < 2:
                print("You must have at least 2 players.")
            else:
                break

    # Play game
    while play:
        winning_player = play_game(board)
        print("{} wins!".format(winning_player.name))
        play_again = input("Play again? (y/n): ")
        if play_again == "n":
            play = False
        board.reset_players()

    # test 1000 games
    # board.add_player(Player("Player 1", False))
    # board.add_player(Player("Player 2", False))
    # board.add_player(Player("Player 3", False))
    # board.add_player(Player("Player 4", False))
    # for i in range(1000):
    #     winning_player = play_game(board)
    #     print("{} wins!".format(winning_player.name))
    #     board.reset_players()

    print("Thanks for playing!")
