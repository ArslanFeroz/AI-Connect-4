import math

import numpy as np

ROWS = 6
COLS = 7
PLAYER = 1  # User
AI = 2  # Computer
EMPTY = 0
WINDOW_LENGTH = 4


def create_board():
    return np.zeros((ROWS, COLS), dtype=int)


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROWS - 1][col] == EMPTY


def get_next_open_row(board, col):
    for row in range(ROWS):
        if board[row][col] == EMPTY:
            return row


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):

    for i in range(ROWS):
        for j in range(COLS):
            if board[i][j] == piece:

                # ---------------- HORIZONTAL CHECK ----------------
                curr_row = i
                curr_col = j

                # go to the start of the horizontal sequence
                while curr_col > 0 and board[curr_row][curr_col - 1] == piece:
                    curr_col -= 1

                # count consecutive pieces
                count = 0
                while curr_col < COLS and board[curr_row][curr_col] == piece:
                    count += 1
                    if count == 4:
                        return True
                    curr_col += 1

                # ---------------- VERTICAL CHECK ----------------
                curr_row = i
                curr_col = j

                # go to the start of the vertical sequence
                while curr_row > 0 and board[curr_row - 1][curr_col] == piece:
                    curr_row -= 1

                # count consecutive pieces
                count = 0
                while curr_row < ROWS and board[curr_row][curr_col] == piece:
                    count += 1
                    if count == 4:
                        return True
                    curr_row += 1

                # ---------------- DIAGONAL (\) CHECK ----------------
                curr_row = i
                curr_col = j

                # go to the start of the diagonal sequence
                while curr_row > 0 and curr_col > 0 and board[curr_row - 1][curr_col - 1] == piece:
                    curr_row -= 1
                    curr_col -= 1

                # count consecutive pieces
                count = 0
                while curr_row < ROWS and curr_col < COLS and board[curr_row][curr_col] == piece:
                    count += 1
                    if count == 4:
                        return True
                    curr_row += 1
                    curr_col += 1

                # ---------------- DIAGONAL (/) CHECK ----------------
                curr_row = i
                curr_col = j

                # go to the start of the anti-diagonal sequence
                while curr_row < ROWS - 1 and curr_col > 0 and board[curr_row + 1][curr_col - 1] == piece:
                    curr_row += 1
                    curr_col -= 1

                # count consecutive pieces
                count = 0
                while curr_row >= 0 and curr_col < COLS and board[curr_row][curr_col] == piece:
                    count += 1
                    if count == 4:
                        return True
                    curr_row -= 1
                    curr_col += 1

    return False


def score_position(board, piece):
    opp_piece = PLAYER if piece == AI else AI

    def score_window(piece_count, opp_count, empty_count):
        if piece_count == 4:
            return 100
        elif piece_count == 3 and empty_count == 1:
            return 5
        elif piece_count == 2 and empty_count == 2:
            return 2
        elif opp_count == 3 and empty_count == 1:
            return -4  # block opponent
        return 0

    score = 0

    for i in range(ROWS):
        for j in range(COLS):
            if board[i][j] == EMPTY:
                continue

            # horizontal
            if j + WINDOW_LENGTH <= COLS:
                pc = oc = ec = 0
                for k in range(WINDOW_LENGTH):
                    cell = board[i][j + k]
                    if cell == piece: pc += 1
                    elif cell == opp_piece: oc += 1
                    else: ec += 1
                score += score_window(pc, oc, ec)

            # vertical
            if i + WINDOW_LENGTH <= ROWS:
                pc = oc = ec = 0
                for k in range(WINDOW_LENGTH):
                    cell = board[i + k][j]
                    if cell == piece: pc += 1
                    elif cell == opp_piece: oc += 1
                    else: ec += 1
                score += score_window(pc, oc, ec)

            # diagonal (\)
            if i + WINDOW_LENGTH <= ROWS and j + WINDOW_LENGTH <= COLS:
                pc = oc = ec = 0
                for k in range(WINDOW_LENGTH):
                    cell = board[i + k][j + k]
                    if cell == piece: pc += 1
                    elif cell == opp_piece: oc += 1
                    else: ec += 1
                score += score_window(pc, oc, ec)

            # anti-diagonal (/)
            if i - WINDOW_LENGTH + 1 >= 0 and j + WINDOW_LENGTH <= COLS:
                pc = oc = ec = 0
                for k in range(WINDOW_LENGTH):
                    cell = board[i - k][j + k]
                    if cell == piece: pc += 1
                    elif cell == opp_piece: oc += 1
                    else: ec += 1
                score += score_window(pc, oc, ec)

    return score


