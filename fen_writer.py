'''
Generates FEN from the current gamestate. A FEN record contains six fields:

    Piece placement, active color, castling availability, 
    en passant target square, halfmove clock, and fullmove number.
    
Each function handles one of these fields.
'''

def fen_generator(board, turn, wks, wqs, bks, bqs, piece, start, target, letter, halfmove_clock, fullmove_number):
    '''Puts all the fields together to generate a FEN string.
    '''
    
    fen = ""
    fen = piece_placement(fen, board).replace("/", "", 1) + active_color(fen, turn) + castling_availability(wks, wqs, bks, bqs) + ep_target_square(fen, turn, piece, start, target, letter) + halfmove(fen, halfmove_clock) + fullmove(fen, fullmove_number)
    return fen

def piece_placement(fen, board):
    '''Handles piece placement by iterating through the board
    and checking what's in each coordinate.
    '''
    
    counter = 0
    
    for row in board:
        if counter > 0:
                fen += str(counter)
                counter = 0
        fen += "/"
        
        for col in row:
            string = ""
            
            if col == "--":
                counter += 1
                
            elif col[0] == "b":
                if counter > 0:
                    fen += str(counter)
                    counter = 0
                string = col[1].lower()
                
            elif col[0] == "w":
                if counter > 0:
                    fen += str(counter)
                    counter = 0
                string = col[1]
    
            fen += string
    
    if counter > 0:
        fen += str(counter)
        
    return fen

def active_color(fen, turn):
    '''Checks whose turn it is.
    '''
    
    if turn:
        fen += " w "
    else:
        fen += " b "
        
    return fen

def castling_availability(wks, wqs, bks, bqs):
    '''Checks if castling is possible by iterating through "KQkq"
    and removing any letters that represent impossible moves 
    (e. g. K stands for white kingside castling)
    '''
    
    castle = ""
    temp_castle = "KQkq"
    castling_side = [wks, wqs, bks, bqs]
    
    for i in range(len(castling_side)):
        if castling_side[i]:
            castle += temp_castle[i]
            
    if castle == "":
        castle += "-"
    
    return castle

def ep_target_square(fen, turn, piece, start, target, letter):
    '''If a pawn has just made a two-square move, this is the position "behind" the pawn.
    '''
    
    pawn_moved_two_squares = piece[1] == "P" and abs(start - target) == 2
    
    if pawn_moved_two_squares and not turn:
        ep = letter + str(start - 3)
    elif pawn_moved_two_squares and turn:
        ep = letter + str(start + 5)
    else:
        ep = "-"
        
    fen += (" " + str(ep) + " ")
    
    return fen

def halfmove(fen, halfmove_clock):
    '''The number of halfmoves since the last capture or pawn advance.
    '''
    
    fen += (str(halfmove_clock) + " ")
    
    return fen

def fullmove(fen, fullmove_number):
    '''The number of the full move. 
    It starts at 1, and is incremented after Black's move.
    '''
    
    fen += str(fullmove_number)
    
    return fen


