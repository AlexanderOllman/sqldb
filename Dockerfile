FROM python:3.8

WORKDIR /workspace

ADD src/requirements.txt /workspace/requirements.txt
RUN pip install -r requirements.txt

ADD src/app.py src/pa_theme.py src/portfolio-assistant.png src/favicon.ico src/quote_template.pdf /workspace/

ENV HOME=/workspace

EXPOSE 80

CMD [ "python3" , "/workspace/app.py" ]
