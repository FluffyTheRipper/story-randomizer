import sys
import random
import qdarkstyle
import json
import jsonpickle
import pdf_report
import os
import copy
import math
from configparser import ConfigParser
from classes import *
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QErrorMessage, QPushButton, QToolButton, QComboBox, QHBoxLayout,QVBoxLayout, QFileDialog, QButtonGroup, QRadioButton, QFrame, QToolTip



# Refactor the selector toggle and the button presses, different regions take different inputs so its fucked rn. 

# Hover Hints


config_object = ConfigParser()
config_object.read('config.ini')

BG_COLOURS = config_object['BG_COLOURS']
TEXT_COLOURS = config_object['TEXT_COLOURS']


# ========================== DEFINITIONS ============================
FILE_PATH = ""
BLANK_TEXT = "--"

HEADING_FONT = QFont()
HEADING_FONT.setBold(True)

COLOR_HEADING_BACKGROUND = "background-color: grey"

def_char_names = ["Eins","Zwei","Drei","Vier","Funf","Sechs","Sieben","Acht","Neun","Zehn"]

dynamics = {"Resolve":["Change", "Steadfast"],
            "Growth":["Start", "Stop"],
            "Approach":["Do-er", "Be-er"],
            "Mental Sex":["Male", "Female"],
            "OS Driver":["Action", "Decision"],
            "OS Limit":["Timelock", "Optionlock"],
            "OS Outcome":["Good", "Bad"],
            "MC Judgement":["Good1", "Bad1"]}

c_dynamics = ["Resolve","Change", "Steadfast",
            "Growth","Start", "Stop",
            "Approach","Do-er", "Be-er",
            "Mental Sex","Male", "Female"]
            
p_dynamics = ["OS Driver","Action", "Decision",
            "OS Limit","Timelock", "Optionlock",
            "OS Outcome","Good", "Bad",
            "MC Judgement","Good", "Bad"]

dynamic_headings = ["Resolve",
                    "Growth",
                    "Approach",
                    "Mental Sex",
                    "OS Driver",
                    "OS Limit",
                    "OS Outcome",
                    "MC Judgement"]

opposites = {'Situation'  : 'Mind',
            'Activity'    : 'Manipulation',
            'Manipulation': 'Activity',
            'Mind'        : 'Situation'}

STYLE = {'Situation'    : "background-color:rgb(56, 145, 166);  color:white",
         'Mind'         : "background-color:rgb(81, 70, 99);    color:white",
         'Manipulation' : "background-color:rgb(214, 69, 80);   color:white",
         'Activity'     : "background-color:rgb(82, 170, 94);   color:white",
         'Disabled'     : "background-color:rgb(100,100,100);   color:white"
        }

with open('./data/throughlines_master.txt') as f:
    TL = f.read()

root = Node('root')
root.add_children([Node(line) for line in TL.splitlines() if line.strip()])

classes = []
types = []
variants = []
elements = []

for ch in root.children:
    classes.append(ch)
    for ty in ch.children:
        types.append(ty)
        for var in ty.children:
            variants.append(var)
            for elem in var.children:
                elements.append(elem)

node_levels = {0: classes,
            1: types,
            2: variants,
            3: elements}

characters = []
characters_bak = []

selector_button = None
selector_node = None

with open('./data/character_traits.txt') as f:
    traits = f.read().splitlines()

with open('./data/tooltips.txt') as f:
    tooltips = f.read().splitlines()

tooltip_delimeter = tooltips[0].split('"')[1]

def get_tooltip(text=None):
    for tt in tooltips:
        name = tt.split(tooltip_delimeter)
        if text == name[0]: 
            return name[1]
    return "Tooltip missing, add definition to tooltips.txt. Verify delimeter is correct"

def change_style_color(style, bg_color, text_color):
    style_string = f"""QPushButton {{
                            background-color: rgb{bg_color}; 
                            color: rgb{text_color};
                            }}
                        QToolTip {{
                            color: black; 
                            background-color: rgb(240,240,240); 
                            border: 1px solid black; 
                            }}
                        """
    try:
        STYLE[style] = (style_string)
    except:
        print('Style change error')
        return

def refresh_styles():
    for branch in root.children:
        style = STYLE[branch.text]
        branch.style = style
        for child in branch.children:
            child.parent = branch
            child.branch = branch
            child.style = style
            for g_child in child.children:
                g_child.parent = child
                g_child.branch = branch
                g_child.style = style
                for gg_child in g_child.children:
                    gg_child.parent = g_child
                    gg_child.branch = branch
                    gg_child.style = style

