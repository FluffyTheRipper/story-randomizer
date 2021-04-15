import json
from collections import namedtuple
from json import JSONEncoder
import jsonpickle


class Node():
    def __init__(self, indented_line):
        self.children = []
        self.parent = None
        self.level = len(indented_line) - len(indented_line.lstrip())
        self.text = indented_line.strip()


    def add_children(self, nodes):
        childlevel = nodes[0].level
        while nodes:
            node = nodes.pop(0)
            if node.level == childlevel: # add node as a child
                self.children.append(node)
            elif node.level > childlevel: # add nodes as grandchildren of the last child
                nodes.insert(0,node)
                self.children[-1].add_children(nodes)
            elif node.level <= self.level: # this node is a sibling, no more children
                nodes.insert(0,node)
                return

    def list_children(self):
    	content = []
    	for child in self.children:
    		content.append(child.text)
    	return content


class Character:
    def __init__(self, name):
        self.name = name
        self.traits = []

    def add_trait(self, trait):
        self.traits.append(trait)