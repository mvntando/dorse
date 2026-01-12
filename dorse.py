import random as random
from utils import DIRECTIONS, SLIDING, START_POS, legal

# GAME LOGIC
# Move representation
class Move:
    __slots__ = ('src', 'dst', 'promo')

    def __init__(self, src, dst, promo=''):
        self.src = src
        self.dst = dst
        self.promo = promo

class Position:
    __slots__ = ('board', 'score', 'wc', 'bc', 'ep', 'sd')

    # A state of a chess game
    # board -- the current board state as a numpy array. !IMPOTANT - board is a cartesian grid
    # score -- the board evaluation
    # wc    -- white castling rights, [left/queen side, right/king side]
    # bc    -- black castling rights, [left/queen side, right/king side]
    # ep    -- the en passant square
    # sd    -- the player to move

    def __init__(self, board, score, wc, bc, ep, sd):
        self.board = board
        self.score = score
        self.wc = wc
        self.bc = bc
        self.ep = ep
        self.sd = sd

    # Return pseudo-legal moves for a single piece at a given position.
    def gen_moves(self):
        DIRS = DIRECTIONS  # local alias
        in_bounds = lambda r, c: 0 <= r < 8 and 0 <= c < 8

        moves = []
        append = lambda move: moves.append(move) if legal(self, move) else None # Only append legal moves

        for r0 in range(8):
            row = self.board[r0]  # local row ref for a tiny speed boost
            for c0 in range(8):
                piece = row[c0]
                if piece == '.':
                    continue
                # skip opponent pieces
                if self.sd == 'w':
                    if not piece.isupper():
                        continue
                else:  # player == 'b'
                    if not piece.islower():
                        continue

                is_white = piece.isupper()
                pu = piece.upper()

                # --- Pawn logic ---
                if pu == 'P':
                    if is_white:
                        fwd_dirs = DIRS["P"]
                        cap_dirs = DIRS["P_capture"]
                        start_row = 1
                        promo_row = 7
                    else:
                        fwd_dirs = DIRS["p"]
                        cap_dirs = DIRS["p_capture"]
                        start_row = 6
                        promo_row = 0
                    # forward moves
                    for dr, dc in fwd_dirs:
                        r = r0 + dr; c = c0 + dc
                        if in_bounds(r, c) and self.board[r][c] == '.':
                            if r == promo_row:
                                for promo in ("Q","R","B","N"):
                                    append(Move((r0, c0), (r, c), promo))
                            else:
                                append(Move((r0, c0), (r, c), ""))
                            # double step
                            if r0 == start_row:
                                rr = r + dr; cc = c + dc
                                if in_bounds(rr, cc) and self.board[rr][cc] == '.':
                                    append(Move((r0, c0), (rr, cc), ""))
                    # captures
                    for dr, dc in cap_dirs:
                        r = r0 + dr; c = c0 + dc
                        if in_bounds(r, c):
                            target = self.board[r][c]
                            if target != '.' and (target.isupper() != is_white):
                                if r == promo_row:
                                    for promo in ("Q","R","B","N"):
                                        append(Move((r0, c0), (r, c), promo))
                                else:
                                    append(Move((r0, c0), (r, c), ""))
                            # En passant capture
                            elif self.ep is not None and (r, c) == self.ep:
                                append(Move((r0, c0), (r, c), ""))  # en passant move
                    # done with this pawn
                    continue

                # --- Non-pawns ---
                dirs = DIRS[pu]
                sliding = pu in SLIDING

                for dr, dc in dirs:
                    r = r0; c = c0
                    while True:
                        r += dr; c += dc
                        if not in_bounds(r, c):
                            break
                        target = self.board[r][c]
                        if target == '.':
                            append(Move((r0, c0), (r, c), ""))
                            if not sliding:
                                break
                        else:
                            # enemy?
                            if target.isupper() != is_white:
                                append(Move((r0, c0), (r, c), ""))
                            break

                # --- Castling ---
                if pu == 'K':
                    back_row = 0 if is_white else 7
                    rights = self.wc if is_white else self.bc

                    # King-side castling
                    if rights[1]:  # king-side right available
                        if self.board[back_row][5] == '.' and self.board[back_row][6] == '.':
                            append(Move((r0, c0), (back_row, 6), ""))

                    # Queen-side castling
                    if rights[0]:  # queen-side right available
                        if (self.board[back_row][1] == '.' and
                            self.board[back_row][2] == '.' and
                            self.board[back_row][3] == '.'):
                            append(Move((r0, c0), (back_row, 2), ""))

        return moves

    def move(self, move):
        src, dst, promo = move.src, move.dst, move.promo
        r0, c0 = src
        r1, c1 = dst
        piece = self.board[r0][c0]

        is_white = self.sd == 'w'

        # --- Handle en passant capture ---
        if piece.upper() == 'P' and self.ep and dst == self.ep:
            self.board[r0][c1] = '.'

        # --- Update castling rights if rook was captured ---
        captured = self.board[r1][c1]  # destination square BEFORE the move
        if captured.upper() == 'R':
            if is_white:  # Captured black rook
                if dst == (7, 0) and self.bc[0] != 0:  # a8 rook
                    self.bc = (0, self.bc[1])
                elif dst == (7, 7) and self.bc[1] != 0:  # h8 rook
                    self.bc = (self.bc[0], 0)
            else:  # Captured white rook
                if dst == (0, 0) and self.wc[0] != 0:  # a1 rook
                    self.wc = (0, self.wc[1])
                elif dst == (0, 7) and self.wc[1] != 0:  # h1 rook
                    self.wc = (self.wc[0], 0)

        # --- Move piece ---
        self.board[r1][c1] = piece
        self.board[r0][c0] = '.'

        # --- Handle promotion ---
        if promo:
            self.board[r1][c1] = promo if is_white else promo.lower()

        # --- Handle castling (moving rook as well) ---
        if piece.upper() == 'K' and abs(c1 - c0) == 2:
            if c1 == 6:  # Kingside castling
                self.board[r1][5] = 'R' if is_white else 'r'
                self.board[r1][7] = '.'
            elif c1 == 2:  # Queenside castling
                self.board[r1][3] = 'R' if is_white else 'r'
                self.board[r1][0] = '.'

        # --- Update castling rights ---
        if piece.upper() == 'K':  # King moved → lose both rights
            if is_white:
                if self.wc != (0, 0):
                    self.wc = (0, 0)
            else:
                if self.bc != (0, 0):
                    self.bc = (0, 0)

        elif piece.upper() == 'R':  # Rook moved
            if is_white:  # White rook moved
                if src == (0, 0):  # a1 rook
                    if self.wc[0] != 0:
                        self.wc = (0, self.wc[1])
                elif src == (0, 7):  # h1 rook
                    if self.wc[1] != 0:
                        self.wc = (self.wc[0], 0)
            else:  # Black rook moved
                if src == (7, 0):  # a8 rook
                    if self.bc[0] != 0:
                        self.bc = (0, self.bc[1])
                elif src == (7, 7):  # h8 rook
                    if self.bc[1] != 0:
                        self.bc = (self.bc[0], 0)

        # --- Update en passant target ---
        if piece.upper() == 'P' and abs(r1 - r0) == 2:
            self.ep = ((r0 + r1) // 2, c0)
        else:
            self.ep = None

        # --- Switch side ---
        self.sd = 'b' if is_white else 'w'

        return self

    def search(self):
        moves = self.gen_moves()

        # Return random moves
        if moves:
            return random.choice(moves)
        return None

    def play(self):
        move = self.search()
        if move:
            self.move(move)
            return move
        return None
    
    def make_uci_move(self, uci_move):
        file_from = ord(uci_move[0]) - ord('a')
        rank_from = int(uci_move[1]) - 1
        file_to   = ord(uci_move[2]) - ord('a')
        rank_to   = int(uci_move[3]) - 1

        src = (rank_from, file_from)
        dst = (rank_to, file_to)

        promo = (p.upper() if self.sd == 'w' else p) if (p := uci_move[4:5]) else None

        for m in self.gen_moves():
            if m.src == src and m.dst == dst:
                if promo is None or (m.promo and m.promo.upper() == promo.upper()):
                    self.move(m)
                    return

        raise ValueError(f"Illegal UCI move: {uci_move}")

