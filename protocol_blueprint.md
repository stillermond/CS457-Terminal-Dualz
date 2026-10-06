Application Protocol Blueprint

Transport and Framing

For the game I am using TCP and JSON messages. Each message will end with a newline (\n) so the receiver knows where one message ends and the next one starts.

TCP is a stream, so one recv() might get half of a message, one message, or even multiple messages. Because of that, the receiver will keep the data in a buffer until it finds a newline.

Example:

{"msg_type":"CONNECT","player_id":"Player1"}\n{"msg_type":"MOVE","player_id":"Player1","action":"ATTACK"}\n

Message Types

CONNECT

Direction: Client -> Server

Used when a player wants to join the game.

{
  "msg_type": "CONNECT",
  "player_id": "Player1"
}

Fields:

msg_type: string

player_id: string

LOBBY_WAIT

Direction: Server -> Client

Used to tell the first player that the server is still waiting for Player 2.

{
  "msg_type": "LOBBY_WAIT",
  "message": "Waiting for Player 2."
}

GAME_START

Direction: Server -> Clients

Used when both players are connected and the game is ready to start.

{
  "msg_type": "GAME_START",
  "player_1": "Player1",
  "player_2": "Player2",
  "health": 100,
  "active_player": "Player1"
}

Fields:

player_1: string

player_2: string

health: integer

active_player: string

MOVE

Direction: Client -> Server

Used when the current player attacks.

{
  "msg_type": "MOVE",
  "player_id": "Player1",
  "action": "ATTACK"
}

The server will check if it is actually that player's turn before accepting it.

STATE_UPDATE

Direction: Server -> Clients

Used after a valid attack so both players know the new health and whose turn is next.

{
  "msg_type": "STATE_UPDATE",
  "player_1_health": 100,
  "player_2_health": 82,
  "damage": 18,
  "active_player": "Player2"
}

ERROR

Direction: Server -> Client

Used when something is wrong, like a player trying to move out of turn.

{
  "msg_type": "ERROR",
  "error_code": "OUT_OF_TURN",
  "message": "It is not your turn."
}

Some possible errors are:

OUT_OF_TURN

INVALID_ACTION

MALFORMED_MESSAGE

GAME_FULL

DISCONNECT

Direction: Client -> Server

Used when a player quits normally.

{
  "msg_type": "DISCONNECT",
  "player_id": "Player1"
}

If this happens during a game, the other player wins by forfeit.

GAME_OVER

Direction: Server -> Clients

Used when the game ends.

{
  "msg_type": "GAME_OVER",
  "winner": "Player1",
  "reason": "HEALTH_ZERO"
}

The reason could be HEALTH_ZERO or OPPONENT_DISCONNECTED.

Connection Ending

If a player quits normally, they should send DISCONNECT before closing the socket.

If the connection closes normally, recv() can return no data:

data = sock.recv(1024)
if not data:
    handle_disconnect()

The server should also handle errors like:

ConnectionResetError
BrokenPipeError
ConnectionAbortedError
TimeoutError

If a player disconnects in the middle of the game, the other player wins and the server cleans up the game.

Main Rules:

Messages use JSON.
Every message ends with \n.
The server controls health, damage, and turns.
Only the current player can attack.
Invalid moves send back an ERROR.
Invalid moves do not switch the turn.
Leaving during a game counts as a forfeit.
