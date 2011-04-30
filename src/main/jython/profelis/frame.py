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
from javax.swing import JPanel
from javax.swing import JTextField
from javax.swing import JLabel
from javax.swing import JButton
from java.awt.event import WindowAdapter
from java.io import File
from java.awt import GridBagLayout
from java.awt import GridBagConstraints

class BlastAction(AbstractAction):
      """
      Action for selecting the location of Blast+.  Brings up a file selection dialog and fills the text field for blast with the selection.
      """
      def __init__(self, frame):
        self.frame = frame
        AbstractAction.__init__(self, "...")

      def actionPerformed(self, event):
        fileChooser = JFileChooser()
        fileChooser.fileSelectionMode = JFileChooser.DIRECTORIES_ONLY
        if fileChooser.showOpenDialog(None) == JFileChooser.APPROVE_OPTION:
          self.frame.blastLocation.text = fileChooser.selectedFile.absolutePath

class DatabaseAction(AbstractAction):
      """
      Action for selecting the location of Blast Databases.  Brings up a file selection dialog and fills the text field for blast with the selection.
      """
      def __init__(self, frame):
        self.frame = frame
        AbstractAction.__init__(self, "...")

      def actionPerformed(self, event):
        fileChooser = JFileChooser()
        fileChooser.fileSelectionMode = JFileChooser.DIRECTORIES_ONLY
        if fileChooser.showOpenDialog(None) == JFileChooser.APPROVE_OPTION:
          self.frame.databaseLocation.text = fileChooser.selectedFile.absolutePath

class OpenAction(AbstractAction):
    def __init__(self, frame):
        AbstractAction.__init__(self, "Open")
        self.frame = frame
                
    def actionPerformed(self, event):
        fileChooser = JFileChooser()
        if fileChooser.showOpenDialog(None) == JFileChooser.APPROVE_OPTION:
            self.frame.projects.addTab(fileChooser.selectedFile.name[:fileChooser.selectedFile.name.rfind(".")], panel.ProfelisPanel(self.frame, fileChooser.selectedFile.absolutePath[:fileChooser.selectedFile.absolutePath.rfind(".")]))

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
        for index in range(self.frame.projects.tabCount):
            self.frame.projects.getComponentAt(index).markButtonLabelerTimer.stop()
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

        self.contentPane = JPanel()
        self.contentPane.layout = GridBagLayout()
        constraints = GridBagConstraints()

        self.blastLocation = JTextField("/Users/mbsulli/blast")
        self.databaseLocation = JTextField("/Users/mbsulli/blast/db")
        self.projects = JTabbedPane()
        
        constraints.gridx, constraints.gridy = 0, 0
        constraints.gridwidth, constraints.gridheight = 1, 1
        constraints.fill = GridBagConstraints.NONE
        constraints.weightx, constraints.weighty = 0, 0
        self.contentPane.add(JLabel("Blast Location"), constraints)
        constraints.gridx, constraints.gridy = 1, 0
        constraints.fill = GridBagConstraints.HORIZONTAL
        constraints.weightx, constraints.weighty = 1, 0
        self.contentPane.add(self.blastLocation, constraints)
        constraints.gridx, constraints.gridy = 2, 0
        constraints.fill = GridBagConstraints.NONE
        constraints.weightx, constraints.weighty = 0, 0
        self.contentPane.add(JButton(BlastAction(self)), constraints)
        constraints.gridx, constraints.gridy = 3, 0
        constraints.fill = GridBagConstraints.NONE
        constraints.weightx, constraints.weighty = 0, 0
        self.contentPane.add(JLabel("Database Location"), constraints)
        constraints.gridx, constraints.gridy = 4, 0
        constraints.fill = GridBagConstraints.HORIZONTAL
        constraints.weightx, constraints.weighty = 1, 0
        self.contentPane.add(self.databaseLocation, constraints)
        constraints.gridx, constraints.gridy = 5, 0
        constraints.fill = GridBagConstraints.NONE
        constraints.weightx, constraints.weighty = 0, 0
        self.contentPane.add(JButton(DatabaseAction(self)), constraints)
        constraints.gridx, constraints.gridy = 0, 1
        constraints.gridwidth, constraints.gridheight = 6, 1
        constraints.fill = GridBagConstraints.BOTH
        constraints.weightx, constraints.weighty = 1, 1
        self.contentPane.add(self.projects, constraints)

        self.projects.addTab("Phi-4-1", panel.ProfelisPanel(self, "/Users/mbsulli/neofelis/genomes/Phi-4-1"))
