FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /usr/src/app

ENV PROFILE PROFILE

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN ls

RUN pip install --no-cache-dir --upgrade -r /usr/src/app/requirements.txt

COPY . . 

RUN chmod -R 755 ./module/CPClient_linux_x64
#  로 빌드시에 매번 권한부여

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "5000"]