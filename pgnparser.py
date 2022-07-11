'''Reads a game from a PGN string with python-chess and io. 
Source: https://python-chess.readthedocs.io/en/v1.7.0/pgn.html#parsing
'''

import chess.pgn
from gamestate import *
import io


def pgn_parser(query):
    '''Reads a game from a PGN string.
    '''
    
    # Initialises the PGN string and reads the game.
    pgn = io.StringIO(query)
    game = chess.pgn.read_game(pgn)

    # Iterates through all moves and plays them on the board.
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
        pgn_moves = str(board.move_stack) # Initialises a string with all the moves in the mainline.
        
    # Removes some unwanted characters, leaving only the actual moves.
    unwanted_s = (("Move.from_uci", ""), ("(", ""), (")", ""), ("[", ""), ("]", ""), ("'", ""))
    for r in unwanted_s:
        pgn_moves = pgn_moves.replace(*r)
    
    # Turns the string into a list.
    pgn_moves = str_to_list(pgn_moves)

    return pgn_moves


def str_to_list(string):
    li = list(string.split(", "))
    return li

   
def pgn_interpreter(pgn_moves, index):
    '''Unconverts the move from proper chess notation to one that matches that of our board.
    This method is used to parse PGN files.
    '''
    
    return [pgn_unconvert(pgn_moves[index][1], pgn_moves[index][0]), pgn_unconvert(pgn_moves[index][3], pgn_moves[index][2])]


def pgn_unconvert(r, c):
    '''Accesses the inverted dictionaries in gamestate to unconvert the moves given by the PGN file.
    '''
    
    return (ranks_to_rows[r], files_to_cols[c])