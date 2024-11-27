# Python base image
FROM python:3.11.4

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the local directory to the container
COPY . /app

# Upgrade pip and install dependencies (including Streamlit)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose Streamlit's default port
EXPOSE 7860

# Define the command to run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
