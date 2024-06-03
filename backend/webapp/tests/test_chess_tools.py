import numpy as np
import pytest
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
import chess_tools_local as ct


FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

ascii_board = np.array([['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
                        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
                        ['.', '.', '.', '.', '.', '.', '.', '.'],
                        ['.', '.', '.', '.', '.', '.', '.', '.'],
                        ['.', '.', '.', '.', '.', '.', '.', '.'],
                        ['.', '.', '.', '.', '.', '.', '.', '.'],
                        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
                        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']])


def test_fen_to_ascii():
    assert np.all(ct.fen_to_ascii(FEN) == ascii_board)   


def test_one_hot_encode_and_decode():
    one_hot = ct.one_hot_encode(ascii_board)
    decoded_board = ct.one_hot_decode(one_hot)
    assert one_hot.shape == (64,13)
    assert np.all(ascii_board == decoded_board)


def test_one_hot_to_fen():
    one_hot = one_hot = ct.one_hot_encode(ascii_board)
    fen = ct.one_hot_to_fen(one_hot, turn='white')
    assert fen == 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'


@pytest.mark.parametrize('test_input,expected', [(0, 'a8'), (1, 'b8'), (62, 'g1'), (63, 'h1')])
def test_index_to_algebraic(test_input, expected):
    assert ct.index_to_algebraic(test_input) == expected


def test_is_move_legal():
    # standard board - white move
    fen = '4k3/8/8/8/8/8/8/4K3 w KQkq - 0 1'
    assert ct.is_move_legal(fen, ['e1','d1']) == True
    assert ct.is_move_legal(fen, ['d1','e4']) == False

    # standard board - black move
    fen = '4k3/8/8/8/8/8/8/4K3 b KQkq - 0 1'
    assert ct.is_move_legal(fen, ['e8','f7']) == True
    assert ct.is_move_legal(fen, ['e8','g8']) == False

    # flipped board - black move
    fen = '3K4/8/8/8/8/8/8/3k4 b KQkq - 0 1'
    assert ct.is_move_legal(fen, ['d1','e1']) == True
    assert ct.is_move_legal(fen, ['d1','e4']) == False

    # flipped board - white move
    fen = '3K4/8/8/8/8/8/8/3k4 w KQkq - 0 1'
    assert ct.is_move_legal(fen, ['d8','c7']) == True
    assert ct.is_move_legal(fen, ['d8','h8']) == False
    

def test_update_one_hot():
    # apply white kingside castling
    fen = 'R2K1B1R/1PPQ1PP1/P1N3B1/3N3P/3P1n1p/1p4n1/pbpp1pp1/1krq1b1r w KQkq - 0 1'
    ascii_board = ct.fen_to_ascii(fen)
    one_hot = ct.one_hot_encode(ascii_board)
    updated_one_hot = ct.update_one_hot(one_hot, 'd8a8')
    updated_fen = ct.one_hot_to_fen(updated_one_hot, turn='black')
    assert updated_fen == '1KR2B1R/1PPQ1PP1/P1N3B1/3N3P/3P1n1p/1p4n1/pbpp1pp1/1krq1b1r b KQkq - 0 1'

    # advance black pawn
    fen = '8/8/8/8/8/8/p7/8 w KQkq - 0 1'
    ascii_board = ct.fen_to_ascii(fen)
    one_hot = ct.one_hot_encode(ascii_board)
    updated_one_hot = ct.update_one_hot(one_hot, 'a2a3')
    updated_fen = ct.one_hot_to_fen(updated_one_hot, turn='white')
    assert updated_fen == '8/8/8/8/8/p7/8/8 w KQkq - 0 1'


def test_find_legal_moves():
    fen = 'R2K4/P7/8/8/8/8/8/8 w KQkq - 0 1'
    candidates, algebraic_moves = ct.find_legal_moves(fen)
    assert len(candidates) == 10
    assert len(algebraic_moves) == 10   # 9 moves if castlings not found
    

def test_most_similar_move():
    fen = 'R2K4/P7/8/8/8/8/8/8 w KQkq - 0 1'
    candidates, algebraic_moves = ct.find_legal_moves(fen)
    ascii_board = ct.fen_to_ascii(fen)
    one_hot = ct.one_hot_encode(ascii_board)
    target_tensor = ct.update_one_hot(one_hot, 'a7a6')
    closest_legal_tensor, algebraic_move = ct.most_similar_move(candidates, target_tensor, algebraic_moves)
    assert np.all(closest_legal_tensor == target_tensor)


