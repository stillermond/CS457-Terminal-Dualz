Server Concurrency

For Terminal Dualz, I decided to use multithreading with Python's threading module. The game only needs two players, so I think this will be easier than using something like select or selectors.

The server will have a main thread that waits for players to connect. When someone connects, the server will create another thread for that player. This way, both players can send messages without having to wait for the other player.

The main server can also keep accepting connections while the game is running.

Player Connections

When the server starts, it will create a TCP socket and use listen() to wait for connections.

The first player connects and sends CONNECT. The server adds them to the player list and sends LOBBY_WAIT since another player is still needed.

When the second player joins, the server sends GAME_START to both players and the game begins.

Each player will have their own thread that uses recv() to listen for messages. I'll be using the same JSON format from Sprint 1, where each message ends with a newline.

Since the game only supports two players, if someone else tries joining while a game is running, the server will send ERROR and close their connection.

The player threads will keep running until the game ends or someone disconnects. Once they're finished, the server will close their sockets and remove them from the player list.

Thread Safety

Since both players have their own threads, I need to make sure they don't try changing the game information at the same time.

For example, both players might try attacking at once. If the server processes both attacks without checking, it could mess up the health values or whose turn it is.

To prevent this, I'll use threading.Lock.

The lock will protect things like player health, scores, the current turn, connected players, and the game state.

Whenever a thread needs to update any of this information, it will first acquire the lock. The other thread will have to wait until the lock is released.

I'll use with game_lock: for this since Python will release the lock automatically once that part of the code finishes.

I won't keep the lock while a thread is just waiting for a player to send something. It'll mainly be used when checking or changing game information.

Handling Player Moves

I already explained most of the game rules in fsm_specification.md, so this part is mostly about how the server will handle moves coming from different threads.

When someone sends MOVE, the server will use the game lock before checking anything.

It will check if the game is running, if the message is valid, and if it's that player's turn.

If the move is allowed, the server will calculate the damage and subtract it from the other player's health.

I decided to use random damage for attacks. I'll probably use Python's random module for this, although I haven't decided on the exact damage range yet.

After an attack, the server checks if the other player still has health left. If they do, the turn switches. Otherwise, the game ends and the winner gets a point.

If someone attacks when it isn't their turn, the server will just send ERROR and ignore the move.

The lock should prevent another thread from changing the game information while an attack is being processed.

Updating Both Players

The server will keep track of the game information so both players are using the same values.

After an attack, both players need to know what happened. I'll use the STATE_UPDATE message from Sprint 1 for this.

The message will include the updated health, damage dealt, and whose turn it is.

The server will send the update to both players using sendall(). I'll keep the game lock while sending these updates so another move doesn't change the information between messages.

The updates won't arrive at exactly the same time, but both players will get the same results.

I'll also use timeouts so the server doesn't get stuck forever if one of the clients stops responding.

Scores

For the scores, I'm planning to use a simple Python dictionary on the server.

Both players will start with zero points. When someone wins a round, their score goes up by one.

The server will use the same lock when changing scores so the threads don't interfere with each other.

After a round ends, both players will receive the updated scores. I'll add the scores to STATE_UPDATE so I don't need another message type just for that.

When the game ends, the server sends GAME_OVER with the winner and final scores.

For now, scores will just stay in memory. They won't be saved anywhere after the game session ends.

Disconnects

I covered disconnects in Sprint 1, but I also need to handle them with the player threads.

If someone leaves, they can send DISCONNECT. The server can also tell when a connection closes because recv() returns empty data. If the connection drops unexpectedly, there might be a socket error instead.

When this happens, the server will use the lock before updating the player list and game state.

If one player disconnects during a game, the other player wins by forfeit. The server will update the score and send GAME_OVER to the remaining player.

After that, the sockets will be closed and the player threads will finish.

The server should then be able to go back to waiting for two new players without needing to restart everything.

Summary

I'm going with multithreading for Terminal Dualz since it's a small two-player game and seems fairly straightforward.

Each player will have their own thread, and the server will use a lock when updating game information. This should help prevent problems when both players are sending messages.

The server will handle turns, random damage, health, and scores while keeping both players updated.

Most of the actual game rules were already planned in Sprint 1. This sprint is more about making sure the server can handle both players at once.
