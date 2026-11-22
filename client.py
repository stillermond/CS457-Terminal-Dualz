import argparse
import json
import socket
import sys


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


def show_health(health):
    print()
    print(f"Player 1 Health: {health[0]}")
    print(f"Player 2 Health: {health[1]}")
    print()


def play(connection):
    # Read messages from the server
    with connection.makefile("r") as stream:
        for line in stream:
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                print("Invalid message received.")
                continue

            msg_type = message.get("msg_type")

            if msg_type == "LOBBY_WAIT":
                print(message["message"])

            elif msg_type == "GAME_START":
                print()
                print("=== TERMINAL DUALZ ===")
                print(f"You are {message['player_id']}")
                print("Game started!")

                show_health(message["health"])

            elif msg_type == "ROUND_RESULT":
                print()
                print(f"{message['attacker']} attacked!")
                print(f"Damage: {message['damage']}")

                show_health(message["health"])

            elif msg_type == "GAME_OVER":
                print()
                print("=== GAME OVER ===")
                print(message["message"])

                show_health(message["health"])
                return

            elif msg_type == "ERROR":
                print("Error:", message["message"])
                continue

            else:
                print("Unknown message.")
                continue

            # Ask player to attack when it is their turn
            if msg_type in ("GAME_START", "ROUND_RESULT"):
                if message["your_turn"]:
                    print("Your Turn!")

                    while True:
                        choice = input("Press Enter to attack: ")

                        if choice == "":
                            break

                        print("Just press Enter.")

                    send_message(connection, {
                        "msg_type": "MOVE",
                        "action": "ATTACK"
                    })

                else:
                    print("Waiting for other player...")

    print("Disconnected from server.")


def main():
    parser = argparse.ArgumentParser(
        description="Terminal Dualz Client"
    )

    parser.add_argument(
        "-i",
        required=True,
        help="Server hostname or IP"
    )

    parser.add_argument(
        "-p",
        type=valid_port,
        required=True,
        help="Port number (1024-65535)"
    )

    args = parser.parse_args()

    try:
        server_ip = socket.gethostbyname(args.i)

    except socket.gaierror:
        print(f"[ERROR] Unable to resolve DNS hostname '{args.i}'.")
        print("Check your Cisco router DNS configuration "
              "(ip dns server / ip host) or hostname spelling.")
        sys.exit(1)

    # Connect to the server
    try:
        connection = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        connection.connect((server_ip, args.p))

        print(f"Connected to {args.i} on port {args.p}")

        send_message(connection, {
            "msg_type": "CONNECT",
            "player_id": "Player"
        })

        play(connection)

    except OSError as error:
        print(f"Connection error: {error}")
        sys.exit(1)

    except (KeyboardInterrupt, EOFError):
        print("Client stopped.")
        sys.exit(1)

    finally:
        if "connection" in locals():
            connection.close()


if __name__ == "__main__":
    main()
