The application has 8 files:

    chessboard.py - handles most drawings, texts and animations.

    engine.py - handles engine analysis with stockfish and python-chess.

    fen_parser.py - reads a FEN record, which is inputted by the user in the form of a string (E. g. rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2)

    fen_writer.py - generates a FEN file after each move.

    games.db - SQL database containing 4 PGN files and their headers.

    gamestate.py - handles most move functions and the current board.

    main.py - main file; runs the code.

There are a few basic parts in this game:

    1. Move generation and validation;

    2. Drawing the board;

    3. Interpreting the engine and reading FEN and PGN

    4. Selecting PGN from SQL database.

1. Move Generation and validation:

    Reading pygame's documentation, I saw that it's good practice to create classes to handle different aspects of your game. With that in mind: 
    
        GameState handles most information about the current gamestate. It also determines the valid moves in the position, piece placement and move log. To generate the moves, it runs each piece's move function and then groups them all together in a dictionary. This dictionary is used in the possible_moves method to return a list containing all the possible moves in the condition. Notice that by possible, I mean those who disregard any checks or castling rights. To validate these moves, it makes each one of them, sees if it results in the king being in check, and removes those that do. If there are no valid moves, then the player is either in checkmate or stalemate. In the end, we have a list containing all the valid moves in this position.

        CastleRights handles castling rights through four different instance variables. They are all boolean values that are updated by methods in GameState. The program keeps track of castling rights through a specific list, to which a new tuple with four boolean values is appended after each move.

        The Move class handles most information about each move. A move is caracterized by its start and target square. It also holds some information on whether it is en passant or castle.

2. Drawing the board

    To draw the board, I thought it would be a good idea to use pygame's library, since it has many built in methods for this purpose. I considered creating a webpage with flask, but I didn't fell as comfortable working with flask to do so.

3. Interpreting the engine

    Regarding the engine, the program simply gives a FEN record to it. In return, it gives a list containing all the moves we asked for. However, these moves are in a different notation to that of our board (since it's a 2d list, it's rows and collumns are inverted), so that's why we need to invert these values with a inverted dict. The same can be said about the PGN, which is parsed by python-chess and converted to our board's notation.

4. Selecting PGN from SQL database

    I could not find a way to automatically add data in pgn files to SQL database, so the database isn't that big for this reason.