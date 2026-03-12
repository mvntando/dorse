# Universal Chess Interface (UCI) Protocol
import sys
from dorse import Position
import utils
from search import Searcher

INIT_BOARD, WC, BC, EP, SD = utils.parse_fen(utils.START_POS)

def print_id():
    print("id name Dorse")
    print("id author MV")
    print("id country Bulawayo")

def print_options():
    # Engine options
    pass

def uci_loop():
    searcher = Searcher()
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
            # Reset any internal state for a new game
            searcher = Searcher()

        elif line.startswith("position"):
            position = parse_position(line)

        elif line.startswith("go"):
            if position is None:
                print("bestmove 0000")
                continue

            depth: int | None = None
            tokens = line.split()
            if "depth" in tokens:
                try:
                    depth_index = tokens.index("depth")
                    depth = int(tokens[depth_index + 1])
                except (IndexError, ValueError):
                    depth = None

            movetime: float | None = None
            if "movetime" in tokens:
                try:
                    time_index = tokens.index("movetime")
                    movetime = float(tokens[time_index + 1]) / 1000.0  # convert ms to seconds (time module uses seconds)
                except (IndexError, ValueError):
                    movetime = None

            move = searcher.search(position, depth=depth, movetime=movetime)
            if move is None:
                print("bestmove 0000")
                continue

            bestmove_str = f"bestmove {move.uci()}"
            print(bestmove_str)

        elif line == "quit":
            print("")
            break

def parse_position(line: str) -> Position | None:
    tokens = line.split()

    if tokens[1] == "startpos":
        pos = Position([row[:] for row in INIT_BOARD], WC, BC, EP, SD)
        idx = 2
    elif tokens[1] == "fen":
        fen = " ".join(tokens[2:8])
        board, wc, bc, ep, sd = utils.parse_fen(fen)
        pos = Position(board, wc, bc, ep, sd)
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
                raise

    return pos

if __name__ == "__main__":
    uci_loop()
