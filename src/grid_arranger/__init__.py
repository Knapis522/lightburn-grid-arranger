"""Grid Arranger for LightBurn.

Neoficiální nástroj; není produktem LightBurn Software.
Vrstvy (spec. kap. 11, 25): ``domain`` → ``core`` → adaptér ``.lbrn2`` → UI.
Závislosti směřují pouze dovnitř.
"""

from .version import __version__

__all__ = ["__version__"]