class SelectorWindow(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("./ui/selector_window.ui",self)

        self.setWindowIcon(QIcon('./ui/icon.png'))

        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, False)

    def keyPressEvent(self, event):
        if event.key() == 16777216: #Escape key
            self.hide()
            mainwindow.setEnabled(True)
            return
        super().keyPressEvent(event)

    def update_buttons(self, options, legal_options=None, bool_legal_only=False):
        for i in reversed(range(self.grid_buttons.count())): 
            self.grid_buttons.itemAt(i).widget().setParent(None)

        grid_size = int(math.sqrt(len(options)))

        if grid_size == 4: # this hard coded shit swaps the order of the list so its arranged in quadrants.
            options[2], options[3], options[4], options[5] = options[4], options[5], options[2], options[3]
            options[10], options[11], options[12], options[13] = options[12], options[13], options[10], options[11]

        self.sent_options = []
        self.sent_options.extend(options)

        positions = [(x,y) for x in range(grid_size) for y in range(grid_size)]
        for i, pos in enumerate(positions):
            button = QPushButton(options[i].text, self)
            button.setStyleSheet(options[i].style)
            button.setToolTip(get_tooltip(options[i].text))
            button.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                                        QtWidgets.QSizePolicy.MinimumExpanding))

            button.clicked.connect(self.button_clicked)

            if legal_options and bool_legal_only == 2:
                if options[i] not in legal_options:
                    button.setEnabled(False)
                    button.setStyleSheet(STYLE['Disabled'])

            self.grid_buttons.addWidget(button, *pos)
     


    def button_clicked(self):
        global selector_node
        global selector_button
        for i, b in enumerate(self.grid_buttons.parentWidget().findChildren(QPushButton)):
            if b == self.sender():
                selector_node = self.sent_options[i]
                break

        mainwindow.toggle_selector()

        layout = selector_button.parent().layout()
        

        if layout == mainwindow.grid_throughlines:
            idx = layout.indexOf(selector_button)
            pos = layout.getItemPosition(idx)
            if pos == (1,3,1,1): # MC Problem cell
                mainwindow.copy_throughline_extras()

            if mainwindow.chk_Seq_Thro.checkState() == 2:
                if pos[1] < 3:
                    next_button = layout.itemAtPosition(pos[0],pos[1]+1).widget()
                    mainwindow.b_throughline_clicked(next_button)
                else:
                    return

        if layout == mainwindow.grid_acts:
            idx = layout.indexOf(selector_button)
            pos = layout.getItemPosition(idx)
            if mainwindow.chk_Seq_Acts.checkState() == 2:
                if pos[1] < 3:
                    next_button = layout.itemAtPosition(pos[0],pos[1]+1).widget()
                    mainwindow.b_acts_clicked(next_button)
                else:
                    return

        return

