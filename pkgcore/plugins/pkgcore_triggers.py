# Copyright: 2006-2008 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD

from pkgcore.merge import triggers

pkgcore_plugins = {
    'triggers':[
        triggers.ldconfig,
        triggers.merge,
        triggers.unmerge,
        triggers.fix_uid_perms,
        triggers.fix_gid_perms,
        triggers.fix_set_bits,
        triggers.detect_world_writable,
        triggers.InfoRegen,
        triggers.CommonDirectoryModes,
        triggers.BaseSystemUnmergeProtection,
        ],
    }
