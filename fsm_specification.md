Game State Machine Specification

The server will use a few different states to keep track of what is happening in the game.

The states are:

INIT

WAITING_FOR_PLAYERS

GAME_START

PLAYER_TURN

EVALUATE_MOVE

GAME_OVER

CLEANUP

State Diagram

stateDiagram-v2
    [*] --> INIT
    INIT --> WAITING_FOR_PLAYERS: Server starts

    WAITING_FOR_PLAYERS --> WAITING_FOR_PLAYERS: First player joins
    WAITING_FOR_PLAYERS --> GAME_START: Second player joins
    WAITING_FOR_PLAYERS --> WAITING_FOR_PLAYERS: Invalid message / ERROR

    GAME_START --> PLAYER_TURN: Set up players and health

    PLAYER_TURN --> EVALUATE_MOVE: Active player sends MOVE
    PLAYER_TURN --> PLAYER_TURN: Wrong turn or bad message / ERROR
    PLAYER_TURN --> GAME_OVER: Player disconnects

    EVALUATE_MOVE --> PLAYER_TURN: Valid attack and health is above 0
    EVALUATE_MOVE --> PLAYER_TURN: Invalid move / ERROR
    EVALUATE_MOVE --> GAME_OVER: Health reaches 0
    EVALUATE_MOVE --> GAME_OVER: Player disconnects

    GAME_OVER --> CLEANUP: Send GAME_OVER
    CLEANUP --> WAITING_FOR_PLAYERS: Reset game

What Each State Does

INIT

The server starts up, creates the TCP socket, and begins listening for players.

WAITING_FOR_PLAYERS

The server waits until two players connect.

The first player joins and gets a LOBBY_WAIT message.

When the second player joins, the server goes to GAME_START.

If a bad message is sent, the server sends an ERROR and stays in this state.

GAME_START

The server sets up Player 1 and Player 2. Both players start with 100 health.

Player 1 goes first.

PLAYER_TURN

The server waits for the current player to send a MOVE.

If the wrong player tries to move, the server sends an ERROR and keeps the same turn.

If somebody disconnects, the game ends and the other player wins by forfeit.

EVALUATE_MOVE

The server checks the move and then creates a random damage amount.

The damage is taken away from the other player's health.

If the other player still has health left, the server sends a STATE_UPDATE and switches turns.

If their health reaches 0, the server goes to GAME_OVER.

If the move was invalid, the server sends an ERROR and keeps the same player turn.

GAME_OVER

The server sends a GAME_OVER message with the winner and the reason the game ended.

CLEANUP

The server clears the old game information and gets ready for another game.

After that, it goes back to WAITING_FOR_PLAYERS.
