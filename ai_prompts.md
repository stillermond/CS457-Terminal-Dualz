AI Prompting

I can use AI to help write parts of the code, but I do not want it changing the protocol or making up its own message types.

The AI should follow protocol_blueprint.md and fsm_specification.md.

Main Prompt:

Help me write the TCP client and server for this game.

Follow protocol_blueprint.md exactly for the message names, JSON fields, and newline framing.

Do not add new message types or rename fields.

The server should control health, damage, turns, and the game state.

If a message is invalid, send ERROR instead of crashing the server.

Parser Prompt:

Write Python functions to send and receive the JSON messages from protocol_blueprint.md.

Each message should end with a newline.

The receive code should keep data in a buffer until it finds a newline.

Do not assume one recv() call always gives one full message.

If the JSON is bad or the message type is not allowed, return an ERROR message.

Game Logic Prompt:

Write the server game logic using the states from fsm_specification.md.

Use INIT, WAITING_FOR_PLAYERS, GAME_START, PLAYER_TURN, EVALUATE_MOVE, GAME_OVER, and CLEANUP.

Only the current player can attack.

If a player moves out of turn, send ERROR and keep the same turn.

If a player's health reaches 0, end the game.

If a player disconnects, the other player wins by forfeit.

Do not make up extra states or message types.
