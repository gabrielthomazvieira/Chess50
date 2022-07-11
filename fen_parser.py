'''Parses a FEN string. 
Source: https://github.com/tlehman/fenparser/blob/master/fenparser.py
'''

from itertools import chain
import re
       
class FenParser():
    '''Handles FEN parsing. Also returns some variables used in main
    to keep track of the gamestate.
    '''
    
    def __init__(self, fen_str):
        self.fen_str = fen_str


    def parse(self):
        '''Uses regex to read the FEN string and 
        convert it to a 2d list representing the board.
        '''
        
        # Removes any spaces or dashes
        ranks = self.fen_str.split(" ")[0].split("/")
        
        # Initialises a 2d list representing the board
        board = [self.parse_rank(rank) for rank in ranks]
        
        # Iterates through the board and changes its elements
        # to match those in gamestate.py.
        for row in range(8):
            for col in range(8):
                if board[row][col].islower():
                    board[row][col] = "b" + board[row][col].upper()
                elif board[row][col].isupper():
                    board[row][col] = "w" + board[row][col]
                else:
                    board[row][col] = "--"
        return board


    def parse_rank(self, rank):
        rank_re = re.compile("(\d|[kqbnrpKQBNRP])")
        piece_tokens = rank_re.findall(rank)
        pieces = self.flatten(map(self.expand_or_noop, piece_tokens))
        return pieces


    def flatten(self, lst):
        return list(chain(*lst))


    def expand_or_noop(self, piece_str):
        piece_re = re.compile("([kqbnrpKQBNRP])")
        retval = ""
        if piece_re.match(piece_str):
            retval = piece_str
        else:
            retval = self.expand(piece_str)
        return retval


    def expand(self, num_str):
        return int(num_str)*" "


    def find_nth(self, string, char, n):
        '''Looks for the nth repetition
        of a character inside a string.
        '''
        
        index = string.find(char)
        while index >= 0 and n > 1:
            index = string.find(char, index + len(char))
            n -= 1
        return index
    
    
    '''The four methods below search for the special fields in
    the FEN string and return their value.
    '''   
    
    def turn(self):
        start = self.find_nth(self.fen_str, " ", 1)
        turn = self.fen_str[start + 1]
        return turn


    def castle(self):
        start = self.find_nth(self.fen_str, " ", 2)
        end = self.find_nth(self.fen_str, " ", 3)
        castle = self.fen_str[start + 1:end]
        return castle
    
    
    def halfmove_clock(self):
        start = self.find_nth(self.fen_str, " ", 4)
        end = self.find_nth(self.fen_str, " ", 5)
        halfmove_clock = int(self.fen_str[start + 1:end])
        return halfmove_clock
    
    
    def fullmove_number(self):
        start = self.find_nth(self.fen_str, " ", 5)
        fullmove_number = int(self.fen_str[start + 1:])
        return fullmove_number