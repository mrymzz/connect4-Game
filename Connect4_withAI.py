

import numpy as np
import random
import pygame   # should be initialized
import sys      # to close 
import math
# initiate Constants to make changes easy
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
ROWS = 6
COLUMNS = 7
PLAYER = 0
AI = 1
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 4
SQUARESIZE = 100
WIDTH = COLUMNS * SQUARESIZE
HEIGHT = (ROWS+1) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)
RADIUS = int(SQUARESIZE/2 - 5)

# Initialize board
def create_board(): 
	board = np.zeros((ROWS,COLUMNS))
	return board

# Drop piece in column
def drop_piece(board, row, col, piece): 
	board[row][col] = piece

# Check if column is valid for placing a piece or is colmpleted
def is_valid_location(board, col): 
	return board[ROWS-1][col] == 0

# Get next available row in column
def get_next_open_row(board, col):
	for ro in range(ROWS):
		if board[ro][col] == 0:
			return ro

# Print board
def print_board(board): # to make pieces start from bottom (flip on x axis)
	print(np.flip(board, 0))

# Draw board
def draw_board(board):
	for col in range(COLUMNS):
		for ro in range(ROWS):              
			pygame.draw.rect(screen, BLUE, (col*SQUARESIZE, ro*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, BLACK, (int(col*SQUARESIZE+SQUARESIZE/2), int(ro*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS) # pygame only accept int
			                                         # +sq/2 to offset( 3a4an el ezaha maykono4 laz2een)
	# pieces
	for col in range(COLUMNS):
		for ro in range(ROWS):		
			if board[ro][col] == PLAYER_PIECE:
				pygame.draw.circle(screen, RED, (int(col*SQUARESIZE+SQUARESIZE/2), HEIGHT-int(ro*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[ro][col] == AI_PIECE: 
				pygame.draw.circle(screen, YELLOW, (int(col*SQUARESIZE+SQUARESIZE/2), HEIGHT-int(ro*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()


def winning_move(board, piece):
	for col in range(COLUMNS-3):    # horizontal win  ( last 3 columns can't be the start)
		for ro in range(ROWS):     
			if board[ro][col] == piece and board[ro][col+1] == piece and board[ro][col+2] == piece and board[ro][col+3] == piece:
				return True

	for col in range(COLUMNS):      # vertical win  ( last 3 rows can't be the start)
		for ro in range(ROWS-3):   
			if board[ro][col] == piece and board[ro+1][col] == piece and board[ro+2][col] == piece and board[ro+3][col] == piece:
				return True

	for col in range(COLUMNS-3):    # positively sloped diaganols (bottom-up)
		for ro in range(ROWS-3):
			if board[ro][col] == piece and board[ro+1][col+1] == piece and board[ro+2][col+2] == piece and board[ro+3][col+3] == piece:
				return True

	for col in range(COLUMNS-3):	# Check negatively sloped diaganols (top-down)
		for ro in range(3, ROWS):
			if board[ro][col] == piece and board[ro-1][col+1] == piece and board[ro-2][col+2] == piece and board[ro-3][col+3] == piece:
				return True

def evaluate_window(window, piece):
	score = 0
	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece = AI_PIECE

	if window.count(piece) == 4:
		score += 100
	elif window.count(opp_piece) == 4:
		score -= 80
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2
	elif window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 5

	return score

 

def score_position(board, piece):
	score = 0

	## Score center column
	center_array = [int(i) for i in list(board[:, COLUMNS//2])]
	center_count = center_array.count(piece)
	score += center_count * 3

	## Score Horizontal
	for ro in range(ROWS):
		row_array = [int(i) for i in list(board[ro,:])]
		for col in range(COLUMNS-3):
			window = row_array[col:col+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score Vertical
	for col in range(COLUMNS):
		col_array = [int(i) for i in list(board[:,col])]
		for ro in range(ROWS-3):
			window = col_array[ro:ro+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score positive sloped diagonal
	for ro in range(ROWS-3):
		for col in range(COLUMNS-3):
			window = [board[ro+i][col+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	## Score negative sloped diagonal
	for ro in range(ROWS-3):
		for col in range(COLUMNS-3):
			window = [board[ro+3-i][col+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	return score


def get_valid_locations(board):
	valid_locations = []
	for col in range(COLUMNS):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def is_terminal_node(board):
	return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0 # game is ove one win or no more moves

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
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy() # to save in memory(no delete ,not temporary)
			drop_piece(b_copy, row, col, AI_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: # Minimizing player
		value = math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, PLAYER_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value



board = create_board()
print_board(board)
game_over = False

pygame.init() 
screen = pygame.display.set_mode(SIZE)
draw_board(board)
pygame.display.update()
myfont = pygame.font.SysFont("monospace", 75)
turn = random.randint(PLAYER, AI)

while not game_over:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEMOTION:
			pygame.draw.rect(screen, BLACK, (0,0, WIDTH, SQUARESIZE)) # remove balls time by time (draw black rects) to make just one appear
			posx = event.pos[0]
			if turn == PLAYER:
				pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)

		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			pygame.draw.rect(screen, BLACK, (0,0, WIDTH, SQUARESIZE)) # remove last ball after winning
			#print(event.pos)
			# Ask for Player 1 Input
			if turn == PLAYER:
				posx = event.pos[0]
				col = int(math.floor(posx/SQUARESIZE)) #to make it from (0,7) not 700 

				if is_valid_location(board, col):
					row = get_next_open_row(board, col)
					drop_piece(board, row, col, PLAYER_PIECE)

					if winning_move(board, PLAYER_PIECE):
						label = myfont.render("Player 1 wins!!", 1, RED)
						screen.blit(label, (40,10))
						game_over = True

					turn += 1
					turn = turn % 2

					print_board(board)
					draw_board(board)

    # Ask for Player 2 Input
	if turn == AI and not game_over:				
		col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

		if is_valid_location(board, col):
			#pygame.time.wait(500)
			row = get_next_open_row(board, col)
			drop_piece(board, row, col, AI_PIECE)

			if winning_move(board, AI_PIECE):
				label = myfont.render("Player 2 wins!!", 1, YELLOW)
				screen.blit(label, (40,10))
				game_over = True

			print_board(board)
			draw_board(board)

			turn += 1
			turn = turn % 2

	if game_over:
		pygame.time.wait(3000)

#=========================================================================================================================================================================================
# =====================================================================     :::::::::::::       ==========================================================================================          
# =====================================================================     :::  DONE :::       ========================================================================================== 
# =====================================================================     :::::::::::::       ==========================================================================================   
#=========================================================================================================================================================================================
