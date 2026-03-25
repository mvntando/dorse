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

# Colour constants
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

PROMO_PIECES = {'q': 5, 'r': 4, 'b': 3, 'n': 2}
PROMO = {**PROMO_PIECES, **{v: k for k, v in PROMO_PIECES.items()}}

PIECE_INDEX = {
    PAWN: 0, KNIGHT: 1, BISHOP: 2, ROOK: 3, QUEEN: 4, KING: 5,
    -PAWN: 6, -KNIGHT: 7, -BISHOP: 8, -ROOK: 9, -QUEEN: 10, -KING: 11
}

# Initial chess board setup
START_POS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# Parse FEN string into board representation and game state
def parse_fen(fen: str) -> tuple[list[list[int]], tuple[int, int], tuple[int, int], tuple[int, int] | None, int]:
    parts = fen.split()
    if len(parts) < 4:
        raise ValueError("Invalid FEN")
    board_part, side, castling, ep = parts[:4]
    board: list[list[int]] = []

    fen_map = {
        'P': PAWN,   'N': KNIGHT, 'B': BISHOP, 'R': ROOK,   'Q': QUEEN,  'K': KING,
        'p': -PAWN,  'n': -KNIGHT,'b': -BISHOP, 'r': -ROOK,  'q': -QUEEN, 'k': -KING,
    }

    # FEN ranks: 8 to 1
    for fen_rank, row in enumerate(board_part.split('/')):
        board.append([EMPTY] * 8)  # create the row first
        file = 0
        for ch in row:
            if ch.isdigit():
                file += int(ch)
            else:
                board[fen_rank][file] = fen_map[ch]
                file += 1
        # optional safety check (can remove for zero overhead)
        if file != 8:
            raise ValueError("Invalid FEN rank")
    # Flip so board[0][0] == a1 (white side) (cartesian coordinates)
    board = board[::-1]
    # Side to move
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
    KNIGHT: [(2, 1), (2, -1), (-2, 1), (-2, -1),
           (1, 2), (1, -2), (-1, 2), (-1, -2)],  # Knight
    BISHOP: [(1, 1), (1, -1), (-1, 1), (-1, -1)],  # Bishop
    ROOK:   [(1, 0), (-1, 0), (0, 1), (0, -1)],    # Rook
    QUEEN:  [(1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)],  # Queen
    KING:   [(1, 0), (-1, 0), (0, 1), (0, -1),
           (1, 1), (1, -1), (-1, 1), (-1, -1)],  # King
    PAWN:   [(1, 0)],  # White pawn (moves up the board)
    -PAWN:  [(-1, 0)], # Black pawn (moves down the board)

    "P_cap":  [(1, 1), (1, -1)],    # White pawn captures diagonally up
    "p_cap":  [(-1, 1), (-1, -1)],  # Black pawn captures diagonally down
}

# Sliding pieces
SLIDING = {BISHOP, ROOK, QUEEN}

# Precompute attack patterns for knights, kings, pawns rays for sliding pieces
KNIGHT_ATTACKS = [[] for _ in range(64)]
for r in range(8):
    for c in range(8):
        sq = r*8 + c
        for dr, dc in DIRECTIONS[KNIGHT]:
            rr, cc = r + dr, c + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                KNIGHT_ATTACKS[sq].append((rr, cc))

KING_ATTACKS = [[] for _ in range(64)]
for r in range(8):
    for c in range(8):
        sq = r*8 + c
        for dr, dc in DIRECTIONS[KING]:
            rr, cc = r + dr, c + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                KING_ATTACKS[sq].append((rr, cc))

PAWN_ATTACKS = {
    WHITE: [[] for _ in range(64)],
    BLACK: [[] for _ in range(64)]
}
for r in range(8):
    for c in range(8):
        sq = r*8 + c

        # white pawns
        for dr, dc in DIRECTIONS['P_cap']:
            rr, cc = r + dr, c + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                PAWN_ATTACKS[WHITE][sq].append((rr, cc))

        # black pawns
        for dr, dc in DIRECTIONS['p_cap']:
            rr, cc = r + dr, c + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                PAWN_ATTACKS[BLACK][sq].append((rr, cc))

BISHOP_RAYS = [[] for _ in range(64)]
for r in range(8):
    for c in range(8):
        sq = r*8 + c

        rays = []

        for dr, dc in DIRECTIONS[BISHOP]:
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

        for dr, dc in DIRECTIONS[ROOK]:
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
        pawn, knight, king = PAWN, KNIGHT, KING
        pawn_table = PAWN_ATTACKS[BLACK]  # reverse lookup
        rook, bishop, queen = ROOK, BISHOP, QUEEN
    else:
        pawn, knight, king = -PAWN, -KNIGHT, -KING
        pawn_table = PAWN_ATTACKS[WHITE]
        rook, bishop, queen = -ROOK, -BISHOP, -QUEEN

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
            if piece == EMPTY:
                continue
            if piece == rook or piece == queen:
                return True
            break  # blocked

    for ray in BISHOP_RAYS[s]:  # bishop/queen
        for rr, cc in ray:
            piece = board[rr][cc]
            if piece == EMPTY:
                continue
            if piece == bishop or piece == queen:
                return True
            break  # blocked

    return False
