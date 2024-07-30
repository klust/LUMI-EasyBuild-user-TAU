##
# This is an easyblock for EasyBuild, see https://github.com/easybuilders/easybuild
#
# Developed by Kurt Lust for the LUMI consortium and based on a similar EasyBlock
# for PDT
#
##
"""
EasyBuild support for building and installing PDT, implemented as an easyblock

@author Kurt Lust (UAntwerpen & LUMI consortium)
"""

import os

from easybuild.easyblocks.generic.configuremake import ConfigureMake
import easybuild.tools.toolchain as toolchain
from easybuild.framework.easyconfig import CUSTOM
from easybuild.tools.build_log import EasyBuildError
from easybuild.tools.filetools import symlink


def find_arch_dir(install_dir):
    """
    Find architecture directory inside the install tree.

    For simplicity any top-level folder containing a bin and lib directory is collected
    Raises an error if multiple or none matching folders are found
    Returns the architecture specific folder
    """
    arch_dirs = []
    for entry in os.listdir(install_dir):
        full_path = os.path.join(install_dir, entry)
        # Only check directories which are not symlinks
        # E.g. on x86_64 there are symlinks craycnl, mic_linux, ... to x86_64
        if not os.path.isdir(full_path) or os.path.islink(full_path):
            continue
        if all(os.path.isdir(os.path.join(full_path, subdir)) for subdir in ['bin', 'lib']):
            arch_dirs.append(full_path)

    if not arch_dirs:
        raise EasyBuildError('Architecture specific directory not found in %s', install_dir)
    elif len(arch_dirs) != 1:
        raise EasyBuildError('Found multiple architecture specific directories: %s', ', '.join(arch_dirs))
    return arch_dirs[0]


class EB_TAULUMI(ConfigureMake):
    """Support for building/installing PDT, enhanced for Cray systems with the LUMI toolchains."""
    
    @staticmethod
    def extra_options(extra_vars=None):
        """Define custom easyconfig parameters specific to MPICH."""
        extra_vars = ConfigureMake.extra_options(extra_vars)
        extra_vars.update({
            'tauarch': [None,  "Architecture for TAU (auto-determined by TAU if absent).", CUSTOM],
            'useropt': [None,  "Overwrite the automatically determined value for the useropt option.", CUSTOM],
            'opari':   [False, "Include OPARI2 support (built-in)", CUSTOM],
        })
        return extra_vars


    def configure_step(self):
        """Custom configuration procedure for PDT."""
        # custom prefix option for configure command
        self.cfg['prefix_opt'] = '-prefix='
        
        # Process the tauarch option for -arch
        if self.cfg['tauarch'] is not None:
            self.cfg.update('configopts', '-arch=%s' % self.cfg['tauarch'])

        # TAU's configure script ignores CFLAGS/CXXFLAGS set in the environment,
        # but allows to pass in custom flags via configure option
        if self.cfg['useropt']:
            useropt = self.cfg['useropt']
        else:
            useropt = os.getenv('CXXFLAGS')
            if self.toolchain.options['pic']:
                useropt += ' -fPIC'
        if useropt is not None:
            self.cfg.update('configopts', f'-useropt="{useropt} -g"')
            
        # Add the compiler names.
        comp_cc = os.getenv('CC')
        if comp_cc is not None:
            self.cfg.update('configopts', f'-cc={comp_cc}')
        comp_cxx = os.getenv('CXX')
        if comp_cc is not None:
            self.cfg.update('configopts', f'-c++={comp_cxx}')
        comp_fc = os.getenv('FC')
        if comp_fc is not None:
            self.cfg.update('configopts', f'-fortran={comp_fc}')

        # Configure creates required subfolders in installdir, so create first (but only once, during first iteration)
        if self.iter_idx == 0:
            super(EB_TAULUMI, self).make_installdir()

        super(EB_TAULUMI, self).configure_step()

    def build_step(self):
        """Skip build step"""
        # `make install` runs `make all` which runs `make clean`, so no point in doing a make first
        pass

    def make_installdir(self):
        """Skip creating installation directory, already done in configure step"""
        pass

    def install_step(self):
        """Create symlinks into arch-specific directories"""

        if self.cfg['parallel']:
            self.cfg.update('installopts', '-j %s' % self.cfg['parallel'])

        super(EB_TAULUMI, self).install_step()

        # Link arch-specific directories into prefix
        arch_dir = find_arch_dir(self.installdir)
        self.log.info('Found %s as architecture specific directory. Creating symlinks...', arch_dir)
        for subdir in ('bin', 'lib'):
            src = os.path.join(arch_dir, subdir)
            dst = os.path.join(self.installdir, subdir)
            if os.path.lexists(dst):
                self.log.info('Skipping creation of symlink %s as it already exists', dst)
            else:
                symlink(os.path.relpath(src, self.installdir), dst, use_abspath_source=False)

#    def sanity_check_step(self):
#        """Custom sanity check for PDT."""
#        custom_paths = {
#            'files': [os.path.join('bin', 'cparse'),
#                      os.path.join('include', 'pdb.h'),
#                      os.path.join('lib', 'libpdb.a')],
#            'dirs': [],
#        }
#        super(EB_TAULUMI, self).sanity_check_step(custom_paths=custom_paths)
