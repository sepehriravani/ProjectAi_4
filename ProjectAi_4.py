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

    def is_valid_move(self, start, end):
        if self.board[start][1] != self.player or self.board[start][0] == 0:
            return False
        if self.board[end][1] not in [self.player, None] and self.board[end][0] > 1:
            return False
        return True

    def make_move(self, start, end):
        self.move_history.append((start, end, self.board[start][:], self.board[end][:]))
        self.board[start][0] -= 1
        if self.board[start][0] == 0:
            self.board[start][1] = None

        if self.board[end][1] not in [self.player, None]:
            opponent = "white" if self.player == "black" else "black"
            self.board[end][0] = 1
            self.board[end][1] = self.player
        else:
            self.board[end][0] += 1
            self.board[end][1] = self.player
