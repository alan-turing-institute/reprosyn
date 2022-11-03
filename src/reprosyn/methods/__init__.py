# Convenience so that using can call `from reprosyn.methods import [command]`

import warnings

warnings.filterwarnings(action="ignore", category=UserWarning)

# METHODS
# ---------------------
from reprosyn.methods.ipf.ipf import IPF
from reprosyn.methods.mbi.mst import MST
from reprosyn.methods.mbi.privbayes import PRIVBAYES
from reprosyn.methods.gans.gans import CTGAN, PATEGAN
from reprosyn.methods.data_synthesiser.wrapper import (
    DS_INDHIST,
    DS_BAYNET,
    DS_PRIVBAYES,
)
from reprosyn.methods.synthpop.synthpop import SYNTHPOP


# CLI COMMANDS
from reprosyn.methods.ipf.cli import cmd_ipf

from reprosyn.methods.mbi.cli import cmd_mst, cmd_pb

from reprosyn.methods.gans.cli import cmd_pategan, cmd_ctgan
from reprosyn.methods.data_synthesiser.cli import (
    cmd_baynet,
    cmd_ds_privbayes,
    cmd_indhist,
)
from reprosyn.methods.synthpop.cli import cmd_spop

COMMANDS = (
    cmd_ipf,
    cmd_mst,
    cmd_pb,
    cmd_ctgan,
    cmd_pategan,
    cmd_baynet,
    cmd_ds_privbayes,
    cmd_indhist,
    cmd_spop,
)
