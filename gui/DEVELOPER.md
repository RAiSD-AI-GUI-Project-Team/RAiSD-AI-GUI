# Developer reference

## RAiSD-AI

The RAiSD-AI-GUI relies on the RAiSD-AI tool to perform its computations. For more information about RAiSD-AI, please refer to the general [README.md](../README.md). It contains detailed information about the tool, its capabilities, and how it works.

## Install and Run

The process of installing and running the GUI is the same as for normal users, see the appropriate chapters [Installing the GUI](/README.md#installing-the-gui) and [Running the GUI](/README.md#running-the-gui) in the project [README.md](../README.md).

When working on the GUI, make sure to activate the `raisd-ai-gui` environment so that running and testing the GUI will work correctly.

## Configuration

The GUI relies on a config file to mirror the allowed operations, parameters, and their values in the RAiSD-AI tool. This allows the GUI to be flexible and adaptable to changes in the underlying tool without requiring significant code changes.

When making changes to the RAiSD-AI tool, make sure to update the config file accordingly to reflect the changes. This will ensure that the GUI continues to function correctly and provides an accurate interface for users to interact with the RAiSD-AI tool.

### Config schema

Refer to the TODO: schema file for details on the structure and content of the config file.

## development
all gui related code is in the gui/ folder

the environment is in ./environment-gui.yml

The gui code is divided into x packages:
### for each package small explanation of function
...

## Testing

run pytest ..

for code coverage run pytest --cov..