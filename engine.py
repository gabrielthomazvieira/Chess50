'''Handles engine analysis with stockfish and python-chess. 
Sources: https://python-chess.readthedocs.io/en/v1.7.0/engine.html, https://blog.propelauth.com/chess-analysis-in-python/, 
and https://github.com/official-stockfish/Stockfish.
'''

import chess
import chess.engine
from gamestate import *


# Stockfish's location
engine = chess.engine.SimpleEngine.popen_uci("/usr/local/bin/stockfish")


def analyze_position(fen, num_moves_to_return=1, depth_limit=None, time_limit=None):
    '''Analyzes the board through a FEN string and returns a dictionary with three
    values:
        mate_score - number of moves to mate. Positive for white, negative for black.
        centipawn_score - centipawn score (1 cp = 1/100th of a pawn). Positive for white, negative for black.
        pv - sequence of moves suggested by the engine.
    
    These values rely on the following parameters:
        fen - FEN string representing the board's configuration.
        num_moves_to_return - he number of move sequences the engine should suggest.
        depth_limit - the depth each sequence goes to.
        time_limit - the engine stops analyzing moves when it hits this time limit,
    '''
    
    # Limits our search.
    search_limit = chess.engine.Limit(depth=depth_limit, time=time_limit)
    
    # Creates the board from FEN.
    board = chess.Board(fen)
    
    # Represents the information we want from our analysis.
    infos = engine.analyse(board, search_limit, multipv=num_moves_to_return)
    
    # Returns a dictionary containing all these values.
    return [format_info(info) for info in infos]
   
def format_info(info):
    '''Called by analyze_position to initiliase a dict
    containing the engine's analysis.
    '''
    
    # Always look from White's perspective.
    score = info["score"].white()
    
    # Initialises a dictionary with mate_score, centipawn_score and pv.
    mate_score = score.mate()
    centipawn_score = score.score()
    return {
        "mate_score": mate_score,
        "centipawn_score": centipawn_score,
        "pv": format_moves(info["pv"]),
    }


def format_moves(pv):
    '''Converts the move class to a standard string.
    '''
    
    return [move.uci() for move in pv]


def eng_interpreter(eng_line): 
    '''Unconverts the move from proper chess notation to one that matches that of our board.
    '''
    
    return eng_unconvert(eng_line["pv"][0][1], eng_line["pv"][0][0]), eng_unconvert(eng_line["pv"][0][3], eng_line["pv"][0][2])


def eng_unconvert(r, c):
    '''Accesses the inverted dictionaries in gamestate to unconvert the moves given by the engine.
    '''
    return (ranks_to_rows[r], files_to_cols[c])