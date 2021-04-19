import sys
import random
import qdarkstyle
import json
import jsonpickle
import pdf_report
import os
import copy
from classes import *
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QErrorMessage, QPushButton,QComboBox, QHBoxLayout,QVBoxLayout, QFileDialog, QButtonGroup, QRadioButton, QFrame

# ========================== DEFINITIONS ============================
FILE_PATH = ""
BLANK_TEXT = "--"

HEADING_FONT = QFont()
HEADING_FONT.setBold(True)

COLOR_HEADING_BACKGROUND = "background-color: grey"

def_char_names = ["Eins","Zwei","Drei","Vier","Funf","Sechs","Sieben","Acht","Neun","Zehn"]

CHARACTER_TRAITS = ['Conscience',
                    'Consider',
                    'Controlled',
                    'Disbelief',
                    'Faith',
                    'Feeling',
                    'Help',
                    'Hinder',
                    'Logic',
                    'Oppose',
                    'Persue',
                    'Prevent',
                    'Reconsider',
                    'Support',
                    'Temptation',
                    'Uncontrolled']

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

characters = []
characters_bak = []

with open('./data/character_traits.txt') as f:
        traits = f.read().splitlines()

class CharWindow(QWidget):
    # global characters
    # global old_characters
    
    def __init__(self):
        super().__init__()
        loadUi("./ui/char_window.ui",self)
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
            for c in characters:
                c.traits = []
            for trait in traits:
                c = random.choice(characters)
                c.add_trait(trait)
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
        self.b_Cancel.setEnabled(not state)

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
                        self.listWidget_Chars.item(i).setForeground(Qt.cyan)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("./ui/main_window.ui",self)
        

        self.emsg = QErrorMessage()
        self.emsg.setWindowModality(QtCore.Qt.WindowModal)
        self.emsg.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        self.initUI()
        self.char_window = CharWindow()
        self.b_Edit_Characters.clicked.connect(self.edit_chars)
        self.b_clear_dyn.clicked.connect(self.clear_dynamics)
        self.b_rand_dyn_miss.clicked.connect(self.rand_dynamics_missing)
        self.b_rand_dyn_all.clicked.connect(self.rand_dynamics_all)   

        self.b_rand_thr_all.clicked.connect(self.rand_throughlines_all) 
        self.b_rand_abs_all.clicked.connect(self.rand_abstracts_all)
        self.b_rand_acts_all.clicked.connect(self.rand_acts_all)

        self.b_rand_EVERYTHING.clicked.connect(self.rand_EVERYTHING)

    def initUI(self):

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

        # Initialize the Dropdowns to default values
        ordered_classes = []
        for cl in classes: ordered_classes.append(cl.text)
        ordered_classes = list(set(ordered_classes))
        ordered_classes.sort()

        ordered_types = []
        for cl in types: ordered_types.append(cl.text)
        ordered_types = list(set(ordered_types))
        ordered_types.sort()

        ordered_variants = []
        for cl in variants: ordered_variants.append(cl.text)
        ordered_variants = list(set(ordered_variants))
        ordered_variants.sort()

        ordered_elements = []
        for cl in elements: ordered_elements.append(cl.text)
        ordered_elements = list(set(ordered_elements))
        ordered_elements.sort()

        self.cb_Crucial_Element.addItem(BLANK_TEXT)

        for combo in self.layout_throughlines.parentWidget().findChildren(QComboBox):
            combo.addItem(BLANK_TEXT)

            if "Class" in combo.objectName():
                for cl in ordered_classes: 
                    if combo.findText(cl) == -1:
                        combo.addItem(cl)
            if "Concern" in combo.objectName():
                for ty in ordered_types: 
                    if combo.findText(ty) == -1:
                        combo.addItem(ty)
            if "Issue" in combo.objectName():
                for var in ordered_variants: 
                    if combo.findText(var) == -1:
                        combo.addItem(var)
            if "Problem" in combo.objectName():
                for elem in ordered_elements: 
                    if combo.findText(elem) == -1:
                        combo.addItem(elem)
                    self.cb_Crucial_Element.addItem(elem)

      
        for combo in self.layout_abstracts.parentWidget().findChildren(QComboBox):
            combo.addItem(BLANK_TEXT)
            for ty in types:
                combo.addItem(ty.text)


        for combo in self.layout_acts.parentWidget().findChildren(QComboBox):
            combo.addItem(BLANK_TEXT)
            for ty in types:
                combo.addItem(ty.text)


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

        for trait in CHARACTER_TRAITS:
            t_widget = QLabel(trait,self)
            t_widget.setFont(HEADING_FONT)
            t_widget.setAlignment(Qt.AlignCenter)
            t_widget.setText(trait)
            t_widget.setFrameStyle(1)
            t_widget.setFrameShape(QFrame.Box)
            t_widget.setFrameShadow(QFrame.Plain)
            t_widget.setStyleSheet(COLOR_HEADING_BACKGROUND)

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
        cb_throughlines[3] = cb_throughlines[7] 

        for i, combo in enumerate(self.layout_throughlines.parentWidget()
                .findChildren(QComboBox)):
            combo.setCurrentIndex(combo.findText(cb_throughlines[i].text))

        self.cb_Crucial_Element.setCurrentIndex(combo.findText(cb_throughlines[7].text))
        
    def find_node(self, string):
        for cl in root.children:
            if cl.text == string: return cl
            for ty in cl.children:
                if ty.text == string: return ty
                for var in ty.children:
                    if var.text == string: return var
                    for elem in var.children:
                        if elem.text == string: return elem
        return   

    def read_throughlines_state(self):
        content = []
        for i, combo in enumerate(self.layout_throughlines.parentWidget()
                .findChildren(QComboBox)):
            content.append(combo.currentText())

        return content

