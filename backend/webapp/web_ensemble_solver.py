""" ensemble solver function called by views.py """

import numpy as np
from tensorflow import keras
from . import chess_tools_local as ct

# Load models from chess_trainer.py
model_1 = keras.models.load_model('/services/backend/webapp/ml_models/general_solver_1')
model_2 = keras.models.load_model('/services/backend/webapp/ml_models/general_solver_2')
# model_3 = keras.models.load_model('/services/backend/webapp/ml_models/general_solver_3')
# model_4 = keras.models.load_model('/services/backend/webapp/ml_models/general_solver_4')
model_5 = keras.models.load_model('/services/backend/webapp/ml_models/whole_game_3')
ensemble = [model_1, model_2, model_5]


def ensemble_solver(onehot_board_tensor): 
    """ predicts best move using an ensemble of neural networks """
    raw_total = np.zeros((64,13), dtype=float)
    legal_total = np.zeros((64,13), dtype=float)
    max_lc_score = float('-inf')
    legal_count = 0
    tag = 'none'
    checkmate = False
    fen = ct.one_hot_to_fen(onehot_board_tensor)
    allowed_tensors, allowed_moves = ct.find_legal_moves(fen)

    # Evaluate board with every model
    for model in ensemble:
        y_predict = model(onehot_board_tensor)
        y_predict = np.array(y_predict).reshape(1,64,13)
        # Sum all predictions
        raw_total = np.add(raw_total, y_predict)

        # Compare prediction to all possible legal moves
        y_predict_bool = ct.booleanise(y_predict)
        for i, tensor in enumerate(allowed_tensors):
            if np.all(y_predict_bool == tensor):
                legal_total = np.add(legal_total, y_predict)
                legal_count += 1

            # Get confidence score and keep record of most confident legal prediction
            c_score = ct.confidence_score(y_predict)
            if c_score > max_lc_score:
                mcf_leg_predict = y_predict
                max_lc_score = c_score

    # Find average of all predictions and all legal predictions 
    avg_raw_predict = raw_total                                                 
    avg_leg_predict = legal_total   # no need to divide due to later argmax()'s   

    # Convert from probability vectors to one-hot vectors
    avg_raw_bool = ct.booleanise(avg_raw_predict)  
    avg_legal_bool = ct.booleanise(avg_leg_predict)   


    # Apply decision criteria to choose best prediction
    for i, tensor in enumerate(allowed_tensors):
        if np.all(tensor == avg_raw_bool):
            # Use average of all ensemble predictions
            ensemble_predict = avg_raw_predict
            tag = 'avrw'
            ai_move = allowed_moves[i]
            checkmate = False

            return(ensemble_predict, ai_move, tag, checkmate)

    for i, tensor in enumerate(allowed_tensors):
        if np.all(tensor == avg_legal_bool):
            # Use average of legal ensemble predictions
            ensemble_predict = avg_leg_predict
            tag = 'avlg'
            ai_move = allowed_moves[i]
            checkmate = False

            return(ensemble_predict, ai_move, tag, checkmate)

    if legal_count >= 1:
        mcf_leg_bool = ct.booleanise(mcf_leg_predict)
        for i, tensor in enumerate(allowed_tensors):
            if np.all(tensor == mcf_leg_bool):
                # Use most confident legal solo prediction
                ensemble_predict = mcf_leg_predict
                tag = 'mclg'
                ai_move = allowed_moves[i]
                checkmate = False

                return(ensemble_predict, ai_move, tag, checkmate)

    else:
        try:
            # Find most similar legal move to average of raw predictions
            ensemble_predict, ai_move = ct.most_similar_move(allowed_tensors, avg_raw_predict, allowed_moves)
            tag = 'mslm'
            checkmate = False

            return(ensemble_predict, ai_move, tag, checkmate)

        except:
            # No legal moves available
            ensemble_predict = None
            ai_move = None
            tag = 'chkm'
            checkmate = True

            return(ensemble_predict, ai_move, tag, checkmate)

    