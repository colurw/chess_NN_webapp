""" ensemble solver function called by views.py """

import numpy as np
from tensorflow import keras
from . import chess_tools_local as ct

# Load models from chess_trainer.py
model_1 = keras.models.load_model('/services/backend/webapp/ml_models/general_solver_1')
model_2 = keras.models.load_model('/services/backend/webapp/ml_models/general_solver_2')
model_3 = keras.models.load_model('/services/backend/webapp/ml_models/general_solver_3')
model_4 = keras.models.load_model('/services/backend/webapp/ml_models/general_solver_4')
ensemble = [model_1, model_2, model_3, model_4]


def ensemble_solver(onehot_board_tensor): 
    """ predicts best move using an ensemble of neural networks """
    # Initialise variables
    remove_illegal = True
    rejected = 0
    raw_total = np.zeros((64,13), dtype=float)
    legal_total = np.zeros((64,13), dtype=float)
    max_lc_score = -10000000000000
    valid_preds = 0
    valid_legal_preds = 0
    tag = 'none'
    checkmate = False

    # Get board
    fen = ct.one_hot_to_fen(onehot_board_tensor)
    # Evaluate board with every model
    for model in ensemble:
        y_predict = model(onehot_board_tensor)
        y_predict = np.array(y_predict).reshape(1,64,13)
        # Sum all predictions
        raw_total = np.add(raw_total, y_predict)
        # Remove non-sensible solo predictions
        move = ct.is_only_one_move(onehot_board_tensor, y_predict)
        if move == False:
            rejected += 1
        else:
            valid_preds += 1
            # Sum remaining legal solo predictions
            flipped_fen = ct.swap_fen_colours(fen, turn='black')
            if ct.is_move_legal(flipped_fen, move) == True or remove_illegal == False:
                valid_legal_preds += 1
                legal_total = np.add(legal_total, y_predict)
                # Get confidence score and keep record of most confident legal prediction
                c_score = ct.confid_score(y_predict)
                if c_score > max_lc_score:
                    mcf_leg_predict = y_predict
                    max_lc_score = c_score

    # Find average of all predictions
    avg_raw_predict = raw_total           # division not necessary due to argmax() in one_hot_to_...()
    # Find average of legal predictions
    avg_leg_predict = legal_total         # which removes runtime division error from focused_conf_score()

    # Apply criteria to choose best prediction
    move = ct.is_only_one_move(onehot_board_tensor, avg_raw_predict)
    flipped_fen = ct.swap_fen_colours(fen, turn='black')
    if move != False and ct.is_move_legal(flipped_fen, move) == True:
        # Use average of all ensemble predictions
        ensemble_predict = avg_raw_predict
        tag = 'avrw'
    else:
        move = ct.is_only_one_move(onehot_board_tensor, avg_leg_predict)
        if move != False and ct.is_move_legal(flipped_fen, move) == True:
            # Use average of legal ensemble predictions, if move is valid and legal
            ensemble_predict = avg_leg_predict
            tag = 'avlv'
        else:
            if valid_legal_preds >= 1:
                # Use most confident legal solo prediction
                ensemble_predict = mcf_leg_predict
                tag = 'mclv'
            else:
                try:
                    # Generate a random legal move
                    mslm_fen = ct.one_hot_to_fen(onehot_board_tensor, turn='white')
                    ensemble_predict = ct.most_similar_legal_move(mslm_fen, avg_raw_predict)
                    tag = 'mslm'
                except:
                    # No legal moves available
                    checkmate = True
    
    # Return onehot board tensor
    return(ensemble_predict, move, tag, checkmate)