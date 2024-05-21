""" Receives board setup and player's move data posted from play.html.  Returns a http response. """

from django.shortcuts import render
from django.http import HttpResponse
from io import BytesIO
import base64
import pickle
import numpy as np
from . import chess_tools_local as ct 
from . import web_ensemble_solver as es


def check_input(move):
    """ checks whether move is of format 'a2a3' """
    valid_chars = "12345678abcdefghABCDEFGH"
    if type(move) == str:
        if (len(move) != 4
                or move[0].isalpha() == False 
                or move[1].isnumeric() == False 
                or move[2].isalpha() == False 
                or move[3].isnumeric() == False 
                or set(move) - set(valid_chars) != set()):
            return 'fail'
    else:
        return 'fail'


def check_input_q(move):
    """ checks whether move is of format 'a7a8q' to allow queening """
    valid_chars = "12345678abcdefghqABCDEFGHQ"
    if type(move) == str:
        if (len(move) != 5
                or move[0].isalpha() == False 
                or move[1].isnumeric() == False 
                or move[2].isalpha() == False 
                or move[3] != '8' 
                or move[4] != 'q'
                or set(move) - set(valid_chars) != set()):
            return 'fail'
    else:
        return 'fail'


def image_to_base64(image):
    """ converts image to base64 string """
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue())
    img_str = img_str.decode("utf-8")
    
    return img_str


def fen_to_base64(fen):
    """ converts FEN to base64 string """
    board = ct.fen_to_ascii(fen)
    onehot = ct.one_hot_encode(board)        
    image = ct.one_hot_to_png(onehot)
    img_str = image_to_base64(image)
    
    return img_str


def play(request):
    """ called by urls.py when /play.html is requested by browser, returns http response """
    move = ''
    ai_move = ''
    tag = ''
    valid_input = False
    fen = request.session.get('session_fen', '8/8/8/8/8/8/8/8 w KQkq - 0 1')

    # If opening option 1 selected, set FEN to Spassky-Fischer 1972 and update browser
    if request.POST.get('option1') == 'Go':
        fen = '1KR2B1R/1PPQ1PP1/P1N3B1/3N3P/3P1n1p/1p4n1/pbpp1pp1/1krq1b1r w KQkq - 0 1'
        request.session['session_fen'] = fen
        move = ' ...g3f5 suggested'  
        image64 = fen_to_base64(fen)

        return render(request, "play.html", {'ai_move': ai_move, 'move': move, 'image64': image64, 'fen': fen, 'tag': tag})

    # If opening option 2 selected, set FEN to King's Indian Defence
    elif request.POST.get('option2') == 'Go':
        fen = '1KR1QB1R/PPPB2PP/2N2N2/3PPP2/3p4/1pn1p3/pbp2ppp/1kr1qbnr w KQkq - 0 1'
        request.session['session_fen'] = fen
        move = ' ...play g1f3 to finish opening'
        image64 = fen_to_base64(fen)

        return render(request, "play.html", {'ai_move': ai_move, 'move': move, 'image64': image64, 'fen': fen, 'tag': tag})
    
    # If opening option 3 selected, set FEN to Nimzo-Indian Defence
    elif request.POST.get('option3') == 'Go':
        fen = '1KR1QB1R/PPP3PP/2NPBN2/4PPb1/4pp2/2np4/ppp3pp/1kr1qbnr w KQkq - 0 1'
        request.session['session_fen'] = fen
        move = ' ...play g1f3 to finish opening'   
        image64 = fen_to_base64(fen)

        return render(request, "play.html", {'ai_move': ai_move, 'move': move, 'image64': image64, 'fen': fen, 'tag': tag})
    
    # If opening option 4 selected, set FEN to Ruy Lopez
    elif request.POST.get('option4') == 'Go':
        fen = '1K1RQBNR/PPP1P1PP/2N2PB1/3P4/3p2p1/2n2n1p/pppbpp2/1kr1qb1r w KQkq - 0 1'
        request.session['session_fen'] = fen
        move = ' ...play e2e4 to finish opening'
        image64 = fen_to_base64(fen)

        return render(request, "play.html", {'ai_move': ai_move, 'move': move, 'image64': image64, 'fen': fen, 'tag': tag})

    # If player move posted, record move
    elif request.method == "POST":
        move = request.POST.get('human_move')
        
        # Check input string from play.html is valid, eg: 'b3c4' or 'd7d8q'
        if check_input(move) == 'fail' and check_input_q(move) == 'fail':
            
            return HttpResponse("Invalid input! <br><br> \
                                 use format: 'a2a3', or 'a7a8q' if promoting a pawn")
              
        else:
            valid_input = True 
            # Check move is legal according to chess rules
            fen = request.session.get('session_fen')
            moves = [str(move[:2].lower()), str(move[2:].lower())]
            # ..from black's perspective 
            flipped_fen = ct.swap_fen_colours(fen, turn='white') 
            if ct.is_move_legal(flipped_fen, moves) == False:
                
                return HttpResponse("Illegal move detected! <br><br> \
                                     NB: <br> undoing moves with 'back' button is cheating! <br> \
                                     if promoting a pawn, enter 'a7a8q'")

        # Load FEN
        fen = request.session.get('session_fen')
        # Convert FEN to one-hot tensor and apply human move
        board = ct.fen_to_ascii(fen)
        onehot = ct.one_hot_encode(board)
        if valid_input == True:                
            onehot = ct.update_one_hot(onehot, move)
        # Get ensemble prediction of best computer move
        onehot = np.array(onehot).reshape(1,64,13)
        onehot, ai_move, tag, checkmate = es.ensemble_solver(onehot)
        # Detect win condition
        if checkmate == True:

            return HttpResponse("Checkmate!")

        # Save updated FEN
        fen = ct.one_hot_to_fen(onehot)
        request.session['session_fen'] = fen
        # Convert onehot tensor to board image then convert image to string
        image = ct.one_hot_to_png(onehot)
        image64 = image_to_base64(image)
        
        return render(request, "play.html", {'ai_move': ai_move, 'move': move, 'image64': image64, 'fen': fen, 'tag': tag})

    # Convert seleceted opening FEN to one-hot tensor
    board = ct.fen_to_ascii(fen)
    onehot = ct.one_hot_encode(board)        
    # Draw image and save as string
    image = ct.one_hot_to_png(onehot)
    image64 = image_to_base64(image)

    return render(request, "play.html", {'ai_move': ai_move, 'move': move, 'image64': image64})