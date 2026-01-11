import dorse, utils
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

BOARD = utils.parse_fen(utils.START_POS)[0]
pos = dorse.Position(BOARD, 0, (1, 1), (1, 1), None, 'w')

# Choose your side
human_side = 'w'  # change to 'b' if you want Black

def move_to_str(move):
    """Convert a Move object into a string like 'e2e4' or 'e7e8q'"""
    return utils.square(move.src) + utils.square(move.dst) + (move.promo)

def print_board(board):
    """
    Prints the board with:
    - ranks 8 → 1 on the left
    - files a → h at the bottom
    Assumes board[0][0] == a1
    """
    for rank in range(7, -1, -1):
        print(f"{rank + 1} ", end="")
        for file in range(8):
            print(board[rank][file], end=" ")
        print()

    print("  a b c d e f g h")

last_move_str = None

def print_state(pos, last_move):
    print()
    print(f"Side to move : {'White' if pos.sd == 'w' else 'Black'}")
    print(f"Score        : {pos.score}")
    print(f"White castle : Q={pos.wc[0]}  K={pos.wc[1]}")
    print(f"Black castle : Q={pos.bc[0]}  K={pos.bc[1]}")
    print(f"En passant   : {utils.square(pos.ep) if pos.ep else '-'}")

    if last_move:
        print(f"Last move    : {last_move}")

    print()

while True:
    clear_screen()

    print_board(pos.board)
    print_state(pos, last_move_str)

    if pos.sd == human_side:
        user_input = input("Your move (eg: e2e4, e7e8q): ").strip()

        if len(user_input) not in (4, 5):
            input("Invalid input format. Press Enter to continue.")
            continue

        moves = pos.gen_moves()
        if not (len(moves)): print("Game over."); break
        moves_str = [move_to_str(m) for m in moves]

        if user_input not in moves_str:
            input("Illegal move. Press Enter to continue.")
            continue

        for m in moves:
            if move_to_str(m) == user_input:
                pos.move(m)
                last_move_str = f"White: {move_to_str(m)}"
                break

    else:
        move = pos.play()
        if move:
            last_move_str = f"Black: {move_to_str(move)}"
        else:
            print("Game over.")
            break
