FROM python:3.9

WORKDIR /lynos

# Install pdm
# The official Docker image for pdm is not maintained.
RUN curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 - -p /usr/local

COPY . .

RUN pdm install

CMD [ "pdm", "run", "uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "4242" ]