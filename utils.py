# Zobrist hashing and board utilities
import random

_rng = random.Random(0)  # isolated, deterministic RNG

def rand64():
    return _rng.getrandbits(64)

# 12 pieces × 64 squares
# 1 side-to-move key
# 4 castling keys
# 8 ep file keys
PIECE_KEYS = [[rand64() for _ in range(64)] for _ in range(12)]
SIDE_KEY = rand64()  # if is white
CASTLE_KEYS = [rand64() for _ in range(4)]  # KQkq
EP_KEYS = [rand64() for _ in range(8)]  # ep file a-h

PIECE_INDEX = {
    "P": 0, "N": 1, "B": 2, "R": 3, "Q": 4, "K": 5,
    "p": 6, "n": 7, "b": 8, "r": 9, "q": 10, "k": 11
}


WHITE = 1
BLACK = -1

# Board integer representation (white = +ve, black = -ve)
EMPTY  = 0
PAWN   = 1
KNIGHT = 2
BISHOP = 3
ROOK   = 4
QUEEN  = 5
KING   = 6

# Initial chess board setup
START_POS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# Parse FEN string into board representation and game state
def parse_fen(fen: str) -> tuple[list[list[str]], tuple[int, int], tuple[int, int], tuple[int, int] | None, int]:
    parts = fen.split()
    if len(parts) < 4:
        raise ValueError("Invalid FEN")
    board_part, side, castling, ep = parts[:4]
    board: list[list[str]] = []
    # FEN ranks: 8 → 1
    for fen_rank, row in enumerate(board_part.split('/')):
        board.append(['.'] * 8)  # <-- Create the row first
        file = 0
        for ch in row:
            if ch.isdigit():
                file += int(ch)
            else:
                board[fen_rank][file] = ch
                file += 1
        # optional safety check (can remove if you want zero overhead)
        if file != 8:
            raise ValueError("Invalid FEN rank")
    # Flip so board[0][0] == a1 (white side) (cartesian coordinates)
    board = board[::-1]
    # Side to move: keep as 'w' / 'b'
    sd = WHITE if side == 'w' else BLACK
    # Castling rights
    wc = (1 if 'Q' in castling else 0, 1 if 'K' in castling else 0)
    bc = (1 if 'q' in castling else 0, 1 if 'k' in castling else 0)
    # En passant
    if ep == '-':
        ep = None
    else:
        file = ord(ep[0]) - ord('a')
        rank = int(ep[1]) - 1  # rank 1 → index 0
        ep = (rank, file)
    return board, wc, bc, ep, sd

# Lists of possible moves for each piece type
DIRECTIONS = {
    "N":  [(2, 1), (2, -1), (-2, 1), (-2, -1),
           (1, 2), (1, -2), (-1, 2), (-1, -2)],  # Knight
    "B":  [(1, 1), (1, -1), (-1, 1), (-1, -1)],  # Bishop
    "R":  [(1, 0), (-1, 0), (0, 1), (0, -1)],    # Rook
    "Q":  [(1, 0), (-1, 0), (0, 1), (0, -1),
           (1, 1), (1, -1), (-1, 1), (-1, -1)],  # Queen
    "K":  [(1, 0), (-1, 0), (0, 1), (0, -1),
           (1, 1), (1, -1), (-1, 1), (-1, -1)],  # King
    "P":  [(1, 0)],  # White pawn (moves up the board)
    "p":  [(-1, 0)], # Black pawn (moves down the board)

    "P_capture":  [(1, 1), (1, -1)],    # White pawn captures diagonally up
    "p_capture":  [(-1, 1), (-1, -1)],  # Black pawn captures diagonally down
}

# Sliding pieces
SLIDING = {"B", "R", "Q"}

# Precompute attack patterns for knights, kings, pawns rays for sliding pieces
KNIGHT_ATTACKS = [[] for _ in range(64)]
for r in range(8):
    for c in range(8):
        sq = r*8 + c
        for dr, dc in DIRECTIONS['N']:
            rr, cc = r + dr, c + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                KNIGHT_ATTACKS[sq].append((rr, cc))

KING_ATTACKS = [[] for _ in range(64)]
for r in range(8):
    for c in range(8):
        sq = r*8 + c
        for dr, dc in DIRECTIONS['K']:
            rr, cc = r + dr, c + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                KING_ATTACKS[sq].append((rr, cc))

PAWN_ATTACKS = {
    'w': [[] for _ in range(64)],
    'b': [[] for _ in range(64)]
}
for r in range(8):
    for c in range(8):
        sq = r*8 + c

        # white pawns
        for dr, dc in DIRECTIONS['P_capture']:
            rr, cc = r + dr, c + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                PAWN_ATTACKS['w'][sq].append((rr, cc))

        # black pawns
        for dr, dc in DIRECTIONS['p_capture']:
            rr, cc = r + dr, c + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                PAWN_ATTACKS['b'][sq].append((rr, cc))

BISHOP_RAYS = [[] for _ in range(64)]
for r in range(8):
    for c in range(8):
        sq = r*8 + c

        rays = []

        for dr, dc in DIRECTIONS['B']:
            ray = []
            rr, cc = r + dr, c + dc

            while 0 <= rr < 8 and 0 <= cc < 8:
                ray.append((rr, cc))
                rr += dr
                cc += dc

            rays.append(ray)

        BISHOP_RAYS[sq] = rays

ROOK_RAYS = [[] for _ in range(64)]
for r in range(8):
    for c in range(8):
        sq = r*8 + c

        rays = []

        for dr, dc in DIRECTIONS['R']:
            ray = []
            rr, cc = r + dr, c + dc

            while 0 <= rr < 8 and 0 <= cc < 8:
                ray.append((rr, cc))
                rr += dr
                cc += dc

            rays.append(ray)

        ROOK_RAYS[sq] = rays

# Check if square is attacked by opponent's pieces
def attacked(pos, sq: tuple[int, int], opponent: int) -> bool:
    r, c = sq
    board = pos.board
    s = r*8 + c

    if opponent == WHITE:
        pawn, knight, king = 'P', 'N', 'K'
        pawn_table = PAWN_ATTACKS['b']  # reverse lookup
        rook, bishop, queen = 'R', 'B', 'Q'
    else:
        pawn, knight, king = 'p', 'n', 'k'
        pawn_table = PAWN_ATTACKS['w']
        rook, bishop, queen = 'r', 'b', 'q'

    # --- Pawn attacks ---
    for rr, cc in pawn_table[s]:
        if board[rr][cc] == pawn:
            return True

    # --- Knight attacks ---
    for rr, cc in KNIGHT_ATTACKS[s]:
        if board[rr][cc] == knight:
            return True

    # --- King attacks ---
    for rr, cc in KING_ATTACKS[s]:
        if board[rr][cc] == king:
            return True

    # --- Sliding attacks ---
    for ray in ROOK_RAYS[s]:  # rook/queen
        for rr, cc in ray:
            piece = board[rr][cc]
            if piece == '.':
                continue
            if piece == rook or piece == queen:
                return True
            break  # blocked

    for ray in BISHOP_RAYS[s]:  # bishop/queen
        for rr, cc in ray:
            piece = board[rr][cc]
            if piece == '.':
                continue
            if piece == bishop or piece == queen:
                return True
            break  # blocked

    return False