class CharWindow(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("./ui/char_window.ui",self)

        self.setWindowIcon(QIcon('./ui/icon.png'))
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, False)
        
        # global traits
        self.listWidget_Chars.clear()
          
        for c in def_char_names:
            characters.append(Character(c))
        self.update_char_list()
       
        self.b_Done.clicked.connect(self.Done)
        # self.b_Cancel.clicked.connect(self.Cancel)

        self.char_name_box.returnPressed.connect(self.Add) # Add when return is pressed as well)
        self.char_name_box.textChanged.connect(self.name_check)

        self.b_Add.clicked.connect(self.Add)
        self.b_Delete.clicked.connect(self.Delete) 
        self.b_Edit.clicked.connect(self.Edit)
        self.b_Edit_Save.clicked.connect(self.Edit_Save)
        self.b_Edit_Cancel.clicked.connect(self.Edit_Cancel)

        self.b_Rand_Traits.clicked.connect(self.Randomize_Traits)

        self.chk_Min.stateChanged.connect(self.chk_min)
        self.chk_Max.stateChanged.connect(self.chk_max)
        self.sb_Min.valueChanged.connect(self.spinbox_Min)
        self.sb_Max.valueChanged.connect(self.spinbox_Max)
        self.chk_Highlight.stateChanged.connect(self.chk_highlight)

        trait_boxes = (self.grid_traits.itemAt(i).widget() for i in range(self.grid_traits.count()))
        for i, t in enumerate(trait_boxes):
            t.setText(traits[i])
            t.setEnabled(False)
            t.setToolTip(get_tooltip(traits[i]))

        self.editing_char = None

    def chk_highlight(self):
        self.update_char_list()

    def chk_min(self):
        if self.chk_Min.checkState():
            self.sb_Min.setEnabled(True)
        else:
            self.sb_Min.setEnabled(False)

    def chk_max(self):
        if self.chk_Max.checkState():
            self.sb_Max.setEnabled(True)
        else:
            self.sb_Max.setEnabled(False)

    def spinbox_Min(self):
        mi = self.sb_Min.value()
        ma = self.sb_Max.value()
        if mi > ma:
            self.sb_Max.setValue(mi)
            return

    def spinbox_Max(self):
        mi = self.sb_Min.value()
        ma = self.sb_Max.value()
        if ma < mi:
            self.sb_Min.setValue(ma)
            return

    def Randomize_Traits(self):
        if not characters:
            print('No characters listed, doofus')
            return
        else:
            # ADD LOGIC TO ACCOUNT FOR DIFFERENT GENERATION MODES (MAX/MIN/UNIQUE)
            randomized_traits = copy.copy(traits)
            random.shuffle(randomized_traits)

            max_traits = len(traits)
            min_traits = 0
            bool_unique = False
            bool_min = False
            bool_min = False

            for c in characters:
                c.traits = []

            if self.chk_Max.checkState() == 2: max_traits = self.sb_Max.value()
            if self.chk_Min.checkState() == 2: min_traits = self.sb_Min.value()
            if self.chk_Unique.checkState() == 2: bool_unique = True

            if bool_unique:
                for trait in randomized_traits:
                    
                    c_least_traits = len(randomized_traits)

                    for c in characters: # Find least number of traits
                        if len(c.traits) < c_least_traits: 
                            c_least_traits = len(c.traits)

                    c_valid = [] # Reset list of valid characters
                    for c in characters:
                        no_traits = len(c.traits)
                        if c_least_traits < min_traits: # There are characters that don't meet the requirement. 
                            if no_traits == c_least_traits: # If a character has the least number of traits
                                c_valid.append(c)

                        else: # If all characters at least have the minimum
                            if no_traits < max_traits:
                                c_valid.append(c)

                    if c_valid: # if there are valid characters left
                        c = random.choice(c_valid)
                        c.add_trait(trait)

                    else:
                        break

            else: # Selection with duplicates
                for c in characters:
                    num_traits = random.randint(min_traits, max_traits)
                    sample = random.sample(randomized_traits,num_traits)

                    for t in sample:
                        c.add_trait(t)          
            
            self.update_char_list()
    
    def name_check(self):
        name = self.char_name_box.text()
        existing = []
        for c in characters:
            existing.append(c.name)

        if self.editing_char:
            if name == self.editing_char.name:
                self.lbl_Debug.setText("Current Name")
                return False

        if name in existing:
            self.lbl_Debug.setText("Already Exists") 
            return True
        else:
            self.lbl_Debug.setText(" ") 
            return False

    def Done(self):
        mainwindow.update_char_layout()
        mainwindow.edit_chars()

    def Cancel(self):
        mainwindow.update_char_layout()
        mainwindow.edit_chars()

    def Add(self):
        if not self.char_name_box.text():
            return
        else:
            if not self.name_check(): 
                characters.append(Character(self.char_name_box.text()))
                self.update_char_list()
                self.char_name_box.setText("")

    def Edit(self):
        sel = self.listWidget_Chars.selectedItems()
        if not sel:
            return   
        else:    
            x = sel[0].text().split(' - ')[0]
            for i, c in enumerate(characters):
                if c.name == x:
                    self.editing_char = c
                    break
            if not self.editing_char:
                print('das fuq?')

            self.toggle_edit(True)
            
            self.char_name_box.setText(x)

            trait_boxes = (self.grid_traits.itemAt(i).widget() for i in range(self.grid_traits.count()))
            for t in trait_boxes:
                t.setChecked(False)
                if t.text() in self.editing_char.traits:
                    t.setChecked(True)

    def Edit_Save(self):
        if not self.name_check():
            self.editing_char.traits = []
            trait_boxes = (self.grid_traits.itemAt(i).widget() for i in range(self.grid_traits.count()))
            for t in trait_boxes:
                if t.isChecked():
                    self.editing_char.traits.append(t.text())
                    t.setChecked(False)

            self.editing_char.name = self.char_name_box.text()
            self.char_name_box.setText("")
            self.toggle_edit(False)
            self.editing_char = None
            self.update_char_list()
        else:
            return

    def Edit_Cancel(self):
        self.toggle_edit(False)
        self.char_name_box.setText("")
        self.toggle_edit(False)
        self.editing_char = None

    def toggle_edit(self, state): #TURN ELEMENTS ON/OFF TO STOP FUCKERY
        trait_boxes = (self.grid_traits.itemAt(i).widget() for i in range(self.grid_traits.count()))
        for t in trait_boxes:
            t.setEnabled(state)
            if not state:
                t.setChecked(False)

        self.b_Edit_Save.setEnabled(state)
        self.b_Edit_Cancel.setEnabled(state)

        self.b_Add.setEnabled(not state)
        self.b_Edit.setEnabled(not state)
        self.b_Delete.setEnabled(not state)
        self.listWidget_Chars.setEnabled(not state)
        self.b_Done.setEnabled(not state)

    def Delete(self):
        sel = self.listWidget_Chars.selectedItems()
        if not sel:
            return   
        else:    
            x = sel[0].text().split(' - ')[0]
            for c in characters:
                if c.name == x:
                    characters.remove(c)
                    self.update_char_list()
                    self.listWidget_Chars.setCurrentRow(self.listWidget_Chars.count()-1)
                    return

    def update_char_list(self):
        c_name_trait = []
        self.listWidget_Chars.clear()
        for c in characters:

            x = c.name + " - " + (", ").join(c.traits)
            c_name_trait.append(x)
        self.listWidget_Chars.addItems(c_name_trait)
        
        if self.chk_Highlight.checkState() == 2:
            self.find_duplicate_traits()

    def find_duplicate_traits(self):
        distribution = {}
        dup_chars = []
        for t in traits:
            distribution[t] = 0
            for c in characters:
                if t in c.traits:
                    distribution[t] += 1
        for k, v in distribution.items():
            if v > 1:
                for i, c in enumerate(characters):
                    if k in c.traits:
                        self.listWidget_Chars.item(i).setBackground(Qt.lightGray)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("./ui/main_window.ui",self)

        self.setWindowIcon(QIcon('./ui/icon.png'))

        self.emsg = QErrorMessage()
        self.emsg.setWindowModality(QtCore.Qt.WindowModal)
        self.emsg.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        self.initUI()
        self.char_window = CharWindow()
        self.selector_window = SelectorWindow()

        self.b_Edit_Characters.clicked.connect(self.edit_chars)
        self.b_clear_dyn.clicked.connect(self.clear_dynamics)
        self.b_rand_dyn_miss.clicked.connect(self.rand_dynamics_missing)
        self.b_rand_dyn_all.clicked.connect(self.rand_dynamics_all)   

        self.b_rand_thr_all.clicked.connect(self.rand_throughlines_all) 
        self.b_rand_abs_all.clicked.connect(self.rand_abstracts_all)
        self.b_rand_acts_all.clicked.connect(self.rand_acts_all)

        self.b_rand_EVERYTHING.clicked.connect(self.rand_EVERYTHING)

        self.b_Crucial_Element.clicked.connect(self.b_crucial_clicked)
        self.b_clear_thro.clicked.connect(self.b_clear_throughlines)
        self.b_clear_abstracts.clicked.connect(lambda: self.reset_button_layout(self.grid_abstracts))
        self.b_clear_acts.clicked.connect(lambda: self.reset_button_layout(self.grid_acts))

    def initUI(self):

        # Load colors from config file
        for branch in root.children:
            change_style_color(branch.text, BG_COLOURS[branch.text], TEXT_COLOURS[branch.text])
        refresh_styles()

        self.actionNew.setShortcut('Ctrl+N')
        self.actionNew.setStatusTip('New document')
        self.actionNew.triggered.connect(self.newCall)

        self.actionOpen.setShortcut('Ctrl+O')
        self.actionOpen.setStatusTip('Open document')
        self.actionOpen.triggered.connect(self.openCall)

        self.actionSave.setShortcut('Ctrl+S')
        self.actionSave.setStatusTip('Save document')
        self.actionSave.triggered.connect(self.saveCall)

        self.actionExport_pdf.setShortcut('Ctrl+E')
        self.actionExport_pdf.setStatusTip('Export to .pdf')
        self.actionExport_pdf.triggered.connect(self.exportCall)

        self.update_char_layout()

        # Fill Throughline and Acts grids with buttons
        positions = [(i, j) for i in range(4) for j in range(4)]
        for i, pos in enumerate(positions):
            widget = QPushButton('th_'+str(i),self)
            widget.clicked.connect(self.b_throughline_clicked)
            widget.setText(BLANK_TEXT)
            self.grid_throughlines.addWidget(widget, *pos)

            widget = QPushButton('ac_'+str(i),self)
            widget.clicked.connect(self.b_acts_clicked)
            widget.setText(BLANK_TEXT)
            self.grid_acts.addWidget(widget,*pos)

        for i, button in enumerate(self.grid_abstracts.parentWidget().findChildren(QPushButton)):
            button.setText(BLANK_TEXT)
            button.clicked.connect(self.b_abstract_clicked)

        # GENERATE THE DYNAMICS TABLES WITH BUTTONS N SHIT
        positions = [(i, j) for i in range(8) for j in range(3)]
        for x in range(3):
            self.grid_c_dynamics.setColumnMinimumWidth(x,150)
            self.grid_p_dynamics.setColumnMinimumWidth(x,150)

        for position, name in zip (positions, c_dynamics):
            if name in dynamic_headings:
                widget = QLabel(name,self)
                widget.setFont(HEADING_FONT)
                widget.setAlignment(Qt.AlignCenter)
            else:
                widget = QPushButton(name,self)
                widget.setCheckable(True)
                widget.clicked.connect(self.opt_flip)
                widget.setObjectName(name)
            self.grid_c_dynamics.addWidget(widget, *position)
            
        for position, name in zip (positions, p_dynamics):
            if name in dynamic_headings:
                widget = QLabel(name,self)
                widget.setFont(HEADING_FONT)

                widget.setAlignment(Qt.AlignCenter)
            else:
                widget = QPushButton(name,self)
                widget.setCheckable(True)
                widget.clicked.connect(self.opt_flip)
                if self.findChild(QPushButton, name) == None:
                    widget.setObjectName(name)
                else:
                    widget.setObjectName(name+str(1))

            self.grid_p_dynamics.addWidget(widget, *position)

    def set_node_button(self, button, text, style):
        button.setText(text)
        button.setStyleSheet(style)
        button.setToolTip(get_tooltip(text))

    def b_clear_throughlines(self):
        self.reset_button_layout(self.grid_throughlines)
        self.set_node_button(self.b_Crucial_Element,BLANK_TEXT, "")

    def copy_throughline_extras(self):
        crucial_text = self.grid_throughlines.itemAtPosition(1,3).widget().text()

        if crucial_text != BLANK_TEXT:
            crucial_node = self.find_node(crucial_text, self.grid_throughlines.itemAtPosition(1,0).widget().text())
            
            self.set_node_button(self.b_Crucial_Element,crucial_node.text, crucial_node.style)
            self.set_node_button(self.grid_throughlines.itemAtPosition(0,3).widget(),crucial_node.text, crucial_node.style)

    def b_throughline_clicked(self, button=None):
        if not button:
            button = self.sender()
        else:
            print('prog exec')

        layout = button.parent().layout()
        idx = layout.indexOf(button)
        pos = layout.getItemPosition(idx)

        siblings = []
        cousins = []

        if pos[1] == 0: # if its a root branch
            cousins = root.children
            selected = []

            for y in range(4):
                text = layout.itemAtPosition(y,0).widget().text()
                if self.find_node(text): selected.append(self.find_node(text))

            for branch in cousins:
                if branch not in selected:
                    siblings.append(branch)

        else:
            branch_text = layout.itemAtPosition(pos[0],0).widget().text()
            parent_text = layout.itemAtPosition(pos[0],pos[1]-1).widget().text()

            try:
                parent_node = self.find_node(parent_text, branch_text, pos[1]-1)
                siblings.extend(parent_node.children)
                cousins = self.find_cousins(parent_node)
            except:
                print('exception')
                return
        try:
            self.toggle_selector(button, layout, idx, pos, cousins, siblings, self.chk_Legal_Only_Thro.checkState())
        except:
            return

    def b_crucial_clicked(self):
        layout = self.grid_throughlines

        branch_node_text = layout.itemAtPosition(1,0).widget().text()
        branch_node = self.find_node(branch_node_text)

        mc_problem_text = layout.itemAtPosition(1,3).widget().text()
        mc_problem_node = self.find_node(mc_problem_text, branch_node_text, 3)

        parent_node_text = layout.itemAtPosition(1,2).widget().text()
        if parent_node_text != BLANK_TEXT:
            try:
                siblings = []
                cousins = []
                parent_node = self.find_node(parent_node_text, branch_node_text, 2)

                siblings.append(mc_problem_node)

                cousins = self.find_cousins(parent_node)
                self.toggle_selector(self.sender(), layout, None, None, cousins, siblings, self.chk_Legal_Only_Thro.checkState())
            except:
                print('exception')
                return

    def b_abstract_clicked(self):
        button = self.sender()
        options_all = copy.copy(types)
        selected = []

        for b in self.grid_abstracts.parentWidget().findChildren(QPushButton):
            if b.text() != BLANK_TEXT:
                selected.append(self.find_node(b.text()))

        legal_options = []

        for o in options_all:
            if o in selected:
                continue
            legal_options.append(o)

        self.toggle_selector(button, self.grid_abstracts, None, None, options_all, legal_options, self.chk_Legal_Only_Abstracts.checkState())

    def b_acts_clicked(self, button=None):
        if not button:
            button = self.sender()
        else:
            print('prog exec')

        layout = button.parent().layout()
        idx = layout.indexOf(button)
        pos = layout.getItemPosition(idx)

        branch_text = self.grid_throughlines.itemAtPosition(pos[0],0).widget().text()
        branch = self.find_node(branch_text)

        if not branch:
            return

        acts_all = []
        acts_all.extend(branch.children)

        acts_picked = []
        for x in range(4):
            if x == pos[1]:
                continue
            picked_text = layout.itemAtPosition(pos[0],x).widget().text()
            if picked_text != BLANK_TEXT:
                acts_picked.append(self.find_node(picked_text))

        acts_legal = []
        for act in acts_all:
            if act not in acts_picked: 
                acts_legal.append(act)

        try:
            self.toggle_selector(button, layout, idx, pos, acts_all, acts_legal, self.chk_Legal_Only_Acts.checkState())
        except:
            return

    def toggle_selector(self, button=None, layout=None, idx=None, pos=None, cousins=None, siblings=None, bool_legal_only=False):
        global selector_node
        global selector_button

        if self.selector_window.isVisible():

            self.set_node_button(selector_button, selector_node.text, selector_node.style)
            self.selector_window.hide()
            self.setEnabled(True)
                 
            selector_button_layout = selector_button.parent().layout()
            
            if selector_button_layout == self.grid_throughlines:
                idx = selector_button_layout.indexOf(selector_button)
                pos = selector_button_layout.getItemPosition(idx)
                for x in range(pos[1]+1,4):
                    b = selector_button_layout.itemAtPosition(pos[0],x).widget()
                    self.set_node_button(b, BLANK_TEXT, "")

        else:
            selector_button = button
            self.selector_window.show() 
            self.selector_window.update_buttons(cousins, siblings, bool_legal_only)
            self.setEnabled(False)

    def find_cousins(self, parent_node):
        cousins = []

        if parent_node.level == 0:
            cousins.extend(parent_node.children)

        else:
            for gp_node in node_levels[parent_node.level-1]:
                for p_node in gp_node.children:
                    if p_node == parent_node:
                        grandparent = gp_node
                        break

            for au in grandparent.children:
                for c in au.children:
                    cousins.append(c)
        return cousins

    def find_chars(self, trait):
        data = []
        for c in characters:
            if trait in c.traits:
                data.append(c.name)
        return data

    def edit_chars(self):
        if self.char_window.isVisible():
            self.char_window.hide()
            self.show()
            self.setEnabled(True)
            
        else:
            self.char_window.show() 
            self.hide()
            self.setEnabled(False)
            self.char_window.update_char_list()

    def update_char_layout(self):
        global characters
        # Clear the layouts of any existing labels
        for label in self.layout_chars.parentWidget().findChildren(QLabel):
            label.setParent(None)

        for label in self.layout_traits.parentWidget().findChildren(QLabel):
            label.setParent(None)

        max_col = 3
        cur_col = 0
        cur_row = 0

        c_names = []
        c_traits = []

        for c in characters: 
            c_names.append(c.name)
            c_traits.append((", ").join(c.traits))

        for i, c in enumerate(c_names):
            c_widget = QLabel(c,self)
            c_widget.setFont(HEADING_FONT)
            c_widget.setAlignment(Qt.AlignCenter)
            c_widget.setText(c)
            c_widget.setFrameStyle(1)
            c_widget.setFrameShape(QFrame.Box)
            c_widget.setFrameShadow(QFrame.Plain)
            c_widget.setStyleSheet(COLOR_HEADING_BACKGROUND)
            
            
            t_widget = QLabel(c_traits[i],self)
            t_widget.setAlignment(Qt.AlignCenter)
            t_widget.setText(c_traits[i])
            t_widget.setFrameStyle(1)
            t_widget.setFrameShape(QFrame.Box)
            t_widget.setFrameShadow(QFrame.Plain)
            t_widget.setWordWrap(True)
            # t_widget.setMinimumSize(t_widget.sizeHint())

            self.layout_chars.addWidget(c_widget,cur_row,cur_col)
            self.layout_chars.addWidget(t_widget,cur_row+1,cur_col)
            
            if cur_col < max_col:
                cur_col += 1
            else:
                cur_col = 0
                cur_row += 2

        cur_col = 0
        cur_row = 0

        for trait in traits:
            t_widget = QLabel(trait,self)
            t_widget.setFont(HEADING_FONT)
            t_widget.setAlignment(Qt.AlignCenter)
            t_widget.setText(trait)
            t_widget.setFrameStyle(1)
            t_widget.setFrameShape(QFrame.Box)
            t_widget.setFrameShadow(QFrame.Plain)
            t_widget.setStyleSheet(COLOR_HEADING_BACKGROUND)
            t_widget.setToolTip(get_tooltip(trait))

            chars_w_trait = []
            for c in characters:
                if trait in c.traits:
                    chars_w_trait.append(c.name)
                    continue

            c_widget = QLabel(trait,self)
            c_widget.setAlignment(Qt.AlignCenter)
            c_widget.setText((", ").join(chars_w_trait))
            c_widget.setFrameStyle(1)
            c_widget.setFrameShape(QFrame.Box)
            c_widget.setFrameShadow(QFrame.Plain)
            c_widget.setWordWrap(True)

            self.layout_traits.addWidget(t_widget,cur_row,cur_col)
            self.layout_traits.addWidget(c_widget,cur_row+1,cur_col)

            if cur_col < max_col:
                cur_col += 1
            else:
                cur_col = 0
                cur_row += 2

    def rand_EVERYTHING(self):
        self.char_window.Randomize_Traits()
        self.update_char_layout()

        self.rand_dynamics_all()
        self.rand_throughlines_all()
        self.rand_abstracts_all()
        self.rand_acts_all()

