import numpy as np
import random
import pygame
import sys
import math

# Constants
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ROWS = 8
COLUMNS = 10
PLAYER = 0
AI = 1
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 6
SQUARESIZE = 75
WIDTH = COLUMNS * SQUARESIZE
HEIGHT = (ROWS + 1) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)
RADIUS = int(SQUARESIZE / 2 - 5)

# Initialize board
def create_board(): 
    return np.zeros((ROWS, COLUMNS))

# Drop piece in column
def drop_piece(board, row, col, piece): 
    board[row][col] = piece

# Check if column is valid for placing a piece
def is_valid_location(board, col): 
    return board[ROWS - 1][col] == 0

# Get next available row in column
def get_next_open_row(board, col):
    for ro in range(ROWS):
        if board[ro][col] == 0:
            return ro

# Print board
def print_board(board): 
    print(np.flip(board, 0))

# Draw board
def draw_board(screen, board):
    for col in range(COLUMNS):
        for ro in range(ROWS):
            pygame.draw.rect(screen, BLUE, (col * SQUARESIZE, ro * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(col * SQUARESIZE + SQUARESIZE / 2), int(ro * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    
    for col in range(COLUMNS):
        for ro in range(ROWS):       
            if board[ro][col] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(col * SQUARESIZE + SQUARESIZE / 2), HEIGHT - int(ro * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[ro][col] == AI_PIECE: 
                pygame.draw.circle(screen, YELLOW, (int(col * SQUARESIZE + SQUARESIZE / 2), HEIGHT - int(ro * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()

# Check if player has won
def winning_move(board, piece):
    for col in range(COLUMNS - 5):    # Horizontal
        for ro in range(ROWS):     
            if board[ro][col] == piece and board[ro][col + 1] == piece and board[ro][col + 2] == piece and board[ro][col + 3] == piece and board[ro][col + 4] == piece and board[ro][col + 5] == piece:
                return True

    for col in range(COLUMNS):      # Vertical
        for ro in range(ROWS - 5):   
            if board[ro][col] == piece and board[ro + 1][col] == piece and board[ro + 2][col] == piece and board[ro + 3][col] == piece and board[ro + 4][col] == piece and board[ro + 5][col] == piece:
                return True

    for col in range(COLUMNS - 5):    # Positively sloped diagonal
        for ro in range(ROWS - 5):
            if board[ro][col] == piece and board[ro + 1][col + 1] == piece and board[ro + 2][col + 2] == piece and board[ro + 3][col + 3] == piece and board[ro + 4][col + 4] == piece and board[ro + 5][col + 5] == piece:
                return True

    for col in range(COLUMNS - 5):    # Negatively sloped diagonal
        for ro in range(5, ROWS):
            if board[ro][col] == piece and board[ro - 1][col + 1] == piece and board[ro - 2][col + 2] == piece and board[ro - 3][col + 3] == piece and board[ro - 4][col + 4] == piece and board[ro - 5][col + 5] == piece:
                return True

# Evaluate window for AI scoring
def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    if window.count(piece) == 6:
        score += 100
    elif window.count(opp_piece) == 6:
        score -= 80
    elif window.count(piece) == 5 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 4 and window.count(EMPTY) == 2:
        score += 2
    elif window.count(opp_piece) == 5 and window.count(EMPTY) == 1:
        score -= 5

    return score

# Score position for AI
def score_position(board, piece):
    score = 0

    # Score Horizontal
    for ro in range(ROWS):
        row_array = [int(i) for i in list(board[ro,:])]
        for col in range(COLUMNS - 5):
            window = row_array[col:col + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for col in range(COLUMNS):
        col_array = [int(i) for i in list(board[:,col])]
        for ro in range(ROWS - 5):
            window = col_array[ro:ro + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score positively sloped diagonal
    for ro in range(ROWS - 5):
        for col in range(COLUMNS - 5):
            window = [board[ro + i][col + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Score negatively sloped diagonal
    for ro in range(5, ROWS):
        for col in range(COLUMNS - 5):
            window = [board[ro - i][col + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

# Get valid locations for AI moves
def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMNS):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

# Check if terminal node reached
def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

# Minimax algorithm with alpha-beta pruning
def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        best_col = random.choice(valid_locations)  # Initialize with random column
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
    else: # Minimizing player
        value = math.inf
        best_col = random.choice(valid_locations)  # Initialize with random column
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

# Main game loop
def main():
    # Initialize game
    board = create_board()
    print_board(board)
    game_over = False

    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    draw_board(screen, board)
    pygame.display.update()
    myfont = pygame.font.SysFont("monospace", 75)
    turn = random.randint(PLAYER, AI)

    # Game loop
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                posx = event.pos[0]
                if turn == PLAYER:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)

                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        label = myfont.render("Player wins!!", 1, RED)
                        screen.blit(label, (40, 10))
                        game_over = True

                    turn += 1
                    turn %= 2

                    print_board(board)
                    draw_board(screen, board)

            if turn == AI and not game_over:              
                col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, AI_PIECE)

                    if winning_move(board, AI_PIECE):
                        label = myfont.render("AI wins!!", 1, YELLOW)
                        screen.blit(label, (40, 10))
                        game_over = True

                    print_board(board)
                    draw_board(screen, board)

                    turn += 1
                    turn %= 2

                if game_over:
                    pygame.time.wait(3000)

if __name__ == "__main__":
    main()
