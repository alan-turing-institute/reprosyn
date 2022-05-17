import click

from reprosyn.methods.mbi.cli import mstcommand


@click.group(help="A cli tool synthesising the 1% census")
def main():
    pass


main.add_command(mstcommand)

if __name__ == "__main__":
    main()
