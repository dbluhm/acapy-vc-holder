FROM ghcr.io/hyperledger/aries-cloudagent-python:py3.9-nightly-2024-03-13

COPY ./pyproject.toml ./README.md ./
RUN mkdir acapy_vc_holder && touch acapy_vc_holder/__init__.py
# Must install ACA-Py from PR commit since not merged yet
RUN yes | pip uninstall aries-cloudagent
RUN pip install git+https://github.com/sicpa-dlab/aries-cloudagent-python@505263411782c488f88952c97d857d4bd2772661
RUN pip install -e .

COPY ./acapy_vc_holder ./acapy_vc_holder
