"""
This file contains the manual testing parts for developing the GUI
"""

from gui.gui_builder import build_interface_standalone
from util.agent_base import BaseTrainingAgent

if __name__ == '__main__':
    root = build_interface_standalone(BaseTrainingAgent())
    root.title('Development')
    root.mainloop()
