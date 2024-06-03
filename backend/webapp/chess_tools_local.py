import numpy as np
from PIL import Image,ImageDraw, ImageFont
import math
import chess


def fen_to_ascii(FEN):
    """ Converts Forysth-Edwards notation to board with ASCII characters """
    board = ''
    for character in FEN:
        if character.isalpha():
            board = board + ' ' + character  
        if character.isnumeric():
            for n in range(int(character)):
                board = board + ' ' + '.' 
        if character == '/':
            continue
        if character == ' ':
            break
    list = board.split()
    arr = np.array(list)
    arr = arr.reshape(-1, 8)

    return arr


def one_hot_encode(array):
    """ Converts ASCII board to 64x13 one-hot tensor:  array[squares, piece_vectors] """
    input = array.flatten()
    one_hot = np.zeros(shape=(64,13), dtype=bool)
    encoding = {'r':0, 'n':1, 'b':2, 'q':3, 'k':4, 'p':5, 'R':6, 'N':7, 'B':8, 'Q':9, 'K':10, 'P':11, '.':12}
    for square, char in enumerate(input):
        one_hot[square][encoding[char]] = 1 

    return one_hot


def one_hot_decode(array):
    """ Converts one-hot array to board with ASCII characters """
    decoding = {0:'r', 1:'n', 2:'b', 3:'q', 4:'k', 5:'p', 6:'R', 7:'N', 8:'B', 9:'Q', 10:'K', 11:'P', 12:'.'}
    board = ''
    arr1 = array.reshape(64,13)
    for square in arr1:
        index = np.argmax(square)
        piece = decoding[index]
        board = board + str(piece) + ' '
    list = board.split()
    arr2 = np.array(list)
    arr2 = arr2.reshape(-1, 8)

    return arr2


def one_hot_to_unicode(array):
    """ Converts one-hot array to board with unicode chess piece symbols """
    decoding = {0:' \u2656', 1:' \u2658', 2:' \u2657', 3:' \u2655', 4:' \u2654', 5:' \u2659', 6:' \u265C', 7:' \u265E', 8:' \u265D', 9:' \u265B', 10:' \u265A', 11:' \u265F', 12:' .'}
    board = ''
    arr1 = array.reshape(64,13)
    for i, square in enumerate(arr1):
        index = np.argmax(square)
        piece = decoding[index]
        board = board + piece
        if (i+1) % 8 == 0 and i != 0:
            board = board + '\n'

    return board


def one_hot_to_fen(array, turn='black'):
    """ converts one-hot array to Forsyth-Edwards Notation string """
    board = one_hot_decode(array).flatten()
    FEN = []
    gap_count = 1

    for index, piece in enumerate(board):
        if piece != '.':
            FEN.append(str(piece))
            gap_count = 1
        if piece == '.':
            if gap_count > 1:
                del FEN[-1]
            FEN.append(gap_count)
            gap_count += 1
        if (index+1) % 8 == 0 and index != 63 and index != 0:
            FEN.append('/')
            gap_count = 1

    string = ' '.join([str(elem) for elem in FEN])
    string = string.replace(' ', '')
    if turn == 'black':
        string = string + ' b KQkq - 0 1'
    if turn == 'white':
        string = string + ' w KQkq - 0 1'
    return string


def one_hot_to_png(array):
    """ Converts one-hot array to graphic output """
    decoding = {0:'\u265C', 1:'\u265E', 2:'\u265D', 3:'\u265B', 4:'\u265A', 5:'\u265F', 6:'\u2656', 7:'\u2658', 8:'\u2657', 9:'\u2655', 10:'\u2654', 11:'\u2659', 12:' '}
    board = []
    arr1 = array.reshape(64,13)
    for i, square in enumerate(arr1):
        index = np.argmax(square)
        piece = decoding[index]
        board.append(piece)

    # Create image file
    image = np.full((338, 340, 3),fill_value=255, dtype=np.uint8)
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)

    # Draw checked pattern
    offset_x = 9
    offset_y = 8
    draw.rectangle((9, 8, 329, 329), fill=(245, 245, 245), outline=(225, 225, 225))
    for i in range(0, 8, 1):
        for j in range(0, 8, 1):
            if (i % 2 == 0 and j % 2 == 1) or (i % 2 == 1 and j % 2 == 0):
                draw.rectangle((j*40+offset_x, i*40+offset_y, (j*40)+40+offset_x, (i*40)+40+offset_y), fill=(225, 225, 225), outline=(225, 225, 225))

    # Draw pieces
    index = 0
    for i in range(0, 320, 40):
        for j in range(10, 330, 40):
            piece = board[index]
            draw.text((j, i), piece, fill=(0,0,0,255), align='center', font=ImageFont.truetype('/services/backend/webapp/pieces_font/FreeSerif.ttf', 50))
            index = index + 1

    return pil_image


def index_to_algebraic(square):
    """ Converts square index number (0-63) to algebraic notation (a8-h1) """
    letter = 'abcdefgh'
    letter = letter[(square % 8)]
    number = 8 - math.floor(square/8)

    return letter + str(number)


def is_move_legal(FEN, moves):
    """ checks if an algebraic notation move is legal according to chess rules, using python-chess library """
    board = chess.Board(FEN, chess960=True)
    alt_1 = moves[0] + moves[1]
    alt_2 = moves[1] + moves[0]
    if chess.Move.from_uci(alt_1) in board.legal_moves:
        is_legal = True
    elif chess.Move.from_uci(alt_2) in board.legal_moves:
        is_legal = True
    else:
        is_legal = False

    return is_legal


