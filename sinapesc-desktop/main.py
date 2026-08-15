"""
Sinapesc Desktop — Controle de REAP
===================================

Ponto de entrada do programa para notebook/computador.
Execute:  python main.py
Gere .exe: build_exe.bat  (Windows)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Garante imports locais ao rodar fora de um pacote instalado
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    from ui import SinapescApp

    app = SinapescApp()
    app.mainloop()


if __name__ == "__main__":
    main()
