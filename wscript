#!/usr/bin/env python

APPNAME = 'talloc'
VERSION = '2.0.3'


blddir = 'bin'

import Logs
import os, sys

# find the buildtools directory
srcdir = '.'
while not os.path.exists(srcdir+'/buildtools') and len(srcdir.split('/')) < 5:
    srcdir = '../' + srcdir
sys.path.insert(0, srcdir + '/buildtools/wafsamba')

import sys
sys.path.insert(0, srcdir+"/buildtools/wafsamba")
import wafsamba, samba_dist, Options

# setup what directories to put in a tarball
samba_dist.DIST_DIRS('lib/talloc:. lib/replace:lib/replace buildtools:buildtools')


def set_options(opt):
    opt.BUILTIN_DEFAULT('replace')
    opt.PRIVATE_EXTENSION_DEFAULT('talloc', noextension='talloc')
    opt.RECURSE('lib/replace')
    opt.add_option('--enable-talloc-compat1',
                   help=("Build talloc 1.x.x compat library [False]"),
                   action="store_true", dest='TALLOC_COMPAT1', default=False)
    if opt.IN_LAUNCH_DIR():
        opt.add_option('--disable-python',
                       help=("disable the pytevent module"),
                       action="store_true", dest='disable_python', default=False)


def configure(conf):
    conf.RECURSE('lib/replace')

    conf.env.standalone_talloc = conf.IN_LAUNCH_DIR()

    conf.env.disable_python = getattr(Options.options, 'disable_python', False)

    if not conf.env.standalone_talloc:
        if conf.CHECK_BUNDLED_SYSTEM('talloc', minversion=VERSION,
                                     implied_deps='replace'):
            conf.define('USING_SYSTEM_TALLOC', 1)
        if conf.CHECK_BUNDLED_SYSTEM('pytalloc-util', minversion=VERSION,
                                     implied_deps='talloc replace'):
            conf.define('USING_SYSTEM_PYTALLOC_UTIL', 1)

    conf.env.TALLOC_COMPAT1 = Options.options.TALLOC_COMPAT1

    if conf.env.standalone_talloc:
        conf.find_program('xsltproc', var='XSLTPROC')

    if not conf.env.disable_python:
        # also disable if we don't have the python libs installed
        conf.check_tool('python')
        conf.check_python_version((2,4,2))
        conf.check_python_headers(mandatory=False)
        if not conf.env.HAVE_PYTHON_H:
            Logs.warn('Disabling pytalloc-util as python devel libs not found')
            conf.env.disable_python = True

    conf.SAMBA_CONFIG_H()


def build(bld):
    bld.RECURSE('lib/replace')

    if bld.env.standalone_talloc:
        bld.env.PKGCONFIGDIR = '${LIBDIR}/pkgconfig'
        bld.env.TALLOC_VERSION = VERSION
        bld.PKG_CONFIG_FILES('talloc.pc', vnum=VERSION)
        bld.INSTALL_FILES('${INCLUDEDIR}', 'talloc.h')
        private_library = False
        vnum = VERSION

        # should we also install the symlink to libtalloc1.so here?
        bld.SAMBA_LIBRARY('talloc-compat1',
                          'compat/talloc_compat1.c',
                          deps='talloc',
                          enabled=bld.env.TALLOC_COMPAT1,
                          vnum=VERSION)

        if not bld.env.disable_python:
            bld.PKG_CONFIG_FILES('pytalloc-util.pc', vnum=VERSION)
    else:
        private_library = True
        vnum = None

    if not bld.CONFIG_SET('USING_SYSTEM_TALLOC'):

        bld.SAMBA_LIBRARY('talloc',
                          'talloc.c',
                          deps='replace',
                          abi_file='ABI/talloc-%s.sigs' % VERSION,
                          abi_match='talloc* _talloc*',
                          hide_symbols=True,
                          vnum=vnum,
                          private_library=private_library,
                          manpages='talloc.3')

    if not bld.CONFIG_SET('USING_SYSTEM_PYTALLOC_UTIL') and not bld.env.disable_python:

        bld.SAMBA_SUBSYSTEM('PYTALLOC',
            source='pytalloc.c',
            public_deps='talloc',
            pyext=True,
            )

    if not getattr(bld.env, '_SAMBA_BUILD_', 0) == 4:
        # s4 already has the talloc testsuite builtin to smbtorture
        bld.SAMBA_BINARY('talloc_testsuite',
                         'testsuite_main.c testsuite.c',
                         deps='talloc',
                         install=False)


def test(ctx):
    '''run talloc testsuite'''
    import Utils, samba_utils
    cmd = os.path.join(Utils.g_module.blddir, 'talloc_testsuite')
    ret = samba_utils.RUN_COMMAND(cmd)
    print("testsuite returned %d" % ret)
    sys.exit(ret)

def dist():
    '''makes a tarball for distribution'''
    samba_dist.dist()