def any_cloned_pieces(x_array, y_array):
    """ compares input with prediction and returns True if any piece is cloned during a move """
    one_hot = np.zeros(shape=(64,13), dtype=int)
    x_array = x_array.astype(int)

    # convert y_array from categorical probabilities to one-hot
    y_array = np.array(y_array).reshape(64,13)
    for square, piece_vector in enumerate(y_array):
        index = np.argmax(piece_vector)
        one_hot[square][index] = 1 
    y_array = one_hot.reshape(1,64,13)

    # remove empty square category and get total of each piece type
    x_array = np.delete(x_array, 12, axis=2)
    y_array = np.delete(y_array, 12, axis=2)
    x_totals = x_array.sum(axis=1)
    y_totals = y_array.sum(axis=1)

    # check if any piece total has increased
    sub = np.subtract(x_totals, y_totals)
    boolean = np.any(sub < 0)
    return boolean


def confidence_score(y_array, exp=False):
    """ Evaluates the degree of confidence in a prediction, based on the whole board """
    total = 0.0
    board = y_array.reshape(64,13)
    for piece_vector in board:

        # Subtract all the lowest values in the piece vector from the highest value
        index = np.argmax(piece_vector)
        if exp == True:
            highest = piece_vector[index] ** 2
            exp_sum = 0.0
            for value in piece_vector:
                exp_sum += value ** 2
            others = exp_sum - highest
        else:
            highest = piece_vector[index]
            others = np.sum(piece_vector) - highest
        certainty = highest - others
        total += certainty

    return total


def update_one_hot(tensor, alg_move):
    """ Updates one-hot array with an algebraic notation move """
    board = one_hot_decode(tensor)
    move = str(alg_move).lower()

    if move == 'd1a1' and board[7][3] == 'k':
        # black kingside castling  
        board[7][0] = '.'
        board[7][1] = 'k'
        board[7][2] = 'r'
        board[7][3] = '.'

    elif move == 'd1h1'and board[7][3] == 'k':
        # black queenside castling  
        board[7][3] = '.'
        board[7][5] = 'r'
        board[7][6] = 'k'
        board[7][7] = '.'

    elif move == 'd8a8' and board[0][3] == 'K':
        # white kingside castling  
        board[0][0] = '.'
        board[0][1] = 'K'
        board[0][2] = 'R'
        board[0][3] = '.'

    elif move == 'd8h8'and board[0][3] == 'K':
        # white queenside castling  
        board[0][3] = '.'
        board[0][5] = 'R'
        board[0][6] = 'K'
        board[0][7] = '.'

    else:   
        # apply algebraic move  
        dict = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}        
        x_from = dict[move[0]]
        y_from = 8 - int(move[1])
        x_to = dict[move[2]]
        y_to = 8 - int(move[3])
        piece = board[y_from][x_from]
        board[y_from][x_from] = '.'
        board[y_to][x_to] = piece

        # promote any pawns on last rank to queen
        if piece == 'p' and y_to == 0:
            board[y_to][x_to] = 'q'
        if piece == 'P' and y_to == 7:
            board[y_to][x_to] = 'Q'

    tensor = one_hot_encode(board)
    return tensor


def swap_fen_colours(fen, turn='black'):
    """ Swaps colour of pieces in Forysth-Edwards notation """
    FEN = ''
    for char in str(fen):
        if char.isupper():
            FEN = FEN + char.lower()
        elif char.islower():
            FEN = FEN + char.upper()
        elif char == '/' or char.isnumeric():
            FEN = FEN + char
        else:
            if turn == 'black':
                FEN = FEN + ' b KQkq - 0 1'
            if turn == 'white':
                FEN = FEN + ' w KQkq - 0 1'
            break

    return FEN


# Unicode chess pieces 
print('\u265A ' '\u265B ' '\u265C ' '\u265D ' '\u265E ' '\u265F ' '\u2654 ' '\u2655 ' '\u2656 ' '\u2657 ' '\u2658 ' '\u2659' )


def find_legal_moves(FEN):
    """ returns a list of candidate board tensors with available moves applied """
    candidates = []
    algebraic_moves = []
    ascii_board = fen_to_ascii(FEN)
    current_tensor = one_hot_encode(ascii_board)
    FEN = swap_fen_colours(FEN, turn='black') 

    # analyse position with python-chess   
    board = chess.Board(FEN, chess960=True)
    for i, move in enumerate(board.legal_moves):
        candidate = update_one_hot(current_tensor, move)
        candidates.append(candidate)
        algebraic_moves.append(move)

    return candidates, algebraic_moves


def most_similar_move(candidates, target_tensor, algebraic_moves):
    """ Compares the cosine similarities of candidate tensors with a target 
        tensor and returns the most similar one """
    scores = []
    for candidate in candidates:
        f_candidate = candidate.astype('float32')
        dot_product = np.matmul(f_candidate.ravel(), np.transpose(target_tensor.ravel()))
            # dot product is proportional to cosine between vectors, given constant vector magnitudes
        scores.append(dot_product)

    closest_legal_tensor = candidates[np.argmax(scores)]
    algebraic_move = algebraic_moves[np.argmax(scores)]
    
    return closest_legal_tensor, algebraic_move


def booleanise(tensor):
    """ convert tensors probability vectors to one-hot tensor [1,64,13] -> [64,13] """
    tensor = np.squeeze(tensor) 
    one_hot_tensor = np.zeros(shape=(64,13), dtype=bool) 
    for square, piece_vector in enumerate(tensor):
        index = np.argmax(piece_vector)
        one_hot_tensor[square][index] = 1 

    return one_hot_tensor