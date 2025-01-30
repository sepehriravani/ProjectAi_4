from abstract import Backgammon  # استفاده از کلاس استاد
from typing import List, Tuple, Optional
import random

random.seed(42)

class MyBackgammon(Backgammon):
    def make_move(self, move: Tuple[int, int]) -> None:
        """اجرای یک حرکت و بررسی خروج مهره‌ها."""
        start, end = move

        # **بررسی امکان خروج مهره‌ها**
        if self.is_bear_off_possible():
            if (self.current_player == "white" and end >= 24) or (self.current_player == "black" and end < 0):
                self.bear_off[self.current_player] += 1
                self.board[start][0] -= 1
                if self.board[start][0] == 0:
                    self.board[start][1] = None
                return

        # حرکت عادی
        self.move_history.append((start, end, self.board[start][:], self.board[end][:]))
        self.board[start][0] -= 1
        if self.board[start][0] == 0:
            self.board[start][1] = None

        if self.board[end][1] not in [self.current_player, None]:
            opponent = "white" if self.current_player == "black" else "black"
            self.bar[opponent] += 1
            self.board[end][0] = 1
            self.board[end][1] = self.current_player
        else:
            self.board[end][0] += 1
            self.board[end][1] = self.current_player

    def undo_move(self, move: Tuple[int, int]) -> None:
        """بازگرداندن حرکت."""
        last_move = self.move_history.pop()
        start, end = last_move[0], last_move[1]
        self.board[start] = last_move[2]
        self.board[end] = last_move[3]

    def is_bear_off_possible(self) -> bool:
        """بررسی امکان خروج مهره‌ها."""
        if self.current_player == "white":
            return all(self.board[i][1] == "white" or self.board[i][0] == 0 for i in range(18, 24))
        else:
            return all(self.board[i][1] == "black" or self.board[i][0] == 0 for i in range(0, 6))

    def evaluate_board(self) -> int:
        """محاسبه امتیاز وضعیت تخته."""
        score = 0
        for i, (count, player) in enumerate(self.board):
            if player == self.current_player:
                score += count * (24 - i if self.current_player == "white" else i)
            elif player is not None:
                score -= count * (24 - i if self.current_player == "white" else i)
        return score

    def get_possible_sequences(self, dice_roll: List[int]) -> List[List[Tuple[int, int]]]:
        """تعیین توالی‌های ممکن حرکت‌ها."""
        sequences = []
        for dice in dice_roll:
            for start in range(len(self.board)):
                end = start + dice if self.current_player == "white" else start - dice
                if 0 <= end < len(self.board) and self.is_valid_move(start, end):
                    sequences.append([(start, end)])
        return sequences

    def is_valid_move(self, start: int, end: int) -> bool:
        """بررسی صحت یک حرکت خاص."""
        if self.board[start][1] != self.current_player or self.board[start][0] == 0:
            return False
        if self.board[end][1] not in [self.current_player, None] and self.board[end][0] > 1:
            return False
        return True

    def alpha_beta_pruning(self, depth: int, alpha: float, beta: float, maximizing_player: bool) -> int:
        """پیاده‌سازی الگوریتم آلفا-بتا پرونینگ."""
        if depth == 0 or self.is_game_over():
            return self.evaluate_board()

        if maximizing_player:
            max_eval = -float("inf")
            for dice1 in range(1, 7):
                for dice2 in range(1, 7):
                    dice_roll = [dice1, dice2]
                    for sequence in self.get_possible_sequences(dice_roll):
                        for move in sequence:
                            self.make_move(move)
                            eval = self.alpha_beta_pruning(depth - 1, alpha, beta, False)
                            self.undo_move(move)
                            max_eval = max(max_eval, eval)
                            alpha = max(alpha, eval)
                            if beta <= alpha:
                                break
            return max_eval
        else:
            min_eval = float("inf")
            for dice1 in range(1, 7):
                for dice2 in range(1, 7):
                    dice_roll = [dice1, dice2]
                    for sequence in self.get_possible_sequences(dice_roll):
                        for move in sequence:
                            self.make_move(move)
                            eval = self.alpha_beta_pruning(depth - 1, alpha, beta, True)
                            self.undo_move(move)
                            min_eval = min(min_eval, eval)
                            beta = min(beta, eval)
                            if beta <= alpha:
                                break
            return min_eval

    def play_turn(self) -> None:
        """اجرای یک نوبت برای بازیکن فعلی."""
        dice_roll = self.roll_dice()
        print(f"{self.current_player} rolls: {dice_roll}")
        move_sequences = self.get_possible_sequences(dice_roll)

        if not move_sequences:
            print(f"{self.current_player} cannot move. Passing turn.")
            self.change_player()
            return

        best_eval = -float("inf") if self.is_maximizing() else float("inf")
        best_sequence = None

        for sequence in move_sequences:
            for move in sequence:
                self.make_move(move)
            eval = self.alpha_beta_pruning(1, -float("inf"), float("inf"), not self.is_maximizing())
            for move in reversed(sequence):
                self.undo_move(move)

            if (self.is_maximizing() and eval > best_eval) or (not self.is_maximizing() and eval < best_eval):
                best_eval = eval
                best_sequence = sequence

        if best_sequence:
            for move in best_sequence:
                self.make_move(move)
                print(f"{self.current_player} moves: {move}")

    def play_game(self) -> None:
        while not self.is_game_over():
            self.display_board()
            self.play_turn()
            self.change_player()

        winner = "white" if self.bear_off["white"] == 15 else "black"
        print(f"{winner} wins the game!")

# اجرای بازی
if __name__ == "__main__":
    game = MyBackgammon()
    game.play_game()
