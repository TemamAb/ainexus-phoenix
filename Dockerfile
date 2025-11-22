FROM python:3.11-alpine
WORKDIR /app
RUN apk add --update nodejs npm
COPY package.json package-lock.json ./
RUN npm install
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "core/app.py"]