# ========================== DYNAMICS ============================
    def opt_flip(self): #TURN THE OPPOSITE CLICKED BUTTON OFF.
        selected = self.sender().objectName()
        for options in dynamics.values():
            if selected in options:
                if options[0] == selected:
                    opposite = options[1]
                else:
                    opposite = options[0]
        self.findChild(QPushButton, opposite).setChecked(False)

    def get_dyn_buttons(self): #GET LIST OF BUTTONS IN THE DYNAMICS GRID FORMS
        c = []
        p = []
        for i in range(self.grid_c_dynamics.count()):
            if isinstance(self.grid_c_dynamics.itemAt(i).widget(), QPushButton):
                c.append(self.grid_c_dynamics.itemAt(i).widget())
            if isinstance(self.grid_p_dynamics.itemAt(i).widget(), QPushButton):
                p.append(self.grid_p_dynamics.itemAt(i).widget())
        c.extend(p)
        return c

    def read_dynamics_state(self):
        dyn_buttons = self.get_dyn_buttons()

        selections = dict.fromkeys(dynamics.keys()) 
        for key, options in dynamics.items():
            for item in dyn_buttons:
                if item.objectName() in options and item.isChecked():
                    selections[key] = item.objectName()
        return selections

    def clear_dynamics(self):
        dyn_buttons = self.get_dyn_buttons()
        for b in dyn_buttons:
            b.setChecked(False)

    def rand_dynamics_missing(self):
        selections = self.read_dynamics_state()
        dyn_buttons = self.get_dyn_buttons()

        for key, options in dynamics.items():
            if selections[key] == None:
                self.findChild(QPushButton, random.choice(options)).setChecked(True)

    def rand_dynamics_all(self):
        dyn_buttons = self.get_dyn_buttons()

        for b in dyn_buttons:
            b.setChecked(False)

        for key, options in dynamics.items():
            self.findChild(QPushButton, random.choice(options)).setChecked(True)

