class Node:
        
    data = None
    next = None
    prev = None
        
    def __init__(self, nodeData, nextNode, prevNode):
        self.data = nodeData
        self.next = nextNode
        self.prev = prevNode