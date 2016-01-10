import functools
from ladygeek.cfg import get_config
from py2neo import Graph
import logging

log = logging.getLogger(__name__)

def get_graph_url(instance):
    cfg = get_config()
    end_point = "%s" % cfg['neo4j_server'][instance]
    log.info("Graph URL is: %s" % end_point)
    return end_point

@functools.lru_cache(maxsize=2)
def get_graph(instance="dev"):
    end_point = get_graph_url(instance)
    log.info("Connection to %s" % end_point)
    return Graph(end_point)