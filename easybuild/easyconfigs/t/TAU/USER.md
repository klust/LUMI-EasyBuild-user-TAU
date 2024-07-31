# User instructions for TAU

The TAU Performance System® is a portable profiling and tracing toolkit for 
performance analysis of parallel programs written in Fortran, C, C++, UPC, 
Java, Python.
It is developed at the computer science department of the University of Oregon.
However, commercial support is available via 
[ParaTools, Inc.](https://www.paratools.com/) and CSC has a support contract with
them. Hence expect most support questions not to be treated by the LUMI User Support
Team or CSC support, but to be forwarded to ParaTools. Note that the company is on
the USA West Coast, so due to the time difference, the answer will not be immediate
and it is important to be as precise as possible in your support request so that
not too many emails back-and-forth are needed to understand the problem.

## Configuring TAU

It is rather likely that TAU will have to be reconfigured for your specific application
and to work with other tools you want to use in your project. 

The LUST developed support for TAU in EasyBuild. Due to the extent of possible configurations
and the difficulties to test all features, also because the LUST is not a level 3 support team
and has limited resources for development and knowledge for such testing, this will likely be
a never ending project and changes may be needed to accommodate new use cases.

The support for TAU relies on a so-called EasyBlock that will generate the right commands
to configure and build TAU based on a number of options specified in different ways in the
EasyConfig.

-   Several parameters in the `toolchainopt` line influence the building process.
  
    An example is:

    ```python
    toolchainopts = {'debug': True, 'usempi': True, 'openmp': True}
    ```

    These options are:

    -   `debug`: Ensures that `-g` is added to the compiler flags to include symbol information.
        It may be a good idea to leave this on.

    -   `usempi`: Enables MPI support in TAU. Set to false or simply delete that option to build
        without MPI support.

        Note that building with MPI will hard-code some paths to libraries, etc., in a number of 
        scripts. This may cause the package to fail after a system update as sometimes we have to
        force users to use a different MPI version because the older version is broken after a
        network stack update.

    -   `openmp`: Enable OpenMP support in TAU (the `-openmp` flag of the TAU `configure` script),
        if it is not already turned on by other options that are used.

-   Some parameters are set via EasyConfig options:

    -   `tauarch`: The TAU architecture, used as the value for the `-arch=` flag. Usually automatic
        determination is fine though and it is not really needed.

    -   `useropt`: The value for the `-useropt=` flag. The EasyBlock will try to determine reasonable
        values automatically though unless the SYSTEM toolchain would be used.

    -   `opari2`: When set to `True`, the included OPARI2 support of TAU will be enabled. The TAU
        build process is currently not able to use an externally provided OPARI2.

-   Configuration options that are added based on detected dependencies.
    The detection code is currently based on the presence of `EBROOT` environment variables so may
    not work with Cray-provided modules.

    Currently supported are:

    -   `zlib`: Will enable zlib support in TAU (`-zlib` flag of the TAU configure script)

    -   `libbfd`: Will enable binutils libbfd subbport in TAU (`-bfd` flag in the TAU configure script)

    -   `libunwind`: Will enable libunwind as the unwinder in TAU (`-unwind` flag in the TAU configure script)

    -   `OTF2`: Will enable support for Open Trace Format version 2 in TAU, a format that is also used
        by various other tools. (The `-otf` flag in the TAU configure script)

    -   `PDT`: Will enable support for the Program Database Toolkit (PDT) in TAU
        (`-pdt` flag in the TAU configure script)
