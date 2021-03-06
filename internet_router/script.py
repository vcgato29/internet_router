#!python3

import sys
import os
import socket
import json

import logging
logging.basicConfig(level=logging.INFO)


def dhclient4():
    state_dir = sys.argv[1]
    logging.info('dhclient4_script invoked, state_dir: %s' % state_dir)

    environment_bytes = json.dumps(dict(os.environ.items())).encode('utf-8')

    logging.info('dhclient4_script creating command socket')
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        # Connect to server and send data
        sock.connect(os.path.join(state_dir, 'dhclient4_comm'))
        logging.info('dhclient4_script sending key + cmd ...')
        sock.sendall(environment_bytes)
        logging.info('dhclient4_script done')
    finally:
        logging.info('dhclient4_script closing command socket')
        sock.close()


def dhclient6():
    state_dir = sys.argv[1]
    logging.info('dhclient6_script invoked, state_dir: %s' % state_dir)

    environment_bytes = json.dumps(dict(os.environ.items())).encode('utf-8')

    logging.info('dhclient6_script creating command socket')
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        # Connect to server and send data
        sock.connect(os.path.join(state_dir, 'dhclient6_comm'))
        logging.info('dhclient6_script sending key + cmd ...')
        sock.sendall(environment_bytes)
        logging.info('dhclient6_script done')
    finally:
        logging.info('dhclient6_script closing command socket')
        sock.close()