# ======================== THROUGHLINES ========================== 
    def gen_throughline(self, start_node):
        thro = []
        thro.append(random.choice(start_node.children))
        for i in range(1,3):
            pick = random.choice(thro[i-1].children)
            thro.append(pick)
        return thro
    
    def rand_throughlines_all(self):
        roots = []
        choices = list(root.children)

        # Initialize the throughline classes
        roots.append(random.choice(choices))
        roots.append(self.find_node(opposites[roots[0].text]))
        choices.remove(roots[0])
        choices.remove(roots[1])

        random.shuffle(choices)
        roots.extend(choices)
        
        # Reorder classes as Subjective Story needs to be last 
        roots.append(roots.pop(roots.index(roots[1])))

        # Generate 4 random throughlines with the above as seeds
        cb_throughlines = []
        for x in range(4):
            cb_throughlines.append(roots[x])
            cb_throughlines.extend(self.gen_throughline(roots[x]))

        # Overall Story problem is supposed to match the Main Character Problem
        try:
            cb_throughlines[3] = self.find_node(cb_throughlines[7].text, cb_throughlines[0].text)
        except:
            cb_throughlines[3] = cb_throughlines[7]


        for i, button in enumerate(self.grid_throughlines.parentWidget()
                                    .findChildren(QPushButton)):
            self.set_node_button(button, cb_throughlines[i].text, cb_throughlines[i].style)
        self.set_node_button(self.b_Crucial_Element,cb_throughlines[7].text, cb_throughlines[7].style)
        
    def find_node(self, string, branch=None, level=None):
        found = []
        if string == BLANK_TEXT: return

        for cl in root.children:
            if branch:
                if cl.text != branch:
                    continue
            if cl.text == string: 
                found.append(cl)
            for ty in cl.children:
                if ty.text == string: 
                    found.append(ty)
                for var in ty.children:
                    if var.text == string: 
                        found.append(var)
                    for elem in var.children:
                        if elem.text == string: 
                            found.append(elem)

        # error checking for multiple results. 
        if level and found:
            for node in found:
                if node.level == level:
                    found = [node]

        return found[0]

    def read_throughlines_state(self):
        content = []

        for i, button in enumerate(self.grid_throughlines.parentWidget()
                                    .findChildren(QPushButton)):
            content.append(button.text())

        return content

