''' Sources: https://github.com/EvanMcCormick1/NumpyChess/blob/main/NumpyChess.py, https://github.com/niklasf/python-chess,
and https://github.com/official-stockfish/Stockfish
'''

# Since the board's coordinates are inverted, these
# dictionaries allow some functions to convert the
# coordinates on the board to proper chess notation.
ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                 "5": 3, "6": 2, "7": 1, "8": 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                 "e": 4, "f": 5, "g": 6, "h": 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}


class GameState():
    '''Handles most information about the current gamestate. It determines the valid moves in the position, piece placement and move log.
    '''

    def __init__(self):

        # Initialises a 2D list with each piece's placement.
        # Notice how its indices start from the top left, and not from the bottom right,
        # which would be the proper chessboard configuration. Collumns also have numerical indices,
        # and not alphabetical. These are all dealt with in the Move class.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        # Dictionary containing the return values of all the different move functions.
        self.move_functions = {"P": self.pawn_moves, "N": self.knight_moves, "B": self.bishop_moves,
                               "R": self.rook_moves, "Q": self.queen_moves, "K": self.king_moves}

        # Keeps track of whose turn it is.
        self.w_to_move = True

        # Initiliases a move log that's later used for notating the moves played.
        self.move_log = []

        # Keeps track of the kings' coordinates.
        self.w_king_coord = [7, 4]
        self.b_king_coord = [0, 4]

        # Keeps track of checkmate and stalemate.
        self.checkmate = False
        self.stalemate = False

        # Stores possible en passant.
        self.ep_possible = ()

        # Sets both queenside and kingside castling for white and black to true.
        self.current_castling_rights = CastleRights(True, True, True, True)

        # Logs castling rights.
        self.castling_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                 self.current_castling_rights.wqs, self.current_castling_rights.bqs)]


    def make_move(self, move):
        '''Makes the moves on the board by changing the appropriate elements on the list board.
        '''

        # Sets the square the piece moved from to empty.
        self.board[move.start_row][move.start_col] = "--"

        # Moves the piece to its target square.
        self.board[move.target_row][move.target_col] = move.piece_moved

        # Appends the move to the move log.
        self.move_log.append(move)

        # Switches turns.
        self.w_to_move = not self.w_to_move

        # Changes kings' coordinates if they move.
        if move.piece_moved == "wK":
            self.w_king_coord[0] = move.target_row
            self.w_king_coord[1] = move.target_col
        elif move.piece_moved == "bK":
            self.b_king_coord[0] = move.target_row
            self.b_king_coord[1] = move.target_col

        # Promotes the pawn to a queen.
        # TODO: allow the user to promote to other pieces.
        if move.is_pawn_promotion:
            self.board[move.target_row][move.target_col] = move.piece_moved[0] + "Q"

        # Accounts for en passant.
        if move.is_ep:
            self.board[move.start_row][move.target_col] = "--"

        # Checks if en passant is possible and adds it to ep_possible.
        if move.piece_moved[1] == "P" and abs(move.start_row - move.target_row) == 2:
            self.ep_possible = (
                (move.start_row + move.target_row)//2, move.start_col)
        else:
            self.ep_possible = ()

        # Moves the king and the rook to castle and updates castling rights.
        if move.is_castle:
            if move.target_col - move.start_col == 2:
                self.board[move.target_row][move.target_col -
                                            1] = self.board[move.target_row][move.target_col + 1]
                self.board[move.target_row][move.target_col + 1] = "--"
            else:
                self.board[move.target_row][move.target_col +
                                            1] = self.board[move.target_row][move.target_col - 2]
                self.board[move.target_row][move.target_col - 2] = "--"
        self.update_castle_rights(move)
        self.castling_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                     self.current_castling_rights.wqs, self.current_castling_rights.bqs))


    def get_valid_moves(self):
        '''Generates all valid moves in the position by making all possible moves and
        removing those who lead to checks.
        '''
        
        temp_ep_possible = self.ep_possible
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        moves = self.possible_moves()
        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])
            self.w_to_move = not self.w_to_move
            if self.in_check():
                moves.remove(moves[i])
            self.w_to_move = not self.w_to_move
            self.undo_move()
        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True

        if self.w_to_move:
            self.castling(self.w_king_coord[0], self.w_king_coord[1], moves)
        else:
            self.castling(self.b_king_coord[0], self.b_king_coord[1], moves)
        self.ep_possible = temp_ep_possible
        self.current_castling_rights = temp_castle_rights
        return moves
    
    
    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.target_row][move.target_col] = move.piece_captured
            self.w_to_move = not self.w_to_move
            if move.piece_moved == "wK":
                self.w_king_coord[0] = move.start_row
                self.w_king_coord[1] = move.start_col
            elif move.piece_moved == "bK":
                self.b_king_coord[0] = move.start_row
                self.b_king_coord[1] = move.start_col
            if move.is_ep:
                self.board[move.target_row][move.target_col] = "--"
                self.board[move.start_row][move.target_col] = move.piece_captured
                self.ep_possible = (move.target_row, move.target_col)
            if move.piece_moved[1] == "P" and abs(move.start_row - move.target_row) == 2:
                self.ep_possible = ()
            self.castling_rights_log.pop()
            new_rights = self.castling_rights_log[-1]
            self.current_castling_right = CastleRights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)
            if move.is_castle:
                if move.target_col - move.start_col == 2:
                    self.board[move.target_row][move.target_col + 1] = self.board[move.target_row][move.target_col - 1]
                    self.board[move.target_row][move.target_col - 1] = "--"
                else:
                    self.board[move.target_row][move.target_col - 2] = self.board[move.target_row][move.target_col + 1]
                    self.board[move.target_row][move.target_col + 1] = "--"
            self.checkmate = False
            self.stalemate = False


    def possible_moves(self):
        '''Generates all possible moves in the position by checking whose turn it is and returning all move functions.
        Note that by possible, I mean all the moves that disregard any checks or pins.
        '''

        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                # Only account for the move functions of the current player.
                turn = self.board[r][c][0]
                if (turn == "w" and self.w_to_move) or (turn == "b" and not self.w_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)
        return moves


    def pawn_moves(self, r, c, moves):
        '''Generates all possible pawn moves in the position by checking
        for empty squares in front and enemy pieces on the diagonals of the pawns.
        '''

        # White's pawn moves.
        if self.w_to_move:

            # Checks if square in front is empty, then appends that square to its possible moves.
            if self.is_empty(r - 1, c):
                moves.append(Move((r, c), (r - 1, c), self.board))

                # If the pawn still hasn't moved, it can advance two squares.
                if r == 6 and self.is_empty(r - 2, c):
                    moves.append(Move((r, c), (r - 2, c), self.board))

            # Creates list with the 3 squares in front.
            front_sq = [[r - 1, c + i] for i in range(-1, 2)]

            # Looks for captures.
            self.front_squares(r, c, front_sq, moves)

        # Black's pawn moves.
        # Notice how we are now adding to the rows.
        else:
            if self.is_empty(r + 1, c):
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.is_empty(r + 2, c):
                    moves.append(Move((r, c), (r + 2, c), self.board))
            front_sq = [[r + 1, c + i] for i in range(-1, 2)]
            self.front_squares(r, c, front_sq, moves)


    def rook_moves(self, r, c, moves):
        '''Generates all possible rook moves by checking for empty square or enemy pieces on the files.
        '''

        # This list represents the "cross" the rook can move in.
        files = [[[r + i, c] for i in range(1, 8 - r)],
                 [[r - i, c] for i in range(1, r + 1)],
                 [[r, c + i] for i in range(1, 8 - c)],
                 [[r, c - i] for i in range(1, c + 1)]]

        # Iterates through the files.
        for direction in files:
            for coordinates in direction:

                # Checks if rook is inside the board's boundaries.
                if self.on_board(coordinates[0], coordinates[1]):

                    # Appends the move if the target square is empty or an enemy piece.
                    if self.is_empty(coordinates[0], coordinates[1]):
                        moves.append(
                            Move((r, c), (coordinates[0], coordinates[1]), self.board))
                    elif not self.team(coordinates[0], coordinates[1]):
                        moves.append(
                            Move((r, c), (coordinates[0], coordinates[1]), self.board))
                        break
                    else:
                        break
                else:
                    break


    def knight_moves(self, r, c, moves):
        '''Generates all possible knight moves by checking for a triangle with sides of length 1, 2, and sqrt(5),
        and then looks if they are empty or occupied by enemy pieces.
        '''
        for i in range(-2, 3):
            for j in range(-2, 3):
                if i ** 2 + j ** 2 == 5:  # Pythagorean theorem.
                    if self.on_board(r + i, c + j) == True:
                        if self.is_empty(r + i, c + j):
                            moves.append(
                                Move((r, c), (r + i, c + j), self.board))
                        elif not self.team(r + i, c + j):
                            moves.append(
                                Move((r, c), (r + i, c + j), self.board))


    def bishop_moves(self, r, c, moves):
        '''Generates all possible bishop moves similarly to the rook, but diagonally.
        '''

        # This list represents all four diagonals the bishop can move in.
        diagonals = [
            [[r + i, c + i] for i in range(1, 8)],
            [[r + i, c - i] for i in range(1, 8)],
            [[r - i, c + i] for i in range(1, 8)],
            [[r - i, c - i] for i in range(1, 8)],
        ]

        for direction in diagonals:
            for coordinates in direction:
                if self.on_board(coordinates[0], coordinates[1]):
                    if self.is_empty(coordinates[0], coordinates[1]):
                        moves.append(
                            Move((r, c), (coordinates[0], coordinates[1]), self.board))
                    elif not self.team(coordinates[0], coordinates[1]):
                        moves.append(
                            Move((r, c), (coordinates[0], coordinates[1]), self.board))
                        break
                    else:
                        break
                else:
                    break


    def queen_moves(self, r, c, moves):
        '''Since the queen works as a bishop and a rook combined, we just put both move functions together.
        '''
        self.bishop_moves(r, c, moves)
        self.rook_moves(r, c, moves)


    def king_moves(self, r, c, moves):
        '''Generates all king moves by looking for empty squares and enemy pieces on the 3x3 square surrounding the king.
        '''
        for i in range(3):
            for j in range(3):
                if self.on_board(r - 1 + i, c - 1 + j):
                    if self.is_empty(r - 1 + i, c - 1 + j) or not self.team(r - 1 + i, c - 1 + j):
                        moves.append(
                            Move((r, c), (r - 1 + i, c - 1 + j), self.board))


    def team(self, r, c):
        '''This method returns True if the given square has a ally piece on it.
        If it's empty or occupied by an enemy piece, it returns False.
        '''
        team_color = "w" if self.w_to_move else "b"
        return True if self.board[r][c][0] == team_color else False


    def is_empty(self, r, c):
        '''This method returns True if the given square is empty"
        '''
        return True if self.board[r][c] == "--" else False


    def on_board(self, r, c):
        '''Returns True if the given square is within the board's boundaries.
        '''
        return True if (r in range(0, 8) and c in range(0, 8)) else False


    def in_check(self):
        '''Returns True if the king is in check, else, False.
        '''
        if self.w_to_move:
            return self.square_under_attack(self.w_king_coord[0], self.w_king_coord[1])
        else:
            return self.square_under_attack(self.b_king_coord[0], self.b_king_coord[1])


    def square_under_attack(self, r, c):
        '''Checks if the given square is under attack by switching turns temporarily
        and calculating the opponent's possible moves.
        '''

        # Switches turns
        self.w_to_move = not self.w_to_move

        # Generates all opponent's moves
        opp_moves = self.possible_moves()

        # Switches turns back
        self.w_to_move = not self.w_to_move

        # If any opp. moves' coordinates match that of the given square, return True.
        # Else, return false.
        for move in opp_moves:
            if move.target_row == r and move.target_col == c:
                return True
        return False


    def front_squares(self, r, c, front_sq, moves):
        '''Looks for possible pawn captures in the three squares in front of the pawn
        (left diagonal, directly in front, right diagonal).
        '''

        for coordinates in front_sq:
            # Only evaluates to True for the squares diagonal to the pawn.
            if self.on_board(coordinates[0], coordinates[1]) and front_sq.index(coordinates) % 2 == 0:
                if not self.team(coordinates[0], coordinates[1]) and not self.is_empty(coordinates[0], coordinates[1]):
                    moves.append(
                        Move((r, c), (coordinates[0], coordinates[1]), self.board))
                elif (coordinates[0], coordinates[1]) == self.ep_possible:
                    moves.append(
                        Move((r, c), (coordinates[0], coordinates[1]), self.board, is_ep=True))


    def castling(self, r, c, moves):
        '''Gets all castling moves in the position by checking if the square is under
        attack and calling a function for kingside and another for queenside castling
        '''

        if self.square_under_attack(r, c):
            return

        if (self.w_to_move and self.current_castling_rights.wks) or (
                not self.w_to_move and self.current_castling_rights.bks):
            self.kgs_castling(r, c, moves)

        if (self.w_to_move and self.current_castling_rights.wqs) or (
                not self.w_to_move and self.current_castling_rights.bqs):
            self.qs_castling(r, c, moves)


    def kgs_castling(self, r, c, moves):
        '''Checks for kingside castling by seeing if the two squares next to the king are empty.
        It also makes sure the king (or these squares) are not under attack.
        '''

        if self.is_empty(r, c + 1) and self.is_empty(r, c + 2):
            if not self.square_under_attack(r, c + 1) and not self.square_under_attack(r, c + 2):
                moves.append(
                    Move((r, c), (r, c + 2), self.board, is_castle=True))


    def qs_castling(self, r, c, moves):
        '''Checks for queenside castling by seeing if the three squares next to the king are empty.
        It also makes sure the king (or these squares) are not under attack.
        '''
        if (self.is_empty(r, c - 1) and self.is_empty(r, c - 2) and self.is_empty(r, c - 3) and
                not self.square_under_attack(r, c - 1) and not self.square_under_attack(r, c - 2)):  # Only the squares the king passes by cannot be under attack
            moves.append(Move((r, c), (r, c - 2), self.board, is_castle=True))


    def update_castle_rights(self, move):
        '''Checks whether the king or the rook have moved (or captured, in case of the rook), 
        then updates current castling rights.
        '''

        # If either king has moved, it cannot castle in both directions.
        if move.piece_moved == "wK":
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == "bK":
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False

        # If the rook has moved, check which rook it is and
        # then change current castling rights accordingly.
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:
                    self.current_castling_rights.bks = False

        # Fixes bug where the king would castle with the
        # enemy piece that captured the rook.
        if move.piece_captured == "wR":
            if move.target_row == 7:
                if move.target_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.target_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.target_row == 0:
                if move.target_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.target_col == 7:
                    self.current_castling_rights.bks = False


