import click

from reprosyn.methods.mbi.cli import mst


@click.group(help="A cli tool synthesising the 1% census")
def main():
    pass


main.add_command(mst)

if __name__ == "__main__":
    main()
