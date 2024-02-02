import numpy as np
import cv2
from PIL import Image,ImageDraw, ImageFont
import math
import chess
import random


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
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
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
            draw.text((j, i), piece, fill=(0,0,0,255), align='center', font=ImageFont.truetype('/services/djangoapp/src/django_wrapper/webapp/pieces_font/FreeSerif.ttf', 50))
            index = index + 1
    # Save image
    # pil_image.save("board.png")
    return pil_image


def reshape_output(y_data, n_outputs):
    """ reshapes output: ndarray[puzzle, square, piece_ohe_vector] into: list[square, ndarray[puzzle, piece_ohe_vector]] """
    list = []
    for index in range(n_outputs):
        y = []
        for puzzle in y_data:
                square = puzzle[index]
                y.append(square)
        z = np.array(y, dtype='bool')
        list.append(z)
    return list


def index_to_algebraic(square):
    """ Converts square index number (0-63) to algebraic notation (a8-h1) """
    letter = 'abcdefgh'
    letter = letter[(square % 8)]
    number = 8 - math.floor(square/8)
    return letter + str(number)


def is_only_one_move(x_array, y_array, algebraic=True):
    """ Compares boards to check exactly one piece has moved and returns relevant squares, else 'False' """
    decoding = {0:'\u265C', 1:'\u265E', 2:'\u265D', 3:'\u265B', 4:'\u265A', 5:'\u265F', 6:'\u2656', 7:'\u2658', 8:'\u2657', 9:'\u2655', 10:'\u2654', 11:'\u2659', 12:' '}
    x_board = []
    y_board = []
    move_1 = ''
    move_2 = ''
    # Convert one-hot x_array into list of pieces
    arr1 = x_array.reshape(64,13)
    for i, piece_vector in enumerate(arr1):
        index = np.argmax(piece_vector)
        piece = decoding[index]
        x_board.append(piece)
    # Convert categorical probabilities of y_array into list of pieces
    arr2 = y_array.reshape(64,13)
    for j, piece_vector in enumerate(arr2):
        index = np.argmax(piece_vector)
        piece = decoding[index]
        y_board.append(piece)
    # Compare lists to check only one piece has moved
    count = 0
    for square in range(len(x_board)):
        if x_board[square] != y_board[square]:
            # Record relevant squares
            if count == 0:
                move_1 = index_to_algebraic(square)
                square_1 = square
            if count == 1:
                move_2 = index_to_algebraic(square)
                square_2 = square
            count += 1    
    if count == 2:   
        output = [move_1, move_2]
        if algebraic == False:
            output = [square_1, square_2]
    else:
        output = False
    return output


def is_move_legal(FEN, moves):
    """ checks if an algebraic notation move is legal according to chess rules, using python-chess library """
    board = chess.Board(FEN)
    alt_1 = moves[0] + moves[1]
    alt_2 = moves[1] + moves[0]
    if chess.Move.from_uci(alt_1) in board.legal_moves:
        boolean = True
    elif chess.Move.from_uci(alt_2) in board.legal_moves:
        boolean = True
    else:
        boolean = False
    return boolean


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
    # remove empty square category
    x_array = np.delete(x_array, 12, axis=2)
    y_array = np.delete(y_array, 12, axis=2)
    # get total of each piece type
    x_totals = x_array.sum(axis=1)
    y_totals = y_array.sum(axis=1)
    # check if any piece total has increased
    sub = np.subtract(x_totals, y_totals)
    boolean = np.any(sub < 0)
    return boolean


def confid_score(y_array, exp=False):
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
    #print('cs:', total)
    return total


def focused_confid_score(x_array, y_array, exp=False):
    """ Evaluates the degree of confidence in a prediction, based on the two active squares only """
    moves = is_only_one_move(x_array, y_array, algebraic=False)
    if moves == False:
        total = 0.0
    else:
        total = 0.0
        board = y_array.reshape(64,13)
        for square, piece_vector in enumerate(board):
            if square == moves[0] or square == moves[1]:
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
                    others = np.sum(square) - highest
                certainty = highest - others
                total += certainty
    #print('cs:', total)
    return total


def random_legal_move(FEN):
    """ Returns a random legal move in alegebraic notation, usimg python-chess library """
    board = chess.Board(FEN)
    moves = []
    for move in board.legal_moves:
        moves.append(move)
    rand_num = random.sample(range(len(moves)), 1)
    return moves[rand_num[0]]


def update_one_hot(array, alg_move):
    """ Updates one-hot array with an algebraic notation move """
    board = one_hot_decode(array)
    move = str(alg_move)  ## e.g. 'e1f1'
    dict = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
    x_from = dict[move[0]]
    y_from = 8-int(move[1])
    x_to = dict[move[2]]
    y_to = 8 - int(move[3])
    piece = board[y_from][x_from]
    board[y_from][x_from] = '.'
    board[y_to][x_to] = piece
    # Promote pawn on last rank to queen
    if piece == 'p' and y_to == 0:
        board[y_to][x_to] = 'q'
    if piece == 'P' and y_to == 7:
        board[y_to][x_to] = 'Q'
    array = one_hot_encode(board)
    return array


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


def im_concat_2(im1, im2):
    """ Stitches two images horizontally """
    im = Image.new('RGB', (im1.width + im2.width, im1.height))
    im.paste(im1, (0, 0))
    im.paste(im2, (1*im1.width, 0))
    return im


def im_concat_3(im1, im2, im3):
    """ Stitches three images horizontally """
    im = Image.new('RGB', (im1.width + im2.width + im3.width, im1.height))
    im.paste(im1, (0, 0))
    im.paste(im2, (1*im1.width, 0))
    im.paste(im3, (2*im1.width, 0))
    return im


def im_concat_4(im1, im2, im3, im4):
    """ Stitches four images vertically """
    im = Image.new('RGB', (im1.width, im1.height + im2.height + im3.height + im4.height))
    im.paste(im1, (0, 0))
    im.paste(im2, (0, 1*im1.height))
    im.paste(im3, (0, 2*im1.height))
    im.paste(im4, (0, 3*im1.height))
    return im
