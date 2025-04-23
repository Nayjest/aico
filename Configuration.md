## Overview
AI-Coder configuration is stored in the `.env` file.

## Supported configuration values
Minimal configuration example: [.env.example](https://github.com/Nayjest/aico/blob/main/.env.example)  
See supported values here: [ai-microcore:configuration.py](https://github.com/Nayjest/ai-microcore/blob/main/microcore/configuration.py)

## Configuration file lookup priority

1. `<AICO_MODULE_LOCATION>/<ENV_FILE>` &mdash; Only for dev. purposes
2. `<CURRENT_WORKING_DIR>/.aico/<ENV_FILE>`  &mdash; Project-specific configuration
3.  `<AICO_USER_HOME>/<ENV_FILE>` &mdash; User-specific configuration
4. `<CURRENT_WORKING_DIR>/.aico/<ENV_FILE>` 

`ENV_FILE` is `.env`, but may be overriden by `--env` command line argument (highest priority) or AICO_ENV_FILE OS Environment variable.