# Experimenting with TAU installation


-   Downloads are prepared. Used the download links:
    
    -   [External packages `ext.tgz`](http://tau.uoregon.edu/ext.tgz)
    
    -   [TAU 2.33.2 `tau-2.33.2.tgz`](https://www.cs.uoregon.edu/research/tau/tau_releases/tau-2.33.2.tar.gz)
    
-   External tools for which we already have support in 23.09:

    -   PDT 3.25.2 is being made for this project

    -   [OPARI 2.0.8 via the `OPARI2` modules](https://lumi-supercomputer.github.io/LUMI-EasyBuild-docs/o/OPARI2/):
        source-to-source instrumentation tool for OpenMP and hybrid codes.
    
    -   [OTF2 3.0.3](https://lumi-supercomputer.github.io/LUMI-EasyBuild-docs/o/OTF2/)
    
    -   [BFD is offered by libbfd](https://lumi-supercomputer.github.io/LUMI-EasyBuild-docs/l/libbfd/)
    
    -   [libunwind 1.6.2](https://lumi-supercomputer.github.io/LUMI-EasyBuild-docs/l/libunwind/) 
        is offered in the standard software stack on LUMI

    -   [zlib](https://lumi-supercomputer.github.io/LUMI-EasyBuild-docs/z/zlib/)
        is a dependency via BFD but is part of the standard software stack on LUMI.
    
    
## Experiment 1

In the uncompressed TAU source code directory:

```bash
tc='cpeGNU'
tcversion='23.09'
module load LUMI/$tcversion partition/L
module load OPARI2/2.0.8-$tc-$tcversion OTF2/3.0.3-$tc-$tcversion libbfd/2.42-$tc-$tcversion
module load libunwind/1.6.2-$tc-$tcversion PDT/3.25.2-$tc-$tcversion
module unload cray-libsci    # To not add those link lines to the TAU wrappers
module unload perftools-base # You never know how they could interfere with TAU...
installdir="$PWD/../INSTALL-$tc-$tcversion"
```

The following have worked

1.  No MPI

    ```bash
    ./configure -prefix=$installdir \
        -c++=CC -cc=cc -fortran=ftn \
        -pdt=$EBROOTPDT -bfd=$EBROOTLIBBFD -unwind=$EBROOTLIBUNWIND
    ```

2.  MPI, but still using gcc/g++ instead of the wrappers for a number of files:

    ```bash
    ./configure -prefix=$installdir \
        -c++=CC -cc=cc -fortran=ftn \
        -mpi -mpilibrary=no \
        -pdt=$EBROOTPDT -bfd=$EBROOTLIBBFD -unwind=$EBROOTLIBUNWIND -zlib=$EBROOTZLIB \
        -otf=$EBROOTOTF2
    ```

    Analysis:

    -  `-mpilibrary=no: Analysis of the configure script suggests that this is needed to  
       trigger Cray-specific discovery of the MPI library options.

    -   I tried setting compilers also via environment variables to get rid of the parts that
        are still compiled with `gcc` and `g++` but that didn't work out. These compilers are
        really hard-coded in the package.

        Components built without the wrappers if no care is taken:

        -   In `src/TraceInput`:
            -   `libTAU_traceinput-gnu-mpi-pdt.a`: Build uses `TAU_CC_FE` and `TAU_CXX_FE` 
                from `include/Makefile`.
        -   In `utils`:
            -   Using `TAU_CC_FE` and `TAU_CXX_FE` 
                -   `pprof` executable
                -   `tau_reduce`, `tau_merge`, `tau_convert`  executables
                -   `tau2otf2`
                -   `tau_trace2json`
            -   Using `PDT_CXX_COMP` instead, set with the `-pdt_c++` configure flag:
                -   `tau_instrumentor`
                -   `tau_wrap`
                -   `tau_header_list`
                -   `tau_selectfile`

                The `-pdt_c++` flag causes the variable `PDT_CXX` to be set in `utils/include/Makefile`.
        -   In `utils/opari`
            -   `opari` executable


3.  Now also setting the PDT compiler to the C++ wrapper (which is also what was used for the module
    that is loaded)

    ```bash
    ./configure -prefix=$installdir \
        -c++=CC -cc=cc -fortran=ftn -pdt_c++=CC \
        -mpi -mpilibrary=no \
        -pdt=$EBROOTPDT -bfd=$EBROOTLIBBFD -unwind=$EBROOTLIBUNWIND -zlib=$EBROOTZLIB \
        -otf=$EBROOTOTF2
    ```

4.  Use the compiler wrappers as the C/C++ compiler for some parts in the `util` subdirectory
    and the library in `src/TraceInput`: 

    ```bash
    ./configure -prefix=$installdir \
        -c++=CC -cc=cc -fortran=ftn -pdt_c++=CC \
        -mpi -mpilibrary=no \
        -pdt=$EBROOTPDT -bfd=$EBROOTLIBBFD -unwind=$EBROOTLIBUNWIND -zlib=$EBROOTZLIB \
        -otf=$EBROOTOTF2
    sed -i -e 's|^TAU_CC_FE=gcc|TAU_CC_FE=cc|' -e 's|^TAU_CXX_FE=g++|TAU_CXX_FE=CC|' include/Makefile
    ```


