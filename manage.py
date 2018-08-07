import sys
import click

import wx

from server.window import GameWindow
from server.socket import MessageServerFactory, reactor as server_reactor

from client.socket import BrainMessageReceiver, reactor as client_reactor
from client.brains import RandomBrain, ScoreBrainAlpha, ScoreBrainBeta


@click.group()
def cli():
    pass

@cli.command()
@click.option('--tick', default=1000, help='Game operation tick')
@click.option('--host', default='127.0.0.1', help='connetion host')
@click.option('--port', default='5001', help='connetion port')
def runserver(tick, host, port):
    # Open reversi GUI Windown
    app = wx.App(False)
    window = GameWindow()
    window.Show()
    # run socket server
    server_reactor.registerWxApp(app)
    url = 'ws://{}:{}'.format(host, port)
    factory = MessageServerFactory(url, window)
    server_reactor.listenTCP(int(port), factory)
    server_reactor.run()

@cli.command()
@click.option('--host', default='127.0.0.1', help='connetion host')
@click.option('--port', default='5001', help='connetion port')
def join_random(host, port):
    brain = RandomBrain()
    client_reactor.connectTCP(host, port, BrainMessageReceiver(brain))
    client_reactor.run()

@cli.command()
@click.option('--host', default='127.0.0.1', help='connetion host')
@click.option('--port', default='5001', help='connetion port')
def join(host, port):
    brain = ScoreBrainBeta()
    client_reactor.connectTCP(host, port, BrainMessageReceiver(brain))
    client_reactor.run()

if __name__ == '__main__':
    cli()
