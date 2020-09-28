import config
import peers
import readline
import router
import sys
import threading

# Console management interface

# Functions starting with "cmd_" will be exposed to the console. test-command
# will call cmd_test_command.


# Terminates the application
def cmd_exit(arg):
    sys.exit(0)


def cmd_peer_list(arg):
    print("Peer list")

    for i, peer in enumerate(peers.peers):
        print(
            f"{i} - {peer.alias} {peer.last_received or 0} {peer.sent} {peer.received}"
        )


def cmd_peer_add(arg):
    name, ip, port = arg.split(" ")
    peers.peers.append(peers.Peer(name, (ip, int(port))))


def cmd_config_set(arg):
    k, v = arg.split(" ", 1)
    config.set(k, v)


def cmd_config_get(arg):
    print(config.get(arg))


def cmd_read(arg):
    # Read a file and execute each line as a command
    with open(arg) as f:
        for line in f:
            line = line.strip()
            run_command(line)


def cmd_start(arg):
    threading.Thread(target=router.listener, daemon=True).start()
    threading.Thread(target=router.tracer_task, daemon=True).start()


def cmd_send_msg(arg):
    node, msg = arg.split(" ", 1)
    router.send_data(node, msg)

def cmd_traceroute(arg):
    router.send_tracert(arg)


def run_command(line):
    # Ignore empty lines
    if not line.strip():
        return

    cmd = line.split(" ", 1)
    args = ""
    if len(cmd) > 1:
        args = cmd[1]
    cmd = cmd[0].replace("-", "_")
    cmd = globals().get(f"cmd_{cmd}")
    if cmd:
        cmd(args)
    else:
        print(f"Unknown command")


def management():
    print("Network Management Console")
    print()

    readline.parse_and_bind("")
    while True:
        try:
            line = input("> ").strip()
            run_command(line)
        except Exception as e:
            print(e)
