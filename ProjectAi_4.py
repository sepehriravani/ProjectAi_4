class Backgammon:
    def __init__(self, board, dice_rolls, player):
        self.board = board
        self.dice_rolls = dice_rolls
        self.player = player
        self.move_history = []

    def get_possible_sequences(self):
        sequences = []
        for dice in self.dice_rolls:
            for start in range(len(self.board)):
                end = start + dice if self.player == "white" else start - dice
                if 0 <= end < len(self.board) and self.is_valid_move(start, end):
                    sequences.append([(start, end)])
        return sequences

   