# Convert a position to algebraic notation
def notation(pos):
    # If pos is a string, convert it to coordinates
    if isinstance(pos, str):
        files = "abcdefgh"
        ranks = "12345678"
        col = files.index(pos[0])
        row = ranks.index(pos[1])
        return (row, col)

    # If pos is a tuple, convert it to chess notation
    files = "abcdefgh"  # columns
    ranks = "12345678"  # rows from White's perspective
    if 0 <= pos[0] < 8 and 0 <= pos[1] < 8:
        return files[pos[1]] + ranks[pos[0]]
    raise ValueError("Coordinates out of range")