# ========================= ABSTRACTS ============================
    def rand_abstracts_all(self):
        choices = list(types)
        random.shuffle(choices)
        for i, button in enumerate(self.grid_abstracts.parentWidget()
                                    .findChildren(QPushButton)):
            self.set_node_button(button, choices[i].text, choices[i].style)

    def read_abstracts_state(self):
        content = []

        for i, button in enumerate(self.grid_abstracts.parentWidget()
                                    .findChildren(QPushButton)):
            content.append(button.text())

        return content

# =========================== ACTS ===============================
    def update_acts(self):
        thro = self.read_throughlines_state()
        branches = thro[0::4]

    def rand_acts_all(self):
        try:
            thro = self.read_throughlines_state()
            branch_names = thro[0::4]

            branch_nodes = []
            for name in branch_names:
                branch_nodes.append(self.find_node(name))

            acts = []
            for b in branch_nodes:
                choices = []
                for child in b.children:
                    choices.append(child)
                random.shuffle(choices)
                acts.extend(choices)

            for i, button in enumerate(self.grid_acts.parentWidget()
                                    .findChildren(QPushButton)):
                self.set_node_button(button, acts[i].text, acts[i].style)

        except:
            return

    def read_acts_state(self):
        content = []

        for i, button in enumerate(self.grid_acts.parentWidget()
                                    .findChildren(QPushButton)):
            content.append(button.text())

        return content
