# Copyright: 2006 Brian Harring <ferringb@gmail.com>
# License: GPL2

from pkgcore.sync import base

class git_syncer(base.dvcs_syncer):

    @staticmethod
    def parse_uri(raw_uri):
        if not raw_uri.startswith("git+") and not raw_uri.startswith("git://"):
            raise base.uri_exception(raw_uri,
                "doesn't start with git+ nor git://")
        if raw_uri.startswith("git+"):
            return raw_uri[4:]
        return raw_uri
    
    def __init__(self, basedir, uri):
        uri = self.parse_uri(uri)
        base.dvcs_syncer(self, basedir, uri)
    
    def _initial_pull(self):
        return ["git", "clone", self.uri, self.basedir]

    def _update_existing(self):
        return ["git", "pull"]