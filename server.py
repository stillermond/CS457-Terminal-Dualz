import argparse
import json
import queue
import random
import socket
import threading

START_HEALTH = 100


def valid_port(value):
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Port must be a number.")

    if port < 1024 or port > 65535:
        raise argparse.ArgumentTypeError("Port must be 1024-65535.")

    return port


def send_message(connection, message):
    data = json.dumps(message) + "\n"
    connection.sendall(data.encode("utf-8"))


def read_messages(connection, player_number, messages):
    # Read me
    try:
        with connection.makefile("r") as stream:
            for line in stream:
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    message = {"msg_type": "INVALID"}

                messages.put((player_number, message))
    except OSError:
        pass

    messages.put((player_number, None))


def run_game(players):
    messages = queue.Queue()
    health = [START_HEALTH, START_HEALTH]

    state = "LOBBY"
    turn = 0
    round_number = 1

    # Start a thread for each player.
    for number in range(2):
        thread = threading.Thread(
            target=read_messages,
            args=(players[number], number, messages),
            daemon=True
        )
        thread.start()

    connected = set()

    # Waits for both players to join
    while len(connected) < 2:
        number, message = messages.get()

        if message is None:
            print("Player disconnected.")
            return

        if message.get("msg_type") == "CONNECT":
            connected.add(number)
        else:
            send_message(players[number], {
                "msg_type": "ERROR",
                "message": "Expected CONNECT."
            })

    state = "START"
    print("Both players connected. Starting game.")

    for number in range(2):
        send_message(players[number], {
            "msg_type": "GAME_START",
            "player_id": f"Player{number + 1}",
            "health": health,
            "your_turn": number == turn
        })

    state = "TURN_A"

    # Main game loop
    while state != "GAME_OVER":
        number, message = messages.get()

        if message is None:
            print(f"Player {number + 1} disconnected.")

            other = 1 - number

            try:
                send_message(players[other], {
                    "msg_type": "GAME_OVER",
                    "message": "Other player disconnected.",
                    "health": health
                })
            except OSError:
                pass

            break

        if message.get("msg_type") != "MOVE":
            send_message(players[number], {
                "msg_type": "ERROR",
                "message": "Expected MOVE."
            })
            continue

        if number != turn:
            send_message(players[number], {
                "msg_type": "ERROR",
                "message": "Not your turn."
            })
            continue

        if message.get("action") != "ATTACK":
            send_message(players[number], {
                "msg_type": "ERROR",
                "message": "Invalid action."
            })
            continue

        state = "RESOLVE"

        # random attack damage
        damage = random.randint(10, 20)
        other = 1 - turn

        health[other] -= damage

        if health[other] < 0:
            health[other] = 0

        print(f"Turn {round_number}: Player {number + 1} "
              f"dealt {damage} damage.")

        # Check if someone won
        if health[other] == 0:
            state = "GAME_OVER"

            for player in players:
                send_message(player, {
                    "msg_type": "GAME_OVER",
                    "message": f"Player {number + 1} wins!",
                    "health": health
                })

            break

        turn = other
        round_number += 1

        if turn == 0:
            state = "TURN_A"
        else:
            state = "TURN_B"

        # Send the results to both players
        for player_number in range(2):
            send_message(players[player_number], {
                "msg_type": "ROUND_RESULT",
                "attacker": f"Player{number + 1}",
                "damage": damage,
                "health": health,
                "your_turn": player_number == turn,
                "turn_number": round_number
            })


def main():
    parser = argparse.ArgumentParser(
        description="Terminal Dualz Server"
    )

    parser.add_argument(
        "-p",
        type=valid_port,
        required=True,
        help="Port number (1024-65535)"
    )

    args = parser.parse_args()
    players = []

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind(("0.0.0.0", args.p))
        server.listen(2)

        print(f"Server listening on port {args.p}")

        # Accept two players
        for number in range(2):
            connection, address = server.accept()
            players.append(connection)

            print(f"Player {number + 1} connected.")

            if number == 0:
                send_message(connection, {
                    "msg_type": "LOBBY_WAIT",
                    "message": "Waiting for Player 2..."
                })

        run_game(players)

    except OSError as error:
        print(f"Server error: {error}")

    except KeyboardInterrupt:
        print("Server stopped.")

    finally:
        for player in players:
            player.close()

        if "server" in locals():
            server.close()


if __name__ == "__main__":
    main()
