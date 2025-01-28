from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import random

# تنظیم یک seed برای ثابت نگه داشتن نتیجه تاس‌ها در اجراهای مختلف
random.seed(42)

class BackgammonBase(ABC):
    @abstractmethod
    def get_possible_sequences(self, dice_roll: List[int]) -> List[List[Tuple[int, int]]]:
        pass

    @abstractmethod
    def make_move(self, move: Tuple[int, int]) -> None:
        pass

    @abstractmethod
    def undo_move(self, move: Tuple[int, int]) -> None:
        pass

    @abstractmethod
    def is_bear_off_possible(self) -> bool:
        pass

    @abstractmethod
    def evaluate_board(self) -> int:
        pass

class Backgammon(BackgammonBase):
    def __init__(self) -> None:
        # تعریف تخته بازی شامل 24 نقطه، هر نقطه شامل تعداد مهره‌ها و رنگ بازیکن است
        self.board: List[Tuple[int, Optional[str]]] = [[0, None] for _ in range(24)]
        # نگهداری مهره‌های گرفته شده هر بازیکن
        self.bar: dict = {"white": 0, "black": 0}
        # شمارش مهره‌هایی که هر بازیکن خارج کرده است
        self.bear_off: dict = {"white": 0, "black": 0}
        # بازیکن فعلی (سفید یا سیاه)
        self.current_player: str = "white"
        # مقداردهی اولیه تخته بازی
        self.initialize_board()
        # تاریخچه حرکات بازی
        self.move_history: List = []

    def initialize_board(self) -> None:
        """مقداردهی اولیه تخته با تنظیمات استاندارد بازی تخته نرد."""
        self.board[0] = [2, "white"]
        self.board[11] = [5, "white"]
        self.board[16] = [3, "white"]
        self.board[18] = [5, "white"]
        self.board[23] = [2, "black"]
        self.board[12] = [5, "black"]
        self.board[7] = [3, "black"]
        self.board[5] = [5, "black"]

    def get_possible_sequences(self, dice_roll: List[int]) -> List[List[Tuple[int, int]]]:
        """تعیین تمام توالی‌های ممکن حرکت‌ها با توجه به مقادیر تاس."""
        sequences = []
        for dice in dice_roll:
            for start in range(len(self.board)):
                # محاسبه نقطه مقصد با توجه به جهت حرکت بازیکن
                end = start + dice if self.current_player == "white" else start - dice
                if 0 <= end < len(self.board) and self.is_valid_move(start, end):
                    sequences.append([(start, end)])
        return sequences

    def is_valid_move(self, start: int, end: int) -> bool:
        """بررسی صحت یک حرکت خاص بر اساس قوانین بازی."""
        # بررسی اینکه نقطه شروع متعلق به بازیکن فعلی باشد
        if self.board[start][1] != self.current_player or self.board[start][0] == 0:
            return False
        # بررسی اینکه نقطه مقصد برای بازیکن مجاز باشد
        if self.board[end][1] not in [self.current_player, None] and self.board[end][0] > 1:
            return False
        return True

    def make_move(self, move: Tuple[int, int]) -> None:
        """انجام یک حرکت و به‌روزرسانی وضعیت تخته."""
        start, end = move
        # ذخیره وضعیت قبل از حرکت در تاریخچه
        self.move_history.append((start, end, self.board[start][:], self.board[end][:]))
        # کاهش تعداد مهره‌ها در نقطه شروع
        self.board[start][0] -= 1
        if self.board[start][0] == 0:
            self.board[start][1] = None

        # بررسی و مدیریت زدن مهره حریف در نقطه مقصد
        if self.board[end][1] not in [self.current_player, None]:
            opponent = "white" if self.current_player == "black" else "black"
            self.bar[opponent] += 1
            self.board[end][0] = 1
            self.board[end][1] = self.current_player
        else:
            self.board[end][0] += 1
            self.board[end][1] = self.current_player

    def undo_move(self, move: Tuple[int, int]) -> None:
        """بازگرداندن آخرین حرکت انجام‌شده و بازگشت وضعیت تخته."""
        last_move = self.move_history.pop()
        start, end = last_move[0], last_move[1]
        self.board[start] = last_move[2]
        self.board[end] = last_move[3]

    def is_bear_off_possible(self) -> bool:
        """بررسی امکان خارج کردن مهره‌ها برای بازیکن فعلی."""
        if self.current_player == "white":
            return all(pos == self.current_player or count == 0 for count, pos in self.board[:18])
        else:
            return all(pos == self.current_player or count == 0 for count, pos in self.board[6:])

    def evaluate_board(self) -> int:
        """محاسبه امتیاز وضعیت تخته بر اساس موقعیت مهره‌ها."""
        score = 0
        for i, (count, player) in enumerate(self.board):
            if player == self.current_player:
                score += count * (24 - i if self.current_player == "white" else i)
            elif player is not None:
                score -= count * (24 - i if self.current_player == "white" else i)
        return score

    def alpha_beta_pruning(self, depth: int, alpha: float, beta: float, maximizing_player: bool) -> int:
        """پیاده‌سازی الگوریتم Alpha-Beta Pruning برای ارزیابی بهترین حرکت."""
        if depth == 0 or self.is_game_over():
            return self.evaluate_board()

        if maximizing_player:
            max_eval = -float("inf")
            for dice1 in range(1, 7):
                for dice2 in range(1, 7):
                    dice_roll = [dice1, dice2]
                    probability = 1 / 36  # احتمال هر ترکیب تاس
                    for sequence in self.get_possible_sequences(dice_roll):
                        for move in sequence:
                            self.make_move(move)
                            eval = self.alpha_beta_pruning(depth - 1, alpha, beta, False)
                            self.undo_move(move)
                            max_eval = max(max_eval, eval * probability)  # اعمال احتمال
                            alpha = max(alpha, eval)
                            if beta <= alpha:
                                break
            return max_eval
        else:
            min_eval = float("inf")
            for dice1 in range(1, 7):
                for dice2 in range(1, 7):
                    dice_roll = [dice1, dice2]
                    probability = 1 / 36  # احتمال هر ترکیب تاس
                    for sequence in self.get_possible_sequences(dice_roll):
                        for move in sequence:
                            self.make_move(move)
                            eval = self.alpha_beta_pruning(depth - 1, alpha, beta, True)
                            self.undo_move(move)
                            min_eval = min(min_eval, eval * probability)  # اعمال احتمال
                            beta = min(beta, eval)
                            if beta <= alpha:
                                break
            return min_eval

    def roll_dice(self) -> List[int]:
        """انداختن دو تاس و بازگرداندن نتیجه."""
        return [random.randint(1, 6), random.randint(1, 6)]

    def is_game_over(self) -> bool:
        """بررسی پایان بازی."""
        return self.bear_off["white"] == 15 or self.bear_off["black"] == 15

    def is_maximizing(self) -> bool:
        """بررسی اینکه آیا بازیکن فعلی بیشینه‌ساز است یا خیر."""
        return self.current_player == "white"

    def change_player(self) -> None:
        """تغییر بازیکن فعلی."""
        self.current_player = "black" if self.current_player == "white" else "white"

    def play_turn(self) -> None:
        """اجرای یک نوبت برای بازیکن فعلی."""
        dice_roll = self.roll_dice()
        print(f"{self.current_player} rolls: {dice_roll}")
        move_sequences = self.get_possible_sequences(dice_roll)

        if not move_sequences:
            print(f"{self.current_player} cannot move. Passing turn.")
            self.change_player()  # انتقال نوبت به بازیکن بعدی
            return

        best_eval = -float("inf") if self.is_maximizing() else float("inf")
        best_sequence = None

        for sequence in move_sequences:
            for move in sequence:
                self.make_move(move)
            eval = self.alpha_beta_pruning(3, -float("inf"), float("inf"), not self.is_maximizing())  # عمق ۳
            for move in reversed(sequence):
                self.undo_move(move)

            if (self.is_maximizing() and eval > best_eval) or (not self.is_maximizing() and eval < best_eval):
                best_eval = eval
                best_sequence = sequence

        if best_sequence:
            for move in best_sequence:
                self.make_move(move)
                print(f"{self.current_player} moves: {move}")