# ========================= ABSTRACTS ============================
    def rand_abstracts_all(self):
        choices = list(types)
        random.shuffle(choices)
        for i, combo in enumerate(self.layout_abstracts.parentWidget().findChildren(QComboBox)):
            combo.setCurrentIndex(combo.findText(choices[i].text))

    def read_abstracts_state(self):
        content = []
        for i, combo in enumerate(self.layout_abstracts.parentWidget().findChildren(QComboBox)):
            content.append(combo.currentText())

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
                    choices.append(child.text)
                random.shuffle(choices)
                acts.extend(choices)

            for i, combo in enumerate(self.layout_acts.parentWidget()
                    .findChildren(QComboBox)):
                combo.setCurrentIndex(combo.findText(acts[i]))
        except:
            return

    def read_acts_state(self):
        content = []
        for i, combo in enumerate(self.layout_acts.parentWidget()
                .findChildren(QComboBox)):
            content.append(combo.currentText())

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
            # for thro in self.read_throughlines_state():
            #     _data['throughlines'].append(thro)
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


    def newCall(self):
        global characters

        characters = []
        self.update_char_layout()

        for button in self.layout_dynamics.parentWidget().findChildren(QPushButton):
            button.setChecked(False)

        for i, combo in enumerate(self.layout_throughlines.parentWidget()
                                                .findChildren(QComboBox)):
            combo.setCurrentIndex(combo.findText(BLANK_TEXT))

        for i, combo in enumerate(self.layout_abstracts.parentWidget()
                                                .findChildren(QComboBox)):
            combo.setCurrentIndex(combo.findText(BLANK_TEXT))

        for i, combo in enumerate(self.layout_acts.parentWidget()
                                                .findChildren(QComboBox)):
            combo.setCurrentIndex(combo.findText(BLANK_TEXT))

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

        for i, combo in enumerate(self.layout_throughlines.parentWidget()
                                                .findChildren(QComboBox)):
            try:
                combo.setCurrentIndex(combo.findText(in_data['throughlines'][i]))
                if combo.objectName() == 'cb_Problem_1':
                    self.cb_Crucial_Element.setCurrentIndex(combo.findText(in_data['throughlines'][i]))
            except:
                print("Error loading throuhglines, save may be corrupted")

        for i, combo in enumerate(self.layout_abstracts.parentWidget()
                                            .findChildren(QComboBox)):
            try:
                combo.setCurrentIndex(combo.findText(in_data['abstracts'][i]))
            except:
                print("Error loading abstracts, save may be corrupted")

        for i, combo in enumerate(self.layout_acts.parentWidget()
                                                .findChildren(QComboBox)):
            try:
                combo.setCurrentIndex(combo.findText(in_data['acts'][i]))
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
# app.setStyleSheet(qdarkstyle.load_stylesheet())
mainwindow = MainWindow()
mainwindow.show()

try:
    sys.exit(app.exec_())
except:
    print('Exiting.')