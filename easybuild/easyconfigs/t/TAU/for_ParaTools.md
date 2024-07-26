*   What is the role of PDT in the TAU story? I see it uses EDG 4.4
    which is not even C++11-compliant...
   
*   The configure tool of PDT is really bad

    *   It does not detect a failure to configure or build the dependencies
        (certainly not the various rose* components) and instead declares
        successful termination.
        
    *   It passes compiler flags given via `-useropt` down to the configure
        process of those tools, but does not pass the compilers and instead
        uses whatever gcc is.
        
        The result of this is that the compiler fails if options were used 
        for the main compiler that are not recognized by the compiler used
        for the dependencies. E.g., our build tool, when compiling with
        AMD AOCC, automatically passes the flags "-O2 -ffp-model=precise",
        but the `-ffp-model` flag is not recognised by the GNU compiler and
        as a result compiling fails which is actually already detected in
        the configure phase of those tools.
        
        A related problem is that the architecture flags are different for
        both compilers. When using the Cray wrappers we don't even need to
        pass them explicitly as the wrappers take care of that, but the
        system compiler will generate binaries for a generic architecture
        that way.

    Most users on LUMI use the Cray compiler wrappers, but depending on the
    type of job, either the GNU or Cray compilers are used. Some users may
    be using the aocc compiler also for CPU code and I expect that some may
    simply be using the compilers that come with ROCm via PrgEnv-amd to
    compile GPU applications.
    
    Could there be potential problems with these mixed compiler builds?
    From the output of ldd I get the impression that you simply used the 
    system gcc to build the whole package?
    
    I am currently building in the project where I do all software development
    for LUST but I can move that to our joint project so that I can better show
    how we put software in our software stacks.
    
*   What options and modules did you use for the builds of TAU?        
        
