import numpy as np
from collections import namedtuple


# GLOBAL CONSTANTS

# # Initial chess board setup
BOARD = np.array([
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
], dtype='U1')
BOARD = np.flipud(BOARD) # Flip board upside down for 0 indexing to be correct

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

# Sliding vs non-sliding
SLIDING = {"B", "R", "Q"}


# GAME LOGIC

# Move representation
Move = namedtuple('Move', ('src', 'dst', 'promo'))

class Position(namedtuple('Position', ('board', 'score', 'wc', 'bc', 'ep', 'kp', 'sd'))):
    # A state of a chess game
    # board -- the current board state as a numpy array
    # score -- the board evaluation
    # wc    -- white castling rights, [left/queen side, right/king side]
    # bc    -- black castling rights, [left/king side, right/queen side]
    # ep    -- the en passant square
    # kp    -- the king passant square
    # sd    -- the player to move

    # Return pseudo-legal moves for a single piece at a given position.
    def gen_moves(self):
        DIRS = DIRECTIONS  # local alias
        in_bounds = lambda r, c: 0 <= r < 8 and 0 <= c < 8

        moves = []
        append = moves.append

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
                                append(Move((r0, c0), (r, c), None))
                            # double step
                            if r0 == start_row:
                                rr = r + dr; cc = c + dc
                                if in_bounds(rr, cc) and self.board[rr][cc] == '.':
                                    append(Move((r0, c0), (rr, cc), None))
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
                                    append(Move((r0, c0), (r, c), None))
                            # En passant capture
                            elif self.ep is not None and (r, c) == self.ep:
                                append(Move((r0, c0), (r, c), None))  # en passant move
                    # done with this pawn
                    continue

                # --- Non-pawns ---
                dirs = DIRS[pu]
                sliding = pu in ("B", "R", "Q")

                for dr, dc in dirs:
                    r = r0; c = c0
                    while True:
                        r += dr; c += dc
                        if not in_bounds(r, c):
                            break
                        target = self.board[r][c]
                        if target == '.':
                            append(Move((r0, c0), (r, c), None))
                            if not sliding:
                                break
                        else:
                            # enemy?
                            if target.isupper() != is_white:
                                append(Move((r0, c0), (r, c), None))
                            break

                # --- Castling ---
                if pu == 'K':
                    back_row = 0 if is_white else 7
                    rights = self.wc if is_white else self.bc

                    # King-side castling
                    if rights[1]:  # king-side right available
                        if self.board[back_row][5] == '.' and self.board[back_row][6] == '.':
                            append(Move((r0, c0), (back_row, 6), None))

                    # Queen-side castling
                    if rights[0]:  # queen-side right available
                        if (self.board[back_row][1] == '.' and
                            self.board[back_row][2] == '.' and
                            self.board[back_row][3] == '.'):
                            append(Move((r0, c0), (back_row, 2), None))

        return moves

    # Check for legal moves
    def is_legal(self, move):

        def attacked(sq, side):
            r, c = sq
            board = self.board
            in_bounds = lambda r, c: 0 <= r < 8 and 0 <= c < 8

            # Piece sets
            is_attacker = str.isupper if side == 'w' else str.islower

            # --- Pawn attacks ---
            pawn_dirs = [(-1, -1), (-1, 1)] if side == 'w' else [(1, -1), (1, 1)]
            pawn = 'P' if side == 'w' else 'p'
            for dr, dc in pawn_dirs:
                rr, cc = r + dr, c + dc
                if in_bounds(rr, cc) and board[rr][cc] == pawn:
                    return True

            # --- Knight attacks ---
            for dr, dc in DIRECTIONS["N"]:
                rr, cc = r + dr, c + dc
                if in_bounds(rr, cc) and board[rr][cc] == ('N' if side == 'w' else 'n'):
                    return True

            # --- King attacks ---
            for dr, dc in DIRECTIONS["K"]:
                rr, cc = r + dr, c + dc
                if in_bounds(rr, cc) and board[rr][cc] == ('K' if side == 'w' else 'k'):
                    return True

            # --- Sliding attacks ---
            sliders = {
                "B": DIRECTIONS["B"],
                "R": DIRECTIONS["R"],
                "Q": DIRECTIONS["Q"],
            }
            for piece, dirs in sliders.items():
                p = piece if side == 'w' else piece.lower()
                for dr, dc in dirs:
                    rr, cc = r, c
                    while True:
                        rr += dr; cc += dc
                        if not in_bounds(rr, cc):
                            break
                        sq_piece = board[rr][cc]
                        if sq_piece == '.':
                            continue
                        if sq_piece == p:
                            return True
                        break  # blocked by other piece

            return False

        src, dst, promo = move.src, move.dst, move.promo
        r0, c0 = src
        r1, c1 = dst

        is_white = self.sd == 'w'
        opponent = 'b' if is_white else 'w'

        # --- Make a backup copy of state we may need to revert ---
        captured_piece = self.board[r1][c1]
        ep_backup = self.ep
        wc_backup = self.wc[:]
        bc_backup = self.bc[:]            

        # --- Handle castling moves ---
        piece = self.board[r0][c0]
        if piece.upper() == 'K' and abs(c1 - c0) == 2:
            if c1 == 6:  # King-side castle
                rook_src, rook_dst = (r0, 7), (r0, 5)
            else:  # Queen-side castle
                rook_src, rook_dst = (r0, 0), (r0, 3)

            # Temporary move
            self.board[r0][c0] = '.'
            self.board[r1][c1] = 'K' if is_white else 'k'
            self.board[rook_dst[0]][rook_dst[1]] = self.board[rook_src[0]][rook_src[1]]
            self.board[rook_src[0]][rook_src[1]] = '.'

            # Check if king passes through or ends up in check
            king_squares = [(r0, c0), (r0, (c0 + c1)//2), (r1, c1)]
            legal = all(
                not attacked(sq, opponent)
                for sq in king_squares
            )

            # Undo temporary move
            self.board[r0][c0] = 'K' if is_white else 'k'
            self.board[r1][c1] = '.'
            self.board[rook_src[0]][rook_src[1]] = self.board[rook_dst[0]][rook_dst[1]]
            self.board[rook_dst[0]][rook_dst[1]] = '.'

            # TODO: restore state
            # self.ep = ep_backup
            # self.wc, self.bc = wc_backup, bc_backup
            return legal

        # --- Handle en passant moves ---
        if piece.upper() == 'P' and self.ep and dst == self.ep:
            # Remove the pawn captured en passant
            pawn_row = r1 + (1 if is_white else -1)
            captured_piece = self.board[pawn_row][c1]
            self.board[pawn_row][c1] = '.'

        # --- Normal move ---
        self.board[r0][c0] = '.'
        self.board[r1][c1] = piece if not promo else (promo if is_white else promo.lower())

        # Find king position
        king_square = None
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == ('K' if is_white else 'k'):
                    king_square = (r, c)
                    break
            if king_square:
                break

        # Check if own king is attacked
        legal = not attacked(king_square, opponent)

        # Undo move
        self.board[r0][c0] = piece
        self.board[r1][c1] = captured_piece
        # TODO: restore state
        # self.ep = ep_backup
        # self.wc, self.bc = wc_backup, bc_backup

        return legal

