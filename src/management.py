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
    threading.Thread(target=router.audio_task, daemon=True).start()

def cmd_debug_update(arg):
    router.send_update(arg)

def cmd_send_msg(arg):
    node, msg = arg.split(" ", 1)
    router.send_data(node, msg)

def cmd_traceroute(arg):
    router.send_tracert(arg)

def cmd_known_nodes(arg):
    tracers = [tracer[1] for tracer in router.tracerList.l]
    tracers = list(set(tracers))
    tracers.sort()

    for tracer in tracers:
        print(tracer)

def cmd_update(arg):
    import selfUpdate
    selfUpdate.update()

def cmd_audio(arg):
    import os
    if arg == "off":
        if router.dsp:
            os.close(router.dsp)
        router.dsp = None
        router.audioTarget = None
    else:
        router.dsp = os.open("/dev/dsp", os.O_RDWR)
        router.audioTarget = arg

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
    import buildtime

    print("Network Management Console")
    print(f"Built on {buildtime.date}")
    print()

    readline.parse_and_bind("")
    while True:
        try:
            line = input("> ").strip()
            run_command(line)
        except Exception as e:
            print(e)
