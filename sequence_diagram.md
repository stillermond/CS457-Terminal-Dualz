Sequence Diagram

This diagram shows how the two players will communicate with the server during a game of Terminal Dualz.

It starts with both players connecting, then shows how attacks are handled and how the server updates both players.

I also included what happens if someone makes an invalid move, disconnects, or wins the game.

```mermaid
sequenceDiagram
    autonumber
    actor P1 as Player 1
    participant S as Game Server
    actor P2 as Player 2
    actor P3 as Extra Player

    P1->>S: CONNECT
    S-->>P1: LOBBY_WAIT

    P2->>S: CONNECT
    Note over S: Create a thread for each player

    S-->>P1: GAME_START
    S-->>P2: GAME_START
    Note over S: Both players start with 100 health

    opt Another player tries joining
        P3->>S: CONNECT
        S-->>P3: ERROR (GAME_FULL)
        Note over S,P3: Close extra connection
    end

    loop While the game is running

        alt Player 1 sends an attack
            P1->>S: MOVE (ATTACK)

            Note over S: Use game lock and check the move

            alt Invalid move or wrong turn
                S-->>P1: ERROR (OUT_OF_TURN or INVALID_ACTION)
            else Valid move
                Note over S: Generate random damage
                Note over S: Update health, turn, and score if needed
                S-->>P1: STATE_UPDATE (health, damage, turn, scores)
                S-->>P2: STATE_UPDATE (health, damage, turn, scores)
            end

        else Player 2 sends an attack
            P2->>S: MOVE (ATTACK)

            Note over S: Use game lock and check the move

            alt Invalid move or wrong turn
                S-->>P2: ERROR (OUT_OF_TURN or INVALID_ACTION)
            else Valid move
                Note over S: Generate random damage
                Note over S: Update health, turn, and score if needed
                S-->>P1: STATE_UPDATE (health, damage, turn, scores)
                S-->>P2: STATE_UPDATE (health, damage, turn, scores)
            end
        end
    end

    alt A player reaches 0 health
        Note over S: Final score was included in STATE_UPDATE
        S-->>P1: GAME_OVER (winner, HEALTH_ZERO)
        S-->>P2: GAME_OVER (winner, HEALTH_ZERO)

    else Player 1 disconnects
        P1->>S: DISCONNECT
        Note over S: Player 2 wins by forfeit
        Note over S: Update Player 2 score
        S-->>P2: STATE_UPDATE (final scores)
        S-->>P2: GAME_OVER (Player 2, OPPONENT_DISCONNECTED)

    else Player 2 disconnects
        P2->>S: DISCONNECT
        Note over S: Player 1 wins by forfeit
        Note over S: Update Player 1 score
        S-->>P1: STATE_UPDATE (final scores)
        S-->>P1: GAME_OVER (Player 1, OPPONENT_DISCONNECTED)
    end

    Note over S: Close connections and clean up game
```

How the Messages Work

The first player connects and gets LOBBY_WAIT since the server is still waiting for someone else.

When Player 2 connects, the server sends GAME_START to both players. Player 1 will go first.

After that, players can send MOVE whenever it's their turn. The server checks each move before doing anything.

If the move is valid, the server generates random damage and subtracts it from the opponent's health.

If someone tries attacking when it isn't their turn, the server sends ERROR and ignores the attack.

Keeping the Game Updated

The server will use a lock when checking moves and changing the game information. This is to prevent both player threads from changing something at the same time.

After an attack, the server sends STATE_UPDATE to both players.

The updates will include the new health values, damage, whose turn is next, and player scores.

Both players should receive the same information. The server will send the messages one after another while holding the lock, so another move can't change the game between the updates.

Scores and Ending the Game

The server will store the scores in a dictionary, like I explained in concurrency_design.md.

When someone wins, their score increases by one. The updated scores will be included in the last STATE_UPDATE before GAME_OVER.

GAME_OVER tells the players who won and why the game ended.

If someone disconnects during a game, the other player wins by forfeit. The server updates their score and sends them the final results.

The diagram shows players sending DISCONNECT normally, but the server will also handle unexpected disconnects if a client crashes or loses its connection.

After the game finishes, the server will close the old connections and reset the game so two new players can join.

Summary

This diagram shows how I'm planning to handle messages between the two players and the server.

The server will check moves, calculate damage, update scores, and send the results to both players.

I'm using the same message types from Sprint 1, with scores added to STATE_UPDATE. The main difference now is that both players will have separate threads, and the server will use a lock to avoid problems when they are both sending messages.
