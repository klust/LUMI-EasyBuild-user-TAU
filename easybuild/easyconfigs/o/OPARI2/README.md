# OPARI2

-   [OPARI2 web site](https://www.vi-hps.org/tools/opari2.html)

    -   [Documentation](https://perftools.pages.jsc.fz-juelich.de/cicd/opari2/tags/latest/html/)
    
        The main source for installation information is the `INSTALL` file though, 
        but there is
        [an online copy](https://perftools.pages.jsc.fz-juelich.de/cicd/opari2/tags/latest/html/installationfile.html).
        


OPARI2, the successor of Forschungszentrum Jülich's OPARI, is a source-to-source 
instrumentation tool for OpenMP and hybrid codes. It surrounds OpenMP directives 
and runtime library calls with calls to the POMP2 measurement interface. 
The POMP2 interface can be implemented by tool builders who want, for example, 
to monitor the performance of OpenMP applications. Like its predecessor, 
OPARI2 works with Fortran, C, and C++ programs. Additional features compared to 
OPARI are a new initialization method that allows for multi-directory and parallel 
builds as well as the usage of pre-instrumented libraries. Furthermore, an efficient 
way of tracking parent-child thread-relationships was added. Additionally OPARI2 was 
extended to support instrumentation of OpenMP 3.0 tied tasks. OPARI is used by many 
performance analysis tools (e.g. TAU, ompP, KOJAK, Scalasca, VampirTrace) whereas 
OPARI2 is currently used by Score-P and TAU.


## Installation instructions

The installation is a bit special in that OPARI2 doesn't seem to honour the compiler
settings given through environment variables to the `configure` script which is otherwise
a pretty standard autotools thing.

It turns out that the full build cycle used the compilers set in
`build-config/common/platforms/platform-frontend-crayunknown`.

For each recognized platform, there are actually three such files:

-   `*-frontend-*` set `*_FOR_BUILD` environment variables.
-   `*-backend-*` set the regular non-MPI environment variables such as `CC` and `CXX`.
-   `*-mpi-*` set the `MPI_*` environment variables.

The OPARI2 build however only uses the `*-frontend-*` files. This is likely because 
the build process was copied from another code (Score-P?) that uses all three.

The values in the `*-frontend-*` files can be overwritten on the command line of `configure`, 
but they have to be given as values on the command line and not as variables in the 
environment as those are not picked up.


## EasyBuild support

-   [OPARI2 support in the EasyBuilders repository](https://github.com/easybuilders/easybuild-easyconfigs/tree/develop/easybuild/easyconfigs/o/OPARI2)

-   [OPARI2 support in the CSCS repository](https://github.com/easybuilders/CSCS/tree/master/easybuild/easyconfigs/o/OPARI2)

-   [OPARI2 support in the JSC repository](https://github.com/easybuilders/JSC/tree/2024/Golden_Repo/o/OPARI2)


### Version 2.0.8 for CPE 23.09

-   The EasyConfig was prepared by Jan André Reuter of JSC based on EasyConfigs in use
    at JSC.


### Revision of July-August 2024

-   It turns out that the earlier EasyConfigs compile everything with the system compilers
    and without architecture-specific optimisations.
    
    This doesn't have to be a disaster as all that is generated are statically linked
    executables that do not interfer with other software, and as it is not the kind of code
    that will be called frequently.
    
-   We now add the `*_FOR_BUILD` values as options on the configure command line through
    `configopts` so that the EasyBuild-set flags are honoured.
    
-   It turns out that the package supports pre-install testing so that was also added.
    
-   Improved the sanity check a bit.

-   Added license information to the installation.

-   The cpeAMD version did not pass the tests so there we currently still use GCC, 
    but then from the `gcc-mixed` module and with a proper architecture option.
    
