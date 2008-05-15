# Copyright: 2006 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD

"""
base class to derive from for domain objects

Bit empty at the moment
"""
from snakeoil.demandload import demandload
demandload(globals(), "pkgcore.repository:multiplex")

# yes this is basically empty. will fill it out as the base is better
# identified.

class domain(object):

    def __getattr__(self, attr):
        if attr == "all_repos":
            if len(self.repos) == 1:
                a = self.all_repos = self.repos[0]
            else:
                a = self.all_repos = multiplex.tree(*self.repos)
        elif attr == "all_livefs_repos":
            if len(self.vdb) == 1:
                a = self.all_livefs_repos = self.vdb[0]
            else:
                a = self.all_livefs_repos = multiplex.tree(*self.vdb)
        else:
            raise AttributeError(attr)
        return a
