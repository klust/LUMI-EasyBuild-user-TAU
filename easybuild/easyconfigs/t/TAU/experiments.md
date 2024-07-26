# Experimenting with TAU installation


-   Downloads are prepared. Used the download links:
    
    -   [External packages `ezxt.tgz`](http://tau.uoregon.edu/ext.tgz)
    
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

```bash
./configure -prefix=$installdir \
    -c++=CC -cc=cc -fortran=ftn \
    -pdt=$EBROOTPDT -bfd=$EBROOTLIBBFD -unwind=$EBROOTLIBUNWIND
```

```bash
./configure -prefix=$installdir \
    -c++=CC -cc=cc -fortran=ftn \
    -mpi -mpilibrary=no \
    -pdt=$EBROOTPDT -bfd=$EBROOTLIBBFD -unwind=$EBROOTLIBUNWIND
```
-  `-mpilibrary=no: Analysis of the configure script suggests that this is needed to  
   trigger Cray-specific discovery of the MPI library options.