class CastleRights():
    '''Handles castling rights through four different instance variables (bool).
    '''

    def __init__(self, wks, bks, wqs, bqs):
        '''wks: white kingside, bks: black kingside, wqs: white queenside, bqs: black queenside.
        These instance variables are used to differentiate between the four possible castling moves.
        '''

        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    '''Handles most information about the move played.
    '''

    # Inverts the board and changes collumns' coordinates from numerical to alphabetical.

    def __init__(self, start_sq, target_sq, board, is_ep=False, is_castle=False):
        '''Initialises some instance variables used to store information about the move played
        '''

        # Store start and target rows and collumns.
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.target_row = target_sq[0]
        self.target_col = target_sq[1]

        # Represents the position on the board of the moved piece.
        self.piece_moved = board[self.start_row][self.start_col]

        # Stores the position on the board of the captured piece. Empty squares are also "captured".
        self.piece_captured = board[self.target_row][self.target_col]

        # Checks if the move is a pawn promotion by looking at the rank the pawn is at.
        self.is_pawn_promotion = (self.piece_moved == "wP" and self.target_row == 0) or (
            self.piece_moved == "bP" and self.target_row == 7)

        # Checks if the move is en passant and captures the appropriate pawn.
        self.is_ep = is_ep
        if self.is_ep:
            self.piece_captured = "wP" if self.piece_moved == "bP" else "bP"

        # Stores whether the move is castle.
        self.is_castle = is_castle

        # This moveID is used later to differentiate between moves. This is based on
        # the fact that, in a given position, only one piece can go from a specific square to another.
        self.moveID = self.start_row * 1000 + self.start_col * \
            100 + self.target_row * 10 + self.target_col


    def __eq__(self, other):
        '''Overrides __eq__ to allow proper equivalence between moves with moveID.
        '''

        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def chess_notation(self):
        '''Calls the method "convert" on the start and target rows and collumns,
        converting the move to the appropriate chess notation.
        '''

        return self.convert(self.start_row, self.start_col) + self.convert(self.target_row, self.target_col)


    def convert(self, r, c):
        '''Uses the inverted dict initialised previously to convert
        collumns to files and rows to ranks as in proper chess notation.
        '''

        return cols_to_files[c] + rows_to_ranks[r]


    def unconvert(self, r, c):

        return (ranks_to_rows[r], files_to_cols[c])
