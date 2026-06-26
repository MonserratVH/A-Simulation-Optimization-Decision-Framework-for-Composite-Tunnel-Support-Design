# How to define composite section plate properties and evaluate tunnel liner capacity with PLAXIS

## Description
With the PLAXIS 2D tunnel liner property definition and capacity evaluation tools, the processes of calculating the equivalent plate properties in PLAXIS 2D input on one hand as well as displaying support capacity plots in PLAXIS 2D Output on the other hand can be fully automated.

## Prerequisites
* Plaxis version: 2D CE V22.01
* Python 3.8.10

## Modules used
The Python script requires the following modules:
* The `plxscripting` module to interact with PLAXIS software
* The `PySide2` module to interact with the user
* The `matplotlib` module to create plots
* The `os` module for various Windows folder handling
* The `sys` module to access Python runtime environment
* The `numpy` module for scientific computing with Python


## Running the script
To use this file:
* Download the package;
* Extract the zipped package and copy the content TunnelCompositeSectionLibrary_Input.pyw, TunnelSupportCapacityPlot_Output.pyw and shared.py files to:
  `<PLAXIS 2D installation folder>\pytools\shared`  
  When using the default installation folder for PLAXIS 2D, this would be  
  `C:\Program Files\Bentley\Geotechnical\PLAXIS 2D CONNECT Edition V22\`
* In PLAXIS 2D Input, create the equivalent homogenized plate for the tunnel lining using the TunnelCompositeSectionLibrary_Input.pyw script
* In the Expert menu, go to Expert > Run Python script > Open... browse for TunnelCompositeSectionLibrary_Input.pyw
* Run the PLAXIS 2D analysis and upload corresponding results in PLAXIS 2D Output program
* In PLAXIS 2D Output, the support capacity plots for previously defined tunnel linings can be drawn using the TunnelSupportCapacityPlot_Output.pyw script
* In the Expert menu, go to Expert > Run Python script > Open... browse for TunnelSupportCapacityPlot_Output.pyw
* When you do not have access rights to add the script in this folder, alternatively, you can save and extract the zipped package in a local folder
* Then, in PLAXIS 2D, go to Expert > Run Python script > Open … and browse for either TunnelCompositeSectionLibrary_Input.pyw or TunnelSupportCapacityPlot_Output.pyw depending on whether you are willing to create equivalent homogenized plate material set(s) for the tunnel lining(s) in PLAXIS 2D Input or looking to generating the support capacity plots in PLAXIS 2D Output.

## Bentley Communities link
https://communities.bentley.com/products/geotech-analysis/w/wiki/62987/support-capacity-evaluation-of-a-tunnel-lining-in-plaxis-2d

## Disclaimer
_Copyright (c) Plaxis bv. All rights reserved. Unless explicitly acquired and licensed from Licensor under another license, the contents of this file are subject to the Plaxis Public License ("PPL") Version 1.0, or subsequent versions as allowed by the PPL, and You may not copy or use this file in either source code or executable form, except in compliance with the terms and conditions of the PPL.
All software distributed under the PPL is provided strictly on an "AS IS" basis, WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, AND LICENSOR HEREBY DISCLAIMS ALL SUCH WARRANTIES, INCLUDING WITHOUT LIMITATION, ANY WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, QUIET ENJOYMENT, OR NON-INFRINGEMENT. See the PPL for specific language governing rights and limitations under the PPL._
