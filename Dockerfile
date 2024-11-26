FROM python:3.11.4

# creating directory 
WORKDIR /code

# copying the requirements.txt to code directory
COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN useradd user

USER user

ENV HOME=home/user \
    PATH=home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user . $HOME/app


CMD ["streamlit","app.py","--host","0.0.0.0","--port","7860"]