# =========================== SAVE ===============================
    def read_total_state(self):
        _data = {}
        _data['characters'] = []
        _data['character_names'] = []
        _data['character_traits'] = []
        _data['dynamics'] = []
        _data['throughlines'] = []
        _data['abstracts'] = []
        _data['acts'] = []        

        try:
            for c in characters:
                _data['characters'].append(jsonpickle.encode(c))
                _data['character_names'].append(c.name)
                _data['character_traits'].append(c.traits)

            for k, dyn in self.read_dynamics_state().items():
                _data['dynamics'].append(dyn)

            _data['throughlines'] = self.read_throughlines_state()

            _data['abstracts'] = self.read_abstracts_state()

            _data['acts'] = self.read_acts_state()

            return _data

        except:
            pass

    def saveCall(self):
        global FILE_PATH
        save_data = self.read_total_state()   

        if FILE_PATH == "":
            save_path = QFileDialog.getSaveFileName(self, 'Save File', "","JSON (*.json)")
        else:
            save_path = QFileDialog.getSaveFileName(self, 'Save File', FILE_PATH,"JSON (*.json)")
        
        if save_path[0]:
            with open(save_path[0], 'w') as outfile:
                json.dump(save_data,outfile)

            FILE_PATH = save_path[0]
            self.setWindowTitle("Story Randomizer - " + FILE_PATH)
        else:
            return

    def reset_button_layout(self,layout):
        try:
            for i, button in enumerate(layout.parentWidget()
                                        .findChildren(QPushButton)):
                    self.set_node_button(button,BLANK_TEXT, "")   
        except:
            return


    def newCall(self):
        global characters

        characters = []
        self.update_char_layout()

        for button in self.layout_dynamics.parentWidget().findChildren(QPushButton):
            button.setChecked(False)

        layouts = [self.grid_throughlines, self.grid_abstracts, self.grid_acts]

        for layout in layouts:
            self.reset_button_layout(layout)
            
        self.set_node_button(self.b_Crucial_Element, BLANK_TEXT, "")

    def openCall(self):
        global characters
        global FILE_PATH
        open_path = QFileDialog.getOpenFileName(self, 'Open File', '',"JSON (*.json)")
        
        if open_path[0]:
            with open(open_path[0]) as json_file:
                in_data = json.load(json_file)
        else:
            return 
        
        FILE_PATH = open_path[0]
        self.setWindowTitle("Story Randomizer - " + FILE_PATH)

        characters = []
        for c in in_data['characters']:
            characters.append(jsonpickle.decode(c))

        self.update_char_layout()

        for button in self.layout_dynamics.parentWidget().findChildren(QPushButton):
            button.setChecked(False)
            if button.text() in in_data['dynamics']: button.setChecked(True)

        for i, button in enumerate(self.grid_throughlines.parentWidget()
                                    .findChildren(QPushButton)):
            try:
                if i % 4 == 0:
                    branch = self.find_node(in_data['throughlines'][i])
                node = self.find_node(in_data['throughlines'][i],branch.text)
                self.set_node_button(button, node.text, node.style)
                if i == 7:
                    self.set_node_button(self.b_Crucial_Element, node.text, node.style)
            except:
                print("Error loading throughlines, save may be corrupted")

        for i, button in enumerate(self.grid_abstracts.parentWidget()
                                    .findChildren(QPushButton)):
            try:
                node = self.find_node(in_data['abstracts'][i])
                self.set_node_button(button, node.text, node.style)
            except:
                print("Error loading abstracts, save may be corrupted")

        for i, button in enumerate(self.grid_acts.parentWidget()
                                    .findChildren(QPushButton)):
            try:
                node = self.find_node(in_data['acts'][i])
                self.set_node_button(button, node.text, node.style)
            except:
                print("Error loading acts, save may be corrupted")

    def exportCall(self):
        try:
            out_data = self.read_total_state()

            save_path = QFileDialog.getSaveFileName(self, 'Save File', "","PDF (*.pdf)")

            if not save_path[0]:
                return

            with open('dump.json', 'w') as outfile:
                json.dump(out_data,outfile)

            pdf_report.save('dump.json', save_path)
        except:
            self.error_message('Export to pdf failed.')

    def error_message(self, text):
        self.emsg.setWindowTitle('Error')
        self.emsg.showMessage(text)

# Startup
app = QApplication(sys.argv)
app.setWindowIcon(QIcon('./ui/icon.png'))
# app.setStyleSheet(qdarkstyle.load_stylesheet())
mainwindow = MainWindow()
mainwindow.show()

try:
    sys.exit(app.exec_())
except:
    print('Exiting.')