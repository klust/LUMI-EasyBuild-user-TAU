# LUMI-EasyBuild-user-TAU

Temporary repository to collaborate on the development of a TAU installation for LUMI.

## How to use the EasyConfigs?

Basically follow the [EasyBuild instructions in the LUMI User Documentation](https://docs.lumi-supercomputer.eu/software/installing/easybuild/).

1.  Create a subdirectory for the installation, e.g., 

    ```bash
    mkdir -p /project/project_462000600/EasyBuild   
    ```

2.  In that directory, clone the GitHub repository `klust/LUMI-EasyBuild-user-TAU`. Then rename the
    directory to `UserRepo`.
    E.g., read-only:
    
    ```bash
    cd /project/project_462000600/EasyBuild
    git clone https://github.com/klust/LUMI-EasyBuild-user-TAU.git
    mv LUMI-EasyBuild-user-TAU UserRepo
    ```

3.  Set the `EBU_USER_PREFIX` environment variable as described in the LUMI documentation:

    ```bash
    export EBU_USER_PREFIX="/project/project_462000600/EasyBuild"
    ```

4.  And you're ready to load `LUMI/23.09`, a partition module if you want to experiment with
    cross-compiling, and `EasyBuild-user` to configure EasyBuild.


## Remarks on configuring TAU

For now, see [`easybuild/easyconfigs/t/TAU/experiments.md`](easybuild/easyconfigs/t/TAU/experiments.md).
