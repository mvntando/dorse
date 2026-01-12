# Universal Chess Interface (UCI) Protocol
import sys
from dorse import Position
import utils

INIT_BOARD, WC, BC, EP_SQ, SD = utils.parse_fen(utils.START_POS)

def print_id():
    print("id name Dorse")
    print("id author MV")

def print_options():
    # Add engine options here if needed
    pass

def uci_loop():
    position = None

    while True:
        try:
            line = input().strip()
        except EOFError:
            break

        if not line:
            continue

        if line == "uci":
            print_id()
            print_options()
            print("uciok")

        elif line == "isready":
            print("readyok")

        elif line == "ucinewgame":
            # Always start fresh
            position = Position(INIT_BOARD.copy(), 0, WC, BC, EP_SQ, SD)

        elif line.startswith("position"):
            position = parse_position(line)

        elif line.startswith("go"):
            if position is None:
                print("bestmove 0000")
                continue

            move = position.search()
            if move is None:
                print("bestmove 0000")
                continue

            # Convert internal coordinates to UCI format
            src = chr(ord('a') + move.src[1]) + str(move.src[0] + 1)
            dst = chr(ord('a') + move.dst[1]) + str(move.dst[0] + 1)
            promo = move.promo.lower() if move.promo else ""

            bestmove_str = f"bestmove {src}{dst}{promo}"
            print(bestmove_str)

        elif line == "quit":
            break


def parse_position(line):
    tokens = line.split()

    if tokens[1] == "startpos":
        pos = Position(INIT_BOARD.copy(), 0, WC, BC, EP_SQ, SD)
        idx = 2
    elif tokens[1] == "fen":
        fen = " ".join(tokens[2:8])
        board, wc, bc, ep, sd = utils.parse_fen(fen)
        pos = Position(board, 0, wc, bc, ep, sd)
        idx = 8
    else:
        return None

    # Replay moves if present
    if idx < len(tokens) and tokens[idx] == "moves":
        for uci_move in tokens[idx + 1:]:
            try:
                pos.make_uci_move(uci_move)
            except Exception as e:
                print(f"[ERROR] Illegal move {uci_move}: {e}", file=sys.stderr)

    return pos

if __name__ == "__main__":
    uci_loop()
    