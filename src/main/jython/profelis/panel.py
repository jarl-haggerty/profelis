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

import re
from javax.swing import JPanel
from javax.swing import JList
from javax.swing import JLabel
from javax.swing import JTextArea
from javax.swing import JTextField
from javax.swing import JButton
from javax.swing import ListCellRenderer
from javax.swing import ListSelectionModel
from javax.swing import DefaultListModel
from javax.swing import JScrollPane
from javax.swing import Action
from javax.swing import AbstractAction
from javax.swing import Timer
from javax.swing.event import ListSelectionListener
from javax.swing.border import LineBorder
from java.awt import Color
from java.awt import Font
from java.awt import GridBagLayout
from java.awt import GridBagConstraints
from java.awt.event import ActionListener

class NewGeneAction(ActionListener):
    def __init__(self, panel):
        AbstractAction.__init__(self, "New Gene")
        self.panel = panel

    def actionPerformed(self, event):
        if self.panel.newGeneFrom.text.isdigit() and self.panel.newGeneTo.text.isdigit():
            location = [int(self.panel.newGeneFrom.text.isdigit()), int(self.panel.newGeneTo.text.isdigit())]
            if location[0] > 0 and location[1] > 0:
                self.panel.outGenes.model.add(GeneCell(location, "", "", [0, 255, 255]))
                self.panel.newGeneFrom.background = self.panel.newGeneTo.background = Color.white
            else:
                self.panel.newGeneFrom.background = self.panel.newGeneTo.background = Color.red
        else:
            self.panel.newGeneFrom.background = self.panel.newGeneTo.background = Color.red

class BlastGenesAction(AbstractAction):
    def __init__(self, panel):
        AbstractAction.__init__(self, "Blast Genes")
        self.panel = panel

    def actionPerformed(self, event):
        pass

class AddGenesAction(AbstractAction):
    def __init__(self, panel):
        AbstractAction.__init__(self, "Add To Artemis File")
        self.panel = panel

    def actionPerformed(self, event):
        for element in self.panel.outGenes.model.elements():
            self.panel.inGenes.addElement(element)
        self.panel.outGenes.model.clear()

class RemoveAction(AbstractAction):
    def __init__(self, panel):
        AbstractAction.__init__(self, "Remove Marked Genes")
        self.panel = panel

    def actionPerformed(self, event):
        index = 0
        while index < self.panel.inGenes.model.size():
            if self.panel.inGenes.model.get(index).remove:
                self.panel.inGenes.model.remove(index)
            else:
                index += 1

        output = open(self.panel.fileName, "w")
        output.write(self.panel.restOfFile)
        for element in self.panel.inGenes.model.elements():
            output.write(str(element))
        output.write("\nORIGIN\n\n")
        for i in range(0, len(self.panel.genome), 50):
            output.write(self.panel.genome[i:min(i+50, len(self.panel.genome))] + "\n")
        output.close()

        self.panel.loadFile()

class MarkForRemovalListener(ActionListener):
    def __init__(self, panel):
        self.panel = panel

    def actionPerformed(self, event):
        self.panel.inGenes.selectedValue.remove = not self.panel.inGenes.selectedValue.remove
        self.panel.repaint()

class GeneCell():
    def __init__(self, location, gene, note, color):
        self.remove = False
        self.location = location
        self.gene = gene
        self.note = note
        self.color = color

    def __str__(self):
        locationString = "..".join(map(str, self.location))
        if self.location[1] < self.location[0]:
            locationString = "complement(" + locationString + ")"
        return "     CDS             " + locationString + "\n" + \
               "                     " + "/gene=\"" + self.gene + "\"\n" + \
               "                     " + "/note=\"" + self.note + "\"\n" + \
               "                     " + "/colour=" + " ".join(map(str, self.color)) + "\n"

class ProfelisCellRenderer(JTextArea, ListCellRenderer):
    def __init__(self):
        self.border = LineBorder(Color.black)
        self.font = Font("Monospaced", Font.PLAIN, self.font.size)
        
    def getListCellRendererComponent(self, list, value, index, isSelected, cellHasFocus):
        self.setText(str(value))
        if isSelected:
            self.background = list.selectionBackground
            self.foreground = list.selectionForeground
        else:
            self.background = list.background
            self.foreground = list.foreground
        if value.remove:
            self.background = Color.red
        return self

class MarkButtonLabeler(ActionListener):
    def __init__(self, panel):
        self.panel = panel

    def actionPerformed(self, event):
        if self.panel.inGenes.selectedValue and self.panel.inGenes.selectedValue.remove:
            self.panel.markForRemovalButton.text = "Unmark For Removal"
        else:
            self.panel.markForRemovalButton.text = "Mark For Removal"

