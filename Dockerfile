FROM python:3.8.6
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
EXPOSE 8080

# Env Variables
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE

CMD jupyter notebook --port=8080 --ip=0.0.0.0 --allow-root
