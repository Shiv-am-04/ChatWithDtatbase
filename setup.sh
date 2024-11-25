#!/bin/bash

# Create the .streamlit directory if it doesn't exist
mkdir -p ~/.streamlit/

# Create the credentials.toml file with your email
echo "\
[general]\n\
email = \"shivamghuge004@gmail,com\"\n\
" > ~/.streamlit/credentials.toml

# Create the config.toml file with the appropriate server settings
echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
