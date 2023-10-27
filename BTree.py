from math import ceil

class BTValue:
    pass

class BTNode:
    pass

class BTValue:
    value = None
    prev, next, left_child, right_child = None, None, None, None

    def __init__(self, value) -> None:
        self.value = value

    def set_next(self, btv: BTValue) -> None:
        self.next = btv
        if btv is not None:
            btv.prev = self

    def set_left_child(self, lc: BTNode, parent_node: BTValue = None) -> None:
        self.left_child = lc
        if self.left_child is not None:
            if parent_node is not None:
                self.left_child.parent_node = parent_node
            self.left_child.parent_value = self

    def set_right_child(self, rc: BTNode, parent_node: BTValue = None) -> None:
        self.right_child = rc
        if self.right_child is not None:
            if parent_node is not None:
                self.right_child.parent_node = parent_node
            self.right_child.parent_value = self

    def clear_left_child(self) -> None:
        self.left_child = None

    def clear_right_child(self) -> None:
        self.right_child = None

class BTNode:
    start, last, parent_node, parent_value, orphan = None, None, None, None, None
    size, degree = 0, 5

    def __init__(
        self, value=None, start: BTValue = None, degree: int = 5, initial_size: int = 1
    ) -> None:
        if value is not None:
            self.start = BTValue(value)
        if start is not None:
            self.start = start
        self.last = self.start
        self.size = initial_size
        self.degree = degree

    def search(self, value) -> (BTNode, BTValue):
        if self.start is None:
            return (self, None)
        v = self.start
        while v.value < value and v.next is not None:
            v = v.next
        if v.value == value:
            return (self, v)
        elif v.next is None and v.value < value:
            if v.right_child is not None:
                return v.right_child.search(value)
            else:
                return (self, None)
        else:
            if v.left_child is not None:
                return v.left_child.search(value)
            else:
                return (self, None)

    def insert(self, value) -> BTValue:
        v = self.start
        while v is not None and v.value <= value:
            v = v.next
        new_value = BTValue(value)
        if v is not None:
            previous_value = v.prev
            new_value.set_next(v)
            if previous_value is not None:
                previous_value.set_next(new_value)
            else:
                self.start = new_value
        else:
            if self.last is not None:
                self.last.set_next(new_value)
            else:
                self.start = new_value
        if new_value.next is None:
            self.last = new_value
        self.size = self.size + 1
        return new_value

    def _adjust_parent(self) -> None:
        v = self.start
        while v is not None:
            if v.left_child is not None:
                v.left_child.parent_node = self
            if v.right_child is not None:
                v.right_child.parent_node = self
            v = v.next

    def split(self) -> BTNode:
        if self.size >= self.degree:
            s = ceil(self.degree / 2) - 1
            new_left = BTNode(start=self.start, degree=self.degree, initial_size=s)
            new_left.parent_node = self.parent_node
            v = self.start
            for i in range(s - 1):
                v = v.next
            new_middle = v.next
            v.next = None
            v.set_right_child(new_middle.left_child)
            new_left.last = v
            new_left._adjust_parent()
            new_right = self
            new_right.start, new_right.size = new_middle.next, new_right.size - 1 - s
            new_middle.next, new_right.start.prev = None, None
            if new_right.parent_node is not None:
                new_value = new_right.parent_node.insert(new_middle.value)
                new_value.set_left_child(new_left)
                if new_value.next is None:
                    new_value.set_right_child(new_value.prev.right_child)
                    new_value.prev.set_right_child(None)
                if new_right.parent_node is not None:
                    return new_right.parent_node.split()
            else:
                new_root = BTNode(value=new_middle.value, degree=self.degree, initial_size=1)
                new_left.parent_node, new_right.parent_node = new_root, new_root
                new_root.start.set_left_child(new_left)
                new_root.start.set_right_child(new_right)
                return new_root
        return None

    def _max_value(self) -> (BTNode, BTValue):
        if self.last is None:
            return (self, None)
        if self.last.right_child is not None:
            return self.last.right_child.max_value()
        else:
            return (self, self.last)

    def _min_value(self) -> (BTNode, BTValue):
        if self.start is None:
            return (self, None)
        if self.start.left_child is not None:
            return self.start.left_child.min_value()
        else:
            return (self, self.start)

    def _siblings(self) -> (BTNode, BTNode):
        previous_sibling, next_sibling, parent_value = None, None, self.parent_value
        if parent_value is not None:
            if parent_value.left_child == self:
                if parent_value.prev is not None:
                    previous_sibling = parent_value.prev.left_child
                if parent_value.right_child is not None:
                    next_sibling = parent_value.right_child
                elif parent_value.next is not None:
                    next_sibling = parent_value.next.left_child
            elif parent_value.right_child == self:
                previous_sibling = parent_value.left_child
        return (previous_sibling, next_sibling)

    def _remove_value(self, v: BTValue) -> (BTValue, BTValue, BTValue):
        previous_value, next_value = v.prev, v.next
        if previous_value is None:
            if next_value is not None:
                self.start = next_value
                next_value.prev = None
            else:
                self.start, self.last = None, None
        else:
            if next_value is not None:
                previous_value.next = next_value
                next_value.prev = previous_value
            else:
                previous_value.next = None
                self.last = previous_value
        self.size = self.size - 1
        return (previous_value, v, next_value)

    def _shift_left(self, new_left: BTNode, v: BTValue, new_right: BTNode) -> None:
        if v.value is None:
            return
        new_left.insert(v.value)
        if new_left.last.prev is not None:
            new_left.last.set_left_child(new_left.last.prev.right_child, new_left)
            new_left.last.prev.clear_right_child()
        elif new_left.orphan is not None:
            new_left.last.set_left_child(new_left.orphan, new_left)
            new_left.orphan = None
        if new_right.size > 0:
            new_left.last.set_right_child(new_right.start.left_child, new_left)
            if new_right.size == 1:
                new_right.orphan = new_right.start.right_child
            v.value = new_right.start.value
            new_right._remove_value(new_right.start)
        else:
            new_left.last.set_right_child(new_right.orphan, new_left)
            v.value = None
            new_right.orphan = None

    def _shift_right(self, new_left: BTNode, v: BTValue, new_right: BTNode) -> None:
        new_right.insert(v.value)
        if new_right.orphan is not None:
            new_right.start.set_right_child(new_right.orphan, new_right)
            new_right.orphan = None
        if new_left.last is not None:
            new_right.start.set_left_child(new_left.last.right_child, new_right)
            v.value = new_left.last.value
            if new_left.last.prev is not None:
                new_left.last.prev.set_right_child(new_left.last.left_child)
            new_left._remove_value(new_left.last)
        else:
            new_right.start.set_left_child(new_left.orphan, new_right)
            new_left.orphan = None
            v.value = None

    def _redistribute(self, new_left: BTNode, v: BTValue, new_right: BTNode) -> None:
        while self.size < ceil(self.degree / 2) - 1:
            if new_left is self:
                self._shift_left(new_left, v, new_right)
            else:
                self._shift_right(new_left, v, new_right)

    def _merge(self, new_left: BTNode, v: BTValue, new_right: BTNode) -> None:
        while self.size > 0 or v.value is not None:
            if new_left is self:
                self._shift_right(new_left, v, new_right)
            else:
                self._shift_left(new_left, v, new_right)
        new_node = new_left
        if new_left is self:
            new_node = new_right
        if self.parent_value.size == 1:
            if self.parent_value.parent_node is None:
                new_node.parent_node, new_node.parent_value = None, None
                return new_node
            else:
                self.parent_value.orphan = new_node
                self.parent_value._remove_value(v)
        elif v.next is None:
            v.prev.set_right_child(new_node, self.parent_node)
            self.parent_value._remove_value(v)
        else:
            v.next.set_left_child(new_node, self.parent_node)
            self.parent_value._remove_value(v)
        return None

    def removal_consolidate(self) -> BTNode:
        new_root = None
        if self.size < ceil(self.degree / 2) - 1:
            (previous_sibling, next_sibling) = self._siblings()
            parent_node = self.parent_node
            if previous_sibling is not None:
                if previous_sibling.size > ceil(self.degree / 2) - 1:
                    self._redistribute(previous_sibling, previous_sibling.parent_value, self)
                else:
                    new_root = self._merge(previous_sibling, previous_sibling.parent_value, self)
            elif next_sibling is not None:
                if next_sibling.size > ceil(self.degree / 2) - 1:
                    self._redistribute(self, self.parent_value, next_sibling)
                else:
                    new_root = self._merge(self, self.parent_value, next_sibling)
            if new_root is None and parent_node is not None:
                new_root = parent_node.removal_consolidate()
        return new_root

    def remove(self, v: BTValue) -> BTNode:
        if v.left_child is not None:
            (node, parent_value) = v.left_child._max_value()
            v.value = parent_value.value
            node._remove_value(parent_value)
            return node
        else:
            self._remove_value(v)
            return self

class BTree:
    root: BTNode
    degree: int
    root, degree = None, 5

    def __init__(self, value, degree=5):
        self.root = BTNode(value, degree=degree)
        self.degree = degree

    def search(self, value) -> BTValue:
        (node, v) = self.root.search(value)
        return v

    def _insert(self, val) -> None:
        (node, v) = self.root.search(val)
        node.insert(val)
        new_root = node.split()
        if new_root is not None:
            self.root = new_root

    def insert(self, value) -> None:
        if type(value) is list:
            for v in value:
                self._insert(v)
        else:
            self._insert(value)

    def _remove(self, val) -> None:
        (node, v) = self.root.search(val)
        if v is not None:
            node = node.remove(v)
            new_root = node.removal_consolidate()
            if new_root is not None:
                self.root = new_root

    def remove(self, value) -> None:
        if type(value) is list:
            for v in value:
                self._remove(v)
        else:
            self._remove(value)
