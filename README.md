Title: 

Chess50


Description:

This application runs a chess game that can either be played between two players on the same machine or between a player and a chess engine (Stockfish). It also features a small SQL database from which the player can select specific games to be shown on the screen and the ability to read FEN records.


Basics:

Player vs. Player:
    Each player can move by clicking on a piece and dragging it to a valid square. When a move is made, it is added to a move log on the right side of the screen. To restart the game, press "r".

Player vs. Engine:
    To play against an engine, simply play a move and press either SHIFT + 1, SHIFT + 2 or SHIFT + 3.
    If you want to play as black, play white's first move and then follow the same steps.
    There are a few differences between which keys you press:
        Shift + 1: weaker, low-depth, engine. Easier difficulty.
        Shift + 1: stronger, mid-depth, engine. Medium difficulty.
        Shift + 3: strongest, high-depth, engine. Hard difficuly.
    You are free to alternate between these keys as you wish.


Study games:

Select from SQL database:
    With this game, comes a SQL database with four PGN games. It contains one table called games with the following fields and data types:

    sqlite> .schema
    CREATE TABLE games (id INTEGER, event TEXT NOT NULL, site TEXT, date TEXT NOT NULL, round INT, white TEXT NOT NULL, black TEXT NOT NULL, result TEXT, white_title TEXT, black_title TEXT, white_elo INT, black_elo INT, eco TEXT, opening TEXT, variation TEXT, white_fide_id INT, black_fide_id INT, event_date TEXT, pgn TEXT NOT NULL, PRIMARY KEY(id));

    Excluding pgn due to its size, we have:
    
    1|Hoogovens Group A|Wijk ann Zee NED|1999.01.20|4|Kasparov, Garry|Topalov, Veselin|1-0|?|?|2812|2700|B07|?|?|?|?|1999.01.16
    2|WCh 2021|Dubai UAE|2021.12.03|6|Carlsen, Magnus|Nepomniachtchi, Ian|1-0|GM|GM|2855|2782|D02|Queen's pawn game|?|1503014|4168119|2021.11.26
    4|WCh 2018|London ENG|2018.11.15|5|Caruana, Fabiano|Carlsen, Magnus|1/2-1/2|GM|GM|2832|2835|B31|Sicilian|Nimzovich-Rossolimo attack, Gurgenidze variation|2020009|1503014|2018.11.09
    5|World Championship 35th-KK5|Lyon/New York|1900.??.??|20|Kasparov, Gary|Karpov, Anatoly|1-0|?|?|2800|2730|C92|?|?|?|?|?

    To search for a game, type [column name] = "[value]" on the top input box. For example, if we want the game in which the Sicilian opening was played, we can search on the top inpux box 'opening = "sicilian"'.

    To run the query, press ENTER. To run through the moves, press the right arrow key. Whenever you are done with your study, press "r".

Read FEN record:
    You can paste a FEN record on the bottom input box by clicking on the box and pressing the key "v". To read it, press SHIFT + ENTER. You can continue to play from this position normally. Press "r" when you're done. You can easily find FEN records online or create them on websites such as lichess.org. (E. g. rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2)

Extra:
    To get the engine's evaluation of a position, press either SHIFT + 4 or SHIFT + 5. The first runs a lower depth analysis, while the latter runs a higher depth analysis. Just click on the screen when you're done.


VIDEO: https://youtu.be/s-h_J5onqVE

LINK TO GOOGLE DRIVE: https://drive.google.com/file/d/1JYBLYMQ6qq-V-xckCKI-H4Tifu8etXER/view?usp=sharing
