#!python3

import sys
import pyroute2
import pyroute2.ipdb
import signal
from .dispatcher import Dispatcher
from threading import Event

import logging
logging.basicConfig(level=logging.ERROR)


def service():
    logging.info('Running as a service')

    wan_interface = sys.argv[1]
    lan_interface = sys.argv[2]
    state_dir = sys.argv[3]

    logging.info('Adding current interfaces')
    dispatcher = Dispatcher(wan_interface, lan_interface, state_dir)
    with pyroute2.IPRoute() as netlink_route:
        for iface in netlink_route.get_links():
            if iface.get_attr('IFLA_OPERSTATE') == 'UP':
                dispatcher.add_interface(iface['index'], iface.get_attr('IFLA_IFNAME'))

    def ipdb_callback(ipdb, msg, action):
        logging.debug('NETLINK event: %s, %s' % (repr(msg), action))

        if action == 'RTM_NEWLINK':
            ifindex = msg['index']
            try:
                interface = ipdb.interfaces[ifindex]
            except KeyError:
                logging.warning('NETLINK warning. Interface does not exist, skipping')
                return
            ifname = interface['ifname']
            if msg.get_attr('IFLA_OPERSTATE') == 'UP':
                dispatcher.add_interface(ifindex, ifname)
            else:
                dispatcher.remove_interface(ifindex, ifname)
            return

        if action == 'RTM_DELLINK':
            ifindex = msg['index']
            try:
                interface = ipdb.interfaces[ifindex]
            except KeyError:
                logging.warning('NETLINK warning. Interface does not exist, skipping')
                return
            ifname = interface['ifname']
            dispatcher.remove_interface(ifindex, ifname)
            return

    global_ipdb = pyroute2.IPDB()
    ipdb_cb = global_ipdb.register_callback(ipdb_callback)

    termination_event = Event()

    def signal_handler(signum, frame):
        logging.warning('Received signal %s. Exiting' % signum)
        termination_event.set()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    while True:
        try:
            if termination_event.wait(60):
                logging.info('Event triggered. Shutting down ...')
                break
            logging.error('Status: my WAN ip4 addresses: %s' % dispatcher.my_wan_ip4_addresses)
            logging.error('Status: my WAN ip6 addresses: %s' % dispatcher.my_wan_ip6_addresses)
            logging.error('Status: my ip6 prefixes: %s' % dispatcher.my_lan_prefixes)
            logging.error('Status: my ip6 rdnss: %s' % dispatcher.my_rdnss)
        except (InterruptedError, KeyboardInterrupt):
            logging.info('Interrupt received. Shutting down ...')
            break

    global_ipdb.unregister_callback(ipdb_cb)
    global_ipdb.release()
    dispatcher.shutdown()


if __name__ == '__main__':
    exit(service())
