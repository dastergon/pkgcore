# Copyright: 2006-2009 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD

import os, errno

from pkgcore.interfaces import repo as repo_interfaces
from pkgcore.fs import tar
from pkgcore.binpkg import xpak
from pkgcore.ebuild.conditionals import stringify_boolean

from snakeoil import osutils
from pkgcore.util.bzip2 import compress
from snakeoil.osutils import join as pjoin
from snakeoil.demandload import demandload
demandload(globals(), "pkgcore.log:logger")

def discern_loc(base, pkg, extension='.tbz2'):
    return pjoin(base, pkg.category,
        "%s-%s%s" % (pkg.package, pkg.fullver, extension))


_metadata_rewrites = {
    "depends":"DEPEND", "rdepends":"RDEPEND", "post_rdepends":"PDEPEND",
    "use":"USE", "eapi":"EAPI", "CONTENTS":"contents", "provides":"PROVIDE"}

def generate_attr_dict(pkg, portage_compatible=True):
    d = {}
    for k in pkg.tracked_attributes:
        if k == "contents":
            continue
        v = getattr(pkg, k)
        if k == 'environment':
            d['environment.bz2'] = compress(v.get_fileobj().read())
            continue
        if k == 'provides':
            versionless_provides = lambda b: b.key
            s = stringify_boolean(v, func=versionless_provides)
        elif not isinstance(v, basestring):
            try:
                s = ' '.join(v)
            except TypeError:
                s = str(v)
        else:
            s = v
        d[_metadata_rewrites.get(k, k.upper())] = s
    d["%s-%s.ebuild" % (pkg.package, pkg.fullver)] = \
        pkg.ebuild.get_fileobj().read()

    # this shouldn't be necessary post portage 2.2.
    # till then, their code requires redundant data,
    # so we've got this.
    if portage_compatible:
        d["CATEGORY"] = pkg.category
        d["PF"] = pkg.PF
    return d


class install(repo_interfaces.nonlivefs_install):

    def modify_repo(self):
        if self.observer is None:
            end = start = lambda x:None
        else:
            start = self.observer.phase_start
            end = self.observer.phase_end
        pkg = self.new_pkg
        final_path = discern_loc(self.repo.base, pkg, self.repo.extension)
        tmp_path = pjoin(os.path.dirname(final_path),
            ".tmp.%i.%s" % (os.getpid(), os.path.basename(final_path)))

        if not osutils.ensure_dirs(os.path.dirname(tmp_path), mode=0755):
            raise repo_interfaces.Failure("failed creating directory %r" %
                os.path.dirname(tmp_path))
        try:
            start("generating tarball: %s" % tmp_path)
            tar.write_set(pkg.contents, tmp_path, compressor='bz2')
            end("tarball created", True)
            start("writing Xpak")
            # ok... got a tarball.  now add xpak.
            xpak.Xpak.write_xpak(tmp_path, generate_attr_dict(pkg))
            end("wrote Xpak", True)
            # ok... we tagged the xpak on.
            os.chmod(tmp_path, 0644)
            os.rename(tmp_path, final_path)
        except Exception, e:
            try:
                os.unlink(tmp_path)
            except (IOError, OSError), e:
                if e.errno != errno.ENOENT:
                    logger.warn("failed removing %r: %r" % (tmp_path, e))
            raise
        return True


class uninstall(repo_interfaces.nonlivefs_uninstall):

    def modify_repo(self):
        os.unlink(discern_loc(self.repo.base, self.old_pkg, self.repo.extension))
        return True


class replace(install, uninstall, repo_interfaces.nonlivefs_replace):

    def modify_repo(self):
        uninstall.modify_repo(self)
        install.modify_repo(self)


class operations(repo_interfaces.operations):


    def _cmd_install(self, *args):
        return install(self.repo, *args)

    def _cmd_uninstall(self, *args):
        return uninstall(self.repo, *args)

    def _cmd_replace(self, *args):
        return replace(self.repo, *args)
