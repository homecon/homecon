
import sys
import logging
import time

from threading import Thread

from homecon.tests.common import TestCase
from homecon.homecon import HomeCon
from homecon.core.state import State


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)7.7s  %(processName)-12.12s  %(name)-28.28s %(message)s',
                    stream=sys.stdout)
logging.getLogger('homecon.core.database').setLevel(logging.INFO)


class TestHomeCon(TestCase):

    def test_running_homecon(self):
        hc = HomeCon()
        homecon_thread = Thread(target=hc.start)
        homecon_thread.start()
        time.sleep(1)

        s = State.add('mystate', value=5)
        s.value = 10
        time.sleep(2)
        hc.stop()
        homecon_thread.join()
        self.assertEqual(s.value, 10)

    def test_restarting_homecon(self):
        hc = HomeCon()
        homecon_thread = Thread(target=hc.start)
        homecon_thread.start()
        time.sleep(1)

        s = State.add('mystate', value=5)
        s.value = 10
        time.sleep(1)

        hc.stop()
        homecon_thread.join()

        hc = HomeCon()
        homecon_thread = Thread(target=hc.start)
        homecon_thread.start()
        time.sleep(1)
        hc.stop()
        homecon_thread.join()
        s = State.get('mystate')
        self.assertEqual(s.value, 10)
