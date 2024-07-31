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
from easybuild.tools.modules import get_software_root, get_software_version


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
            'opari2':   [False, "Include OPARI2 support (built-in)", CUSTOM],
        })
        return extra_vars


    def configure_step(self):
        """Custom configuration procedure for PDT."""
        # custom prefix option for configure command
        self.cfg['prefix_opt'] = '-prefix='
        
        # Process the tauarch option for -arch
        if self.cfg['tauarch'] is not None:
            self.cfg.update('configopts', '-arch=%s' % self.cfg['tauarch'])
            self.log.info('TAU configuration: Architecture `-arch=%s` manually specified through EasyConfig parameter tauarch.')
        else:
            self.log.info('TAU configuration: Automatic architecture detection by the configure script, no `-arch` flag used.')

        # TAU's configure script ignores CFLAGS/CXXFLAGS set in the environment,
        # but allows to pass in custom flags via configure option
        if self.cfg['useropt']:
            useropt = self.cfg['useropt']
            self.log.info(f'TAU configuration: Value "{useropt}" for -useropt specified through EasyConfig parameter `useropt`.')
        else:
            useropt = os.getenv('CXXFLAGS')
            self.log.info('TAU configuration: CXXFLAGS found, automatically configuring `-useropt`.')
            if self.toolchain.options['pic']:
                useropt += ' -fPIC'
            if self.toolchain.options['debug']:
                self.log.info('TAU configuration: Debug symbol support requested via toolchainopts "debug", added automatically to `-useropt` via EasyBuild CXXFLAGS.')
        if useropt is not None:
            self.cfg.update('configopts', f'-useropt="{useropt}"')
        else:
            self.cfg.update('TAU configuration: No `-useropt` generated as the EasyConfig parameter `useropt` is not given and CXXFLAGS could not be found in the environment.')
            
        # Add the compiler names.
        comp_cc = os.getenv('CC')
        if comp_cc is not None:
            self.cfg.update('configopts', f'-cc={comp_cc}')
            self.log.info(f'TAU configuration: Found C compiler name, setting `-cc="{comp_cc}"`.')
        else:
            self.log.info('TAU configuration: C compiler name could not be found in the environment (CC), not setting `-cc`')
        comp_cxx = os.getenv('CXX')
        if comp_cc is not None:
            self.cfg.update('configopts', f'-c++={comp_cxx}')
            self.log.info(f'TAU configuration: Found C++ compiler name, setting `-c++="{comp_cxx}"`.')
        else:
            self.log.info('TAU configuration: C++ compiler name could not be found in the environment (CXX), not setting `-c++`')
        comp_fc = os.getenv('FC')
        if comp_fc is not None:
            self.cfg.update('configopts', f'-fortran={comp_fc}')
            self.log.info(f'TAU configuration: Found Fortran compiler name through $FC, setting `-fortran="{comp_fc}"`.')
        else:
            self.log.info('TAU configuration: Fortran compiler name could not be found in the environment (FC), not setting `-fortran`')
            
        # Include MPI support?
        if self.toolchain.options['usempi']:
            self.cfg.update('configopts', '-mpi -mpilibrary=no')
            self.log.info('TAU configuration: MPI support requested through toolchainopts, adding "-mpi -mpilibrary=no".')
        else:
            self.log.info('TAU configruation: MPI support not included (use toolchainopt `usempi` to do so).')
            
        # Include OpenMP support?
        if self.toolchain.options['openmp']:
            self.cfg.update('configopts', '-openmp')
            self.log.info('TAU configuration: OpenMP support requested through toolchainopts, adding "-openmp".')
        else:
            self.log.info('TAU configuration: OpenMP support not included (use toolchainopt `openmp` to do so).')
            
        # OPARI2 support for TAU? Note that TAU will build this itself, there seems to
        # be no way to pick it up from an external dependency
        # TODO: Does this make sense without -openmp?
        if self.cfg['opari2']:
            self.cfg.update('configopts', '-opari')
            self.log.info('TAU configuration: OPARI2 support requested via opari2 EasyConfig parameter, adding "-opari" which will enable `-openmp` internally in configure if not given.')
        else:
            self.log.info('TAU configuration: OPARI2 support not requested (use `opari2` EasyConfig parameter).')
            
        # Add zlib support (always through a dependency, auto-download not supported 
        # by this EasyBlock).
        if get_software_root('zlib'):
            self.cfg.update('configopts', '-zlib="$EBROOTZLIB"')
            self.log.info('TAU configuration: zlib support requested through dependencies, adding `-zlib="$EBROOTZLIB"`.')
        else:
            self.log.info('TAU configuration: zlib support (`-zlib`) was not added as it was not found as a dependency and download is not supported by this EasyBlock.')

        # Add libbfd (binutils) support (always through a dependency, auto-download not supported 
        # by this EasyBlock).
        if get_software_root('libbfd'):
            self.cfg.update('configopts', '-bfd="$EBROOTLIBBFD"')
            self.log.info('TAU configuration: libbfd (binutils) support requested through dependencies, adding `-bfd="$EBROOTLIBBFD"`.')
        else:
            self.log.info('TAU configuration: libbfd (binutils) support (`-bfd`) was not added as it was not found as a dependency and download is not supported by this EasyBlock.')
       
        # Add libunwind support (always through a dependency, auto-download not supported 
        # by this EasyBlock).
        if get_software_root('libunwind'):
            self.cfg.update('configopts', '-unwind="$EBROOTLIBUNWIND"')
            self.log.info('TAU configuration: libunwind support requested through dependencies, adding `-unwind="$EBROOTLIBUNWIND"`.')
        else:
            self.log.info('TAU configuration: libunwind support (`-unwind`) was not added as it was not found as a dependency and download is not supported by this EasyBlock.')
       
        # Add Open Trace Format support (always through OTF2 as a dependency)
        if get_software_root('OTF2'):
            self.cfg.update('configopts', '-otf="$EBROOTOTF2"')
            self.log.info('TAU configuration: OTF support requested through dependencies, adding `-otf="$EBROOTOTF2"`.')
        else:
            self.log.info('TAU configuration: OTF support (`-otf`) was not added as it was not found as a dependency, so no support included.')
       
        # Add PRogram Database Toolkit support (always through PDT as a dependency)
        if get_software_root('PDT'):
            self.cfg.update('configopts', '-pdt="$EBROOTPDT"')
            self.log.info('TAU configuration: PDT support requested through dependencies, adding `-pdt="$EBROOTPDT"`.')
        else:
            self.log.info('TAU configuration: PDT support (`-pdt`) was not added as it was not found as a dependency, so no support included.')
       
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
