#!/usr/bin/python
# coding: utf8

import click
import os
from subprocess import call

@click.command()
@click.option('--simulate', is_flag=True, default=True, help='Simulate the Oven')  # TODO no default
@click.option('--serial', help='Serial Port')
@click.option('--port', default=8080, help='Webserver Port')
def run(simulate, serial, port):
    click.echo('Starting reflowc')
    if simulate:
        click.echo("SIMULATION")

    cmdline = ['bokeh', 'serve', "app.py", "--port", str(port), "--show"]
    call(cmdline, cwd=os.path.abspath(os.path.dirname(__file__)))

if __name__ == '__main__':
    run()