class SearchListener(ActionListener):
    def __init__(self, panel):
        self.panel = panel

    def actionPerformed(self, event):
        if self.panel.searchField.text != self.panel.searchTerm:
            self.panel.searchTerm = self.panel.searchField.text
            self.panel.searchIndex = -1

        for index in range(self.panel.searchIndex+1, self.panel.inGenes.model.size()):
            if str(self.panel.inGenes.model.get(index)).find(self.panel.searchTerm) != -1:
                self.panel.inGenes.selectedIndex = self.panel.searchIndex = index
                self.panel.inGenes.ensureIndexIsVisible(self.panel.inGenes.selectedIndex)
                break

class ProfelisPanel(JPanel):
    def __init__(self, fileName):
        self.fileName = fileName
        self.searchTerm = None
        self.searchIndex = -1

        self.searchField = JTextField("")
        self.searchField.addActionListener(SearchListener(self))

        self.newGeneFrom = JTextField("")
        self.newGeneTo = JTextField("")
        self.newGeneButton = Jbutton("New Gene")
        newGeneActionListener = NewGeneActionListener()
        self.newGeneFrom.addActionListener(newGeneActionListener)
        self.newGeneTo.addActionListener(newGeneActionListener)
        self.newGeneButton.addActionListener(newGeneActionListener)

        self.markForRemovalButton = JButton("Mark For Removal")
        self.markForRemovalButton.addActionListener(MarkForRemovalListener(self))
        
        self.inGenes = JList(DefaultListModel())
        self.inGenes.selectionMode = ListSelectionModel.SINGLE_SELECTION
        self.inGenes.cellRenderer = ProfelisCellRenderer()
        self.markButtonLabelerTimer = Timer(100, MarkButtonLabeler(self))
        self.markButtonLabelerTimer.start()
        self.loadFile()

        self.outGenes = JList(DefaultListModel())
        self.outGenes.selectionMode = ListSelectionModel.SINGLE_SELECTION
                
        constraints = GridBagConstraints()
        self.layout = GridBagLayout()
        
        constraints.gridx, constraints.gridy = 0, 0
        constraints.gridwidth, constraints.gridheight = 1, 1
        constraints.fill = GridBagConstraints.NONE
        constraints.weightx, constraints.weighty = 0, 0
        self.add(JLabel("Genes In Artemis File"), constraints)
        constraints.gridx, constraints.gridy = 0, 1
        self.add(JButton(RemoveAction(self)), constraints)
        constraints.gridx, constraints.gridy = 1, 1
        self.add(self.markForRemovalButton, constraints)
        constraints.gridx, constraints.gridy = 2, 1
        self.add(JLabel("Search"), constraints)
        constraints.gridx, constraints.gridy = 3, 1
        constraints.fill = GridBagConstraints.HORIZONTAL
        self.add(self.searchField, constraints)
        constraints.gridx, constraints.gridy = 0, 2
        constraints.gridwidth, constraints.gridheight = 4, 1
        constraints.fill = GridBagConstraints.BOTH
        constraints.weightx, constraints.weighty = 1, 1
        self.add(JScrollPane(self.inGenes), constraints)

        constraints.gridx, constraints.gridy = 4, 0
        constraints.gridwidth, constraints.gridheight = 1, 1
        constraints.fill = GridBagConstraints.NONE
        constraints.weightx, constraints.weighty = 0, 0
        self.add(JLabel("Genes To Add To Artemis File"), constraints)
        constraints.gridx, constraints.gridy = 4, 1
        self.add(JButton(self.newGeneButton), constraints)
        constraints.gridx, constraints.gridy = 5, 1
        self.add(JButton(BlastGenesAction(self)), constraints)
        constraints.gridx, constraints.gridy = 6, 1
        self.add(JButton(AddGenesAction(self)), constraints)
        constraints.gridx, constraints.gridy = 4, 2
        constraints.gridwidth, constraints.gridheight = 3, 1
        constraints.fill = GridBagConstraints.BOTH
        constraints.weightx, constraints.weighty = 1, 1
        self.add(JScrollPane(self.outGenes), constraints)

    def loadFile(self):
        input = open(self.fileName, "r")
        lines = input.readlines()
        input.close()
        self.inGenes.model.clear()
        self.restOfFile = ""
        self.genome = ""
        while lines:
            if lines[0].find("     CDS") == 0:
                self.inGenes.model.addElement(GeneCell(map(int, re.findall("(\d+)\.\.(\d+)", lines[0])[0]),
                                                       re.findall("/gene=\"(.*)\"", lines[1])[0],
                                                       re.findall("/note=\"(.*)\"", lines[2])[0],
                                                       map(int, re.findall("/colour=(\d+)\s+(\d+)\s+(\d+)", lines[3])[0])))
                lines = lines[4:]
            elif lines[0].find("ORIGIN") == 0:
                self.genome = "".join(lines[1:]).replace("\n", "").strip()
                lines = None
            elif lines[0].strip():
                self.restOfFile += lines[0]
                lines = lines[1:]
            else:
                lines = lines[1:]
