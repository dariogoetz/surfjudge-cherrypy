FROM ubuntu

RUN apt-get update && apt-get install -y python-pip

RUN pip install cherrypy configobj bcrypt jinja2 sqlalchemy xlsxwriter

ADD surfjudge /surfjudge

EXPOSE 80

WORKDIR /surfjudge

CMD ["python", "main.py", "--webserver"]