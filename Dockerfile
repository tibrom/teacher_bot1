FROM python:3.9


WORKDIR /developer


COPY ./requirements.txt /developer/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /developer/requirements.txt



COPY . /developer


CMD ["python", "telegram_bot.py"]