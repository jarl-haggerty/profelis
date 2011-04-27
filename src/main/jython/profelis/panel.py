

from profelis import utils
from profelis import xml
import re
import os
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


class NewGeneActionListener(ActionListener):
    def __init__(self, panel):
        self.panel = panel

    def actionPerformed(self, event):
        if self.panel.newGeneFrom.text.isdigit() and self.panel.newGeneTo.text.isdigit():
            location = [int(self.panel.newGeneFrom.text), int(self.panel.newGeneTo.text)]
            if location[0] > 0 and location[1] > 0:
                self.panel.outGenes.model.addElement(utils.Iteration(location))
                self.panel.newGeneFrom.background = self.panel.newGeneTo.background = Color.white
            else:
                self.panel.newGeneFrom.background = self.panel.newGeneTo.background = Color.red
        else:
            self.panel.newGeneFrom.background = self.panel.newGeneTo.background = Color.red

class AddGenesAction(AbstractAction):
    def __init__(self, panel):
        AbstractAction.__init__(self, "Add Genes")
        self.panel = panel

    def actionPerformed(self, event):
        output = open("profelis.query.fas", "w")
        for gene in self.panel.outGenes.model.elements():
            print gene.location
            if gene.location[0] < gene.location[1]:
                proteins = utils.translate(self.panel.genome[gene.location[0]-1:gene.location[1]])
            else:
                proteins = utils.translate(utils.reverseComplement(self.panel.genome[gene.location[1]-1:gene.location[0]]))
            output.write(">profelis" + ":" + "-".join(map(str, gene.location)) + "\n")
            for i in xrange(0, len(proteins), 50):
                output.write(proteins[i:min(i+50, len(proteins))] + "\n")
        output.close()
        
        self.panel.frame.blastLocation.background = Color.white
        self.panel.frame.databaseLocation.background = Color.white
        try:
            utils.cachedBlast("profelis.query.blastp.xml", self.panel.frame.blastLocation.text, self.panel.frame.databaseLocation.text + "/" + self.panel.database, self.panel.evalue, "profelis.query.fas", self.panel, True)
        except OSError:
            self.panel.frame.blastLocation.background = Color.red
            self.panel.frame.databaseLocation.background = Color.red

        genes = utils.parseBlast("profelis.query.blastp.xml")[2]
        self.panel.outGenes.model.clear()
        [self.panel.inGenes.model.addElement(gene) for gene in genes]

        xml.addGenes(self.panel.name + ".blastp.xml", "profelis.query.blastp.xml")
        
class RemoveAction(AbstractAction):
    def __init__(self, panel):
        AbstractAction.__init__(self, "Remove Marked Genes")
        self.panel = panel

    def actionPerformed(self, event):
        index = 0
        removed = []
        while index < self.panel.inGenes.model.size():
            if self.panel.inGenes.model.get(index).remove:
                removed.append(self.panel.inGenes.model.remove(index).location[0])
            else:
                index += 1

        xml.deleteGenes(self.panel.name + ".blastp.xml", removed)

        output = open(self.panel.name + ".art", "w")
        output.write(self.panel.restOfFile)
        for element in self.panel.inGenes.model.elements():
            output.write(element.toArtemis())
        output.write("\nORIGIN\n\n")
        for i in range(0, len(self.panel.genome), 50):
            output.write(self.panel.genome[i:min(i+50, len(self.panel.genome))] + "\n")
        output.close()        

class MarkForRemovalListener(ActionListener):
    def __init__(self, panel):
        self.panel = panel

    def actionPerformed(self, event):
        self.panel.inGenes.selectedValue.remove = not self.panel.inGenes.selectedValue.remove
        self.panel.repaint()

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
    def __init__(self, frame, name):
        self.frame = frame
        self.exception = None
        self.name = name
        self.searchTerm = None
        self.searchIndex = -1

        self.searchField = JTextField("")
        self.searchField.addActionListener(SearchListener(self))

        self.newGeneFrom = JTextField("")
        self.newGeneTo = JTextField("")
        self.newGeneButton = JButton("New Gene")
        newGeneActionListener = NewGeneActionListener(self)
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
        self.outGenes.cellRenderer = ProfelisCellRenderer()
                
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
        constraints.gridwidth, constraints.gridheight = 4, 2
        constraints.fill = GridBagConstraints.BOTH
        constraints.weightx, constraints.weighty = 1, 1
        self.add(JScrollPane(self.inGenes), constraints)

        constraints.gridx, constraints.gridy = 4, 0
        constraints.gridwidth, constraints.gridheight = 1, 1
        constraints.fill = GridBagConstraints.NONE
        constraints.weightx, constraints.weighty = 0, 0
        self.add(JLabel("Genes To Add To Artemis File"), constraints)
        constraints.gridx, constraints.gridy = 4, 1
        self.add(self.newGeneButton, constraints)
        constraints.weightx = 1
        constraints.fill = GridBagConstraints.BOTH
        constraints.gridx, constraints.gridy = 5, 1
        self.add(self.newGeneFrom, constraints)
        constraints.weightx = 0
        constraints.fill = GridBagConstraints.NONE
        constraints.gridx, constraints.gridy = 6, 1
        self.add(JLabel("To"), constraints)
        constraints.weightx = 1
        constraints.fill = GridBagConstraints.BOTH
        constraints.gridx, constraints.gridy = 7, 1
        self.add(self.newGeneTo, constraints)

        constraints.weightx = 0
        constraints.fill = GridBagConstraints.NONE
        constraints.gridx, constraints.gridy = 4, 2
        self.add(JButton(AddGenesAction(self)), constraints)
        constraints.gridx, constraints.gridy = 4, 3
        constraints.gridwidth, constraints.gridheight = 4, 1
        constraints.fill = GridBagConstraints.BOTH
        constraints.weightx, constraints.weighty = 1, 1
        self.add(JScrollPane(self.outGenes), constraints)

    def loadFile(self):
        self.inGenes.model.clear()
        self.database, self.evalue, genes = utils.parseBlast(self.name + ".blastp.xml")
        [self.inGenes.model.addElement(gene) for gene in genes]

        artemisInput = open(self.name + ".art", "r")
        lines = artemisInput.readlines()
        artemisInput.close()
        self.restOfFile = self.genome = []
        while lines:
            if re.match("\s+CDS\s+(complement\()?\d+\.\.\d+\)?\n", lines[0]):
                lines = lines[4:]
            elif lines[0].find("ORIGIN") == 0:
                self.genome = map(lambda x: re.sub("\s+", "", x), lines[1:])
                lines = []
            else:
                if lines[0].strip():
                    self.restOfFile.append(lines[0])
                lines = lines[1:]
                
        self.genome = "".join(self.genome)
        self.restOfFile = "".join(self.restOfFile)
            
                