def get_valid_locations(board):
    valid_cols = []
    for col in range(COLS):
        if is_valid_location(board, col):
            valid_cols.append(col)
    return valid_cols


def is_terminal_node(board):
    if winning_move(board, AI):
        return (True, AI)
    elif winning_move(board, PLAYER):
        return (True, PLAYER)
    elif len(get_valid_locations(board)) == 0:   # FIX: was empty() from numpy — wrong function
        return (True, -1)
    else:
        return (False, 0)


def minimax(board, depth, maximizingPlayer):
    status, obj = is_terminal_node(board)

    # --- Base case: terminal board state ---
    if status == True:
        if obj == AI:
            return (None, math.inf)
        elif obj == PLAYER:
            return (None, -math.inf)
        else:
            return (None, 0)

    # --- Base case: depth limit reached — evaluate statically ---
    if depth == 0:
        return (None, score_position(board, AI))   # FIX: was returning bare int, must be a tuple

    if maximizingPlayer:
        best_score = -math.inf
        valid_col = get_valid_locations(board)
        best_col = None

        for col in valid_col:
            board_copy = board.copy()                                     # FIX: copy BEFORE dropping, never mutate original
            drop_piece(board_copy, get_next_open_row(board_copy, col), col, AI)
            _, score = minimax(board_copy, depth - 1, False)             # FIX: unpack tuple; was comparing tuple to int
            if score > best_score:
                best_score = score
                best_col = col
        return (best_col, best_score)

    else:
        best_score = math.inf                                             # FIX: removed duplicate line that reset this to -inf
        valid_col = get_valid_locations(board)
        best_col = None

        for col in valid_col:
            board_copy = board.copy()                                     # FIX: copy BEFORE dropping, never mutate original
            drop_piece(board_copy, get_next_open_row(board_copy, col), col, PLAYER)   # FIX: was dropping AI piece instead of PLAYER
            _, score = minimax(board_copy, depth - 1, True)              # FIX: unpack tuple; was comparing tuple to int
            if score < best_score:
                best_score = score
                best_col = col
        return (best_col, best_score)


def best_move(board, depth=4):
    col, score = minimax(board.copy(), depth, True)
    return col


# -------------------- MAIN GAME LOOP --------------------
board = create_board()
game_over = False
turn = 0  # 0 = Player goes first, 1 = AI

print("Welcome to Connect Four!")
print("You are Player 1 (piece = 1). AI is piece 2.")
print("Columns are numbered 0 to 6 (left to right).\n")
print_board(board)

while not game_over:

    # ---------------- PLAYER'S TURN ----------------
    if turn == 0:
        valid_input = False
        while not valid_input:
            try:
                col = int(input("\nPlayer, choose a column (0-6): "))
                if col < 0 or col >= COLS:
                    print("Column out of range. Pick between 0 and 6.")
                elif not is_valid_location(board, col):
                    print("That column is full. Try another.")
                else:
                    valid_input = True
            except ValueError:
                print("Invalid input. Enter a number between 0 and 6.")

        row = get_next_open_row(board, col)
        drop_piece(board, row, col, PLAYER)

        print_board(board)

        if winning_move(board, PLAYER):
            print("\nPlayer wins! Congratulations!")
            game_over = True

    # ---------------- AI'S TURN ----------------
    else:
        print("\nAI is thinking...")
        col = best_move(board)
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, AI)

        print(f"AI chose column {col}.")
        print_board(board)

        if winning_move(board, AI):
            print("\nAI wins! Better luck next time.")
            game_over = True

    # ---------------- CHECK DRAW ----------------
    if not game_over and len(get_valid_locations(board)) == 0:
        print("\nIt's a draw!")
        game_over = True

    # toggle turn: 0 -> 1 -> 0 -> ...
    turn = 1 - turn