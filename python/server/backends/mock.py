from collections import defaultdict
import random

from loremipsum import get_sentences

from lucidfind.backends import Backend, Document
from lucidfind.fusion import compare_datasources

class MockBackend(Backend):
    def __init__(self):
        self.datasources = {}

    def get_document(self, doc_id):
        return _gen_fake_docs(1).next()

    def get_datasource(self, id):
        return self.datasources.get(id, None)

    def update_datasource(self, id, **config):
        datasource = self.get_datasource(id)

        if datasource is None:
            self.datasources[id] = config
        else:
            # Update it (maybe)
            if compare_datasources(config, datasource) == False:
                print "Detected an update in config, updating Fusion"
                self.datasources[id] = config
                return config
            else:
                print "No change in datasource, doing nothing"
                return

def _gen_fake_docs(count, author=None, source=None, project=None):
    authors = ["Joe", "Jane", "Bill", "Mary"]
    sources = ["web", "twitter", "email"]
    projects = ["solr", "lucene", "elasticsearch"]
    
    
    def _random_choice(value, choices):
        if value is not None:
            return value
        else:
            return random.choice(choices)

    for i in range(count):
        yield Document(id="doc-%d" % i, author=_random_choice(author, authors), source=_random_choice(source, sources), 
                       project=_random_choice(project, projects), content="".join(get_sentences(random.randint(1, 4))), link="http://example.com/%d" % i,
                       created_at="2015-01-01T%02d:%02d:00Z" % (random.randint(0,23), random.randint(0,59)))

def _gen_fake_facets(docs, author=None, source=None, project=None):
    facets = defaultdict(lambda: defaultdict(int))
    for doc in docs:
        facets["author"][doc.author] += 1
        facets["source"][doc.source] += 1
        facets["project"][doc.project] += 1
    return facets