## OpenMind


### Запуск бекенда

#### Запуск бд
```bash
docker network create local-apps 
```

```bash
docker run --name local-pg12 \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_INITDB_ARGS="--locale=C.UTF-8" \
    -v ~/Documents/storedata/pg-data:/var/lib/postgresql/data \
    -p 5432:5432 \
    --network="local-apps" \
    --restart always \
    -d postgres:12.0-alpine
```

```bash
docker exec -it local-pg12 psql -U postgres
```

```sql
CREATE USER open_mind CREATEDB LOGIN PASSWORD 'super_mega_mind_password';
CREATE DATABASE open_mind WITH OWNER = open_mind CONNECTION LIMIT = -1;
GRANT ALL PRIVILEGES ON DATABASE open_mind to open_mind;

CREATE DATABASE open_mind2 WITH OWNER = open_mind CONNECTION LIMIT = -1;
GRANT ALL PRIVILEGES ON DATABASE open_mind2 to open_mind;
```

#### Для выполенние асинхронных задач используется Celery. Требуется брокер и бекенд в виде реббита

Можно установать в докере:

```bash
docker run --name local-rabbit-host \
    -v ~/Documents/storedata/rabbit-data/:/var/lib/rabbitmq \
    -p 5672:5672 \
    -p 15672:15672 \
    --network="local-apps" \
    --restart always \
    -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password \
    -d rabbitmq:3.8.9-management
```

#### Настройки 

```bash
cp sample.env .env
```

#### Зависимости

***Нужен Python 3.8***

**Создаем и активируем виртуальное окружение**

```bash
pip install -r requirements.txt
```

#### Зависимости фронтенда(опционально только для разработки)

```bash
cd front
npm i
```
Разработка
```bash
npm run dev
```
Сборка
```bash
npm run build
```

#### Запуск севера

```bash
python manage.py migrate
```


```bash
python manage.py createsuperuser
```

```bash
python manage.py runserver
```

```bash
docker build -t opemind/proj:4 .
docker save -o opemind opemind/proj:4
scp opemind study@194.67.105.157:~/
rm openind
ssh study@194.67.105.157 "docker load -i opemind"
ssh study@194.67.105.157 "rm openind"
```

```bash
docker-compose -f docker-compose-workers.yml up -d --scale regular_workers=1 --timeout 50
```