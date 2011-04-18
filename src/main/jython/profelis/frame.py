"""
Copyright 2010 Jarl Haggerty

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
       
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from profelis import panel
from javax.swing import JFrame
from javax.swing import JMenuBar
from javax.swing import JMenu
from javax.swing import AbstractAction
from javax.swing import JTabbedPane
from javax.swing import JFileChooser
from java.awt.event import WindowAdapter
from java.io import File

class OpenAction(AbstractAction):
    def __init__(self, frame):
        AbstractAction.__init__(self, "Open")
        self.frame = frame
                
    def actionPerformed(self, event):
        fileChooser = JFileChooser()
        if fileChooser.showOpenDialog(None) == JFileChooser.APPROVE_OPTION:
            self.frame.contentPane.addTab(fileChooser.selectedFile.name, panel.ProfelisPanel(fileChooser.selectedFile.absolutePath))

class CloseAction(AbstractAction):
    def __init__(self, frame):
        AbstractAction.__init__(self, "Close")
        self.frame = frame
                
    def actionPerformed(self, event):
        self.frame.contentPane.remove(self.frame.contentPane.selectedIndex)

class QuitAction(AbstractAction):
    def __init__(self, frame):
        AbstractAction.__init__(self, "Quit")
        self.frame = frame
                
    def actionPerformed(self, event):
        self.frame.dispose()

class ProfelisWindowAdapter(WindowAdapter):
    def __init__(self, frame):
        self.frame = frame

    def windowClosed(self, event):
        for index in range(self.frame.contentPane.tabCount):
            self.frame.contentPane.getComponentAt(index).markButtonLabelerTimer.stop()
        self.frame.running = False

    def windowClosing(self, event):
        self.frame.dispose()
    
class ProfelisFrame(JFrame):
    def __init__(self):
        self.running = True
        menuBar = JMenuBar()
        
        menu = JMenu("File")
        menu.add(OpenAction(self))
        menu.add(CloseAction(self))
        menu.addSeparator()
        menu.add(QuitAction(self))
        self.addWindowListener(ProfelisWindowAdapter(self))
        menuBar.add(menu)

        self.setJMenuBar(menuBar)

        self.contentPane = JTabbedPane()

        self.contentPane.addTab("Phi-4-1.art", panel.ProfelisPanel("/Users/mbsulli/neofelis/genomes/Phi-4-1.art"))
