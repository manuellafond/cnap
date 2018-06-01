import random




class Node:

	
	def __init__(self):
		self.label = ""
		self.parent = None
		self.params = {}
		self.children = []
		
	def add_child(self, child):
		self.children.append(child)
		child.parent = self
		
	def create_child(self):
		n = Node()
		self.children.append(n)
		n.parent = self
		return n
		
	def is_leaf(self):
		if self.get_nb_children() == 0:
			return True
		return False
		
	def is_root(self):
		if self.parent == None:
			return True
		return False
		
	def get_nb_children(self):
		return len(self.children)

	def remove_child(self, i):
		c = self.children.pop(i)
		c.parent = None
		
		
	#TODO: makes two passes through the nodes, could be faster
	def get_leaves(self):
		leaves = []
		for n in self.get_preorder_nodes():
			if n.is_leaf():
				leaves.append(n)
		return leaves
		
	def to_newick(self, split_label = '', split_label_index = 0, write_internal_labels = True):
		label = self.label or ''
		
		if not write_internal_labels and not self.is_leaf():
			label = ""
		elif split_label != '':
			pz = label.split(split_label)
			if split_label_index < len(pz):
				label = pz[split_label_index]
			else:
				label = ""
		
		children_newick = ','.join([n.to_newick(split_label, split_label_index, write_internal_labels) for n in self.children])
		if children_newick:
			children_newick = '(' + children_newick + ')'
		return children_newick + label

	def get_preorder_nodes(self):
		arr = []
		return self._rec_preorder_nodes(arr)
		
	def _rec_preorder_nodes(self,curarray):
		curarray.append(self)
		
		for c in self.children:
			c._rec_preorder_nodes(curarray)
			
		return curarray
		

	@staticmethod	
	def get_random_binary_tree(nb_leaves, label_prefix = "L"):
		n = Node()
		for i in range(nb_leaves):
			n.create_child()
			n.children[i].label = label_prefix + str(i + 1)
			
		while n.get_nb_children() > 2:
			r1 = random.randint(0,n.get_nb_children() - 1)
			r2 = random.randint(0,n.get_nb_children() - 2)
			
			if r2 >= r1:
				r2 = r2 + 1
			else:	#swap
				rt = r1
				r1 = r2
				r2 = rt

			#assertion: r2 > r1
			n2 = n.children.pop(r2)
			n1 = n.children.pop(r1)
			
			
			newnode = Node()
			newnode.add_child(n1)
			newnode.add_child(n2)
			
			n.add_child(newnode)
			
		return n
			
			
			
			
			