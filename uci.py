# Universal Chess Interface (UCI) Protocol
import sys
from dorse import Position
import utils
import search

INIT_BOARD, WC, BC, EP, SD = utils.parse_fen(utils.START_POS)

def print_id():
    print("id name Dorse")
    print("id author MV")
    print("id country Bulawayo")

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
            position = Position([row[:] for row in INIT_BOARD], WC, BC, EP, SD)

        elif line.startswith("position"):
            position = parse_position(line)

        elif line.startswith("go"):
            if position is None:
                print("bestmove 0000")
                continue
            
            depth: int | None = None  # default depth
            tokens = line.split()
            if "depth" in tokens:
                try:
                    depth_index = tokens.index("depth")
                    depth = int(tokens[depth_index + 1])
                except (IndexError, ValueError):
                    depth = None  # fallback to default if parsing fails

            move = search.search(position, depth=depth)
            if move is None:
                print("bestmove 0000")
                continue

            # Convert internal coordinates to UCI format
            src = chr(ord('a') + move.src[1]) + str(move.src[0] + 1)
            dst = chr(ord('a') + move.dst[1]) + str(move.dst[0] + 1)
            promo = move.promo if move.promo else ''

            bestmove_str = f"bestmove {src}{dst}{promo}"
            print(bestmove_str)

        elif line == "quit":
            print("")
            break

def parse_position(line):
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
