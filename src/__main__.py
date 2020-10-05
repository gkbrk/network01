#!/usr/bin/env python3
import sys
import management

# Entry point for the network
# Starts the management console


def main():
    if len(sys.argv) > 1:
        for cmd in sys.argv[1:]:
            management.run_command(cmd)
    management.management()
    return 0


if __name__ == "__main__":
    sys.exit(main())
