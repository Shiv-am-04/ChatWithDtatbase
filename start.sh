mkdir -p ~/.streamlit/

# Create credentials.toml
cat <<EOL > ~/.streamlit/credentials.toml
[general]
email = "shivamghuge004@gmail.com"
EOL

# Create config.toml
cat <<EOL > ~/.streamlit/config.toml
[server]
headless = true
enableCORS = false
port = $PORT
EOL
