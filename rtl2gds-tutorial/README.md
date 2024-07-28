# About
A tutorial on the RTL-to-GDS flow using open source toolchain.

![RTL2GDS ToolChain](../doc/rtl2gds-toolchain.svg)

# Installation

- Before installation, upgrade your distribution:
  - `sudo apt update -y && sudo apt upgrade -y`
- **Icarus Verilog (iverilog) gtkwave**
  - `sudo apt install iverilog gtkwave` This will install version available in the distro package repo which is typically an older version.
  - If you need to install the _latest version_, you need to compile from source. Use the following instructions for it:
    - Install the pre-reqs: `sudo apt install gperf autoconf gcc g++ flex bison make`
    - `git clone https://github.com/steveicarus/iverilog.git`
    - `cd iverilog`
    - `sh autoconf.sh`
    - `./configure`
    - `make`
    - `sudo make install`

- **Yosys**
  - Yosys can be installed from binaries using the [Tabby CAD Suite](https://www.yosyshq.com/tabby-cad-datasheet) or the [OSS CAD Suite](https://github.com/YosysHQ/oss-cad-suite-build). You can follow the instructions on the [Yosys GitHub Page](https://github.com/YosysHQ/yosys#installation).
  - If you want to build from the source, you can follow the instructions at the [Yosys GitHub Page](https://github.com/YosysHQ/yosys#building-from-source) OR, follow these steps:
  - Install the **pre-reqs**:
    - `sudo apt install build−essential clang bison flex`
    - `sudo apt install libreadline−dev gawk tcl−dev libffi−dev git`
    - `sudo apt install graphviz xdot pkg−config python3 libboost−system−dev` 
    - `sudo apt install libboost−python−dev libboost−filesystem−dev zlib1g−dev`
  - Clone the repo, build and install the package:
    - `git clone https://github.com/YosysHQ/yosys.git`
    - `cd yosys`
    - `git submodule update --init`
    - `make`  **WARNING** Takes a while to compile.
    - `sudo make install`
    - If you want to quickly run through an example, follow the [Getting Started](https://github.com/YosysHQ/yosys#getting-started) section in the Yosys github site.

- **OpenROAD** (**OpenSTA** included) is a comprehensive tool for chip physical design that transforms a synthesized Verilog netlist into a routed layout. The OpenROAD can used in two ways:
  1. [OpenROAD StandAlone Application](https://github.com/The-OpenROAD-Project/OpenROAD) ([Doc](https://openroad.readthedocs.io/en/latest/main/README.html)) is a set of binaries for digital `Place \& Route (PnR)`  that can be used by any other RTL-GDSII flow.
  2. [OpenROAD Flow Script (ORFS)](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts) ([Doc](https://openroad-flow-scripts.readthedocs.io/en/latest/)) is the native OpenROAD flow that consists of a set of integrated scripts for an autonomous RTL-GDSII flow using OpenROAD and other open-source tools.

  - In this tutorial we will follow the OpenROAD standalone application so we can get an idea about each of the steps in the RTL2GDS flow.
  - **Installation Steps**:
    - `git clone --recursive https://github.com/The-OpenROAD-Project/OpenROAD.git`
    - `cd OpenROAD`
    - `sudo ./etc/DependencyInstaller.sh`
    - `mkdir build`
    - `cd build`
    - `cmake ..`
    - `make`
    - `sudo make install`
  - Verify the installation by running `openroad`
 
# Tutorial Flow

In this tutorial, we will use a simple counter to go through the entire flow.

- **Design Verification (DV)** of the design using `iverilog` and `gtkwave`
  - `iverilog -o counter.vvp counter.v tb_counter.v`
