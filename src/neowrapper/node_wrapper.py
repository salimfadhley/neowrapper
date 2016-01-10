import pprint
import logging

from functools import partial
from py2neo import Node, Relationship


log = logging.getLogger(__name__)


__author__ = 'sal'


class RelationshipMeta(object):
    def __init__(self, direction, relationship, implementation, multiple):
        self.direction = direction
        self.relationship = relationship
        self.implementation = implementation
        self.multiple = multiple

NODE_IMPLEMENTATIONS = {}

def filter_json_data(data):
    assert isinstance(data, dict), "Invalid data: %r" % data
    return {k: v for (k, v) in data.items() if not isinstance(v, dict)}

class MissingProperty(RuntimeError):
    """An expected property was missing.
    """

class NoRelationshipExists(ValueError):
    """Raised when an expected relationship cannot be found
    """

class InvalidNode(ValueError):
    """Raised when a object cannot be wrapped as a node
    """

class NodeMeta(type):

    @staticmethod
    def get_getter_name(name):
        return "get_%s" % name

    @staticmethod
    def get_adder_name(name):
        return "add_%s" % name

    def create_getter_method(cls, cfg, name):
        function_name = cls.get_getter_name(name)
        log.info("Creating getter function %s.%s" % (cls, function_name))
        if cfg.multiple:
            setattr(cls, function_name, lambda slf: partial(slf.get_nodes_by_relationship, cfg)())
        else:
            setattr(cls, function_name, lambda slf: partial(slf.get_single_node_by_relationship, cfg)())

    def create_adder_method(cls, cfg, name):
        function_name = cls.get_adder_name(name)
        log.info("Creating adder function %s.%s" % (cls, function_name))
        if cfg.multiple:
            # Add multiple objects, get back a list
            setattr(cls, function_name, lambda slf, items, unique=False: partial(slf.add_nodes, cfg)(items, unique))
        else:
            # Add a single related object, return a single wrapped node
            setattr(cls, function_name, lambda slf, item, unique=False: partial(slf.add_nodes, cfg)([item,], unique)[0])

    def __init__(cls, name, bases, nmspc):

        super(NodeMeta, cls).__init__(name, bases, nmspc)

        # Register this implementation
        NODE_IMPLEMENTATIONS[name] = cls
        for name, cfg in cls.RELATIONSHIPS.items():
            cls.create_getter_method(cfg, name)
            cls.create_adder_method(cfg, name)

class NodeWrapper(object, metaclass=NodeMeta):
    RELATIONSHIPS = {}
    UNIQUE_KEY = None

    @staticmethod
    def get_node_implementation(name):
        return NODE_IMPLEMENTATIONS[name]

    def __init__(self, n):
        if not n:
            raise InvalidNode(n)
        self.n = n

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.n == other.n

    def __repr__(self):
        return """<%s %s>""" % (self.__class__.__name__, str(self))

    def __str__(self):
        return repr(self.n)

    @property
    def g(self):
        return self.n.graph

    @classmethod
    def exists(cls, g, properties):
        try:
            cls.find_one(g, properties)
            return True
        except ValueError:
            return False

    @classmethod
    def sample(cls, g, n=1):
        return [None, None]

    @classmethod
    def new(cls, g, properties, unique=True):
        _properties = {}
        _properties.update(properties)
        if unique:
            try:
                unique_value = _properties.pop(cls.UNIQUE_KEY)
            except KeyError:
                raise MissingProperty("Key %s is missing from %s" % (cls.UNIQUE_KEY, pprint.pformat(properties)))
            n = g.merge_one(cls.__name__, cls.UNIQUE_KEY, unique_value)
            filtered_properties = filter_json_data(_properties)
            for k, v in filtered_properties.items():
                n[k] = v
            if filtered_properties:
                n.push()
        else:
            n = Node(cls.__name__, **filter_json_data(_properties))
            g.create(n)

        return cls(n)

    @classmethod
    def find_one(cls, g, parameters):
        args = []

        for criteria in parameters.items():
            args.extend(criteria)

        try:
            n = g.find_one(cls.__name__, *args)
        except StopIteration:
            raise ValueError("No such %s: %r" % (cls.__name__, parameters))
        return cls(n)

    @classmethod
    def find(cls, g, parameters):
        args = []

        for criteria in parameters.items():
            args.extend(criteria)

        for n in g.find(cls.__name__, *args):
            yield cls(n)

    def push(self):
        self.n.push()
        return self

    def get_nodes_by_relationship(self, cfg):
        """
        Get a generator of nodes that match a particular relationship
        """
        if cfg.direction == "In":
            gen = self.n.match_incoming
            node_accessor = lambda r: r.start_node
        elif cfg.direction == "Out":
            gen = self.n.match_outgoing
            node_accessor = lambda r: r.end_node
        else:
            raise ValueError("Unknown direction in %s" % cfg)
        node_implementation_class = self.get_node_implementation(cfg.implementation)
        for rel in gen(cfg.relationship):
            node = node_accessor(rel)
            yield node_implementation_class(node)

    def get_single_node_by_relationship(self, cfg):
        try:
            return next(self.get_nodes_by_relationship(cfg))
        except StopIteration:
            raise NoRelationshipExists("No %s node with relationship %s connects to %r" % (cfg.direction, cfg.relationship, self))

    def add_nodes(self, cfg, items, unique=False):
        return list(self._add_nodes(cfg, items, unique))

    def _add_nodes(self, cfg, items, unique=True):
        node_implementation_class = self.get_node_implementation(cfg.implementation)
        for item in items:
            n = Node(cfg.implementation, **filter_json_data(item))
            if cfg.direction == "Out":
                r = Relationship(self.n, cfg.relationship, n)
            elif cfg.direction == "In":
                r = Relationship(n, cfg.relationship, self.n)
            if unique:
                self.n.graph.create_unique(r)
            else:
                self.n.graph.create(r)
            yield node_implementation_class(n)

    def __getitem__(self, item):
        return self.n.properties[item]
