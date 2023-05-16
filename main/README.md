


``` bash
flask --app manager db init
flask --app manager db migrate
mysql> show tables;
+-----------------+
| Tables_in_main  |
+-----------------+
| alembic_version |
+-----------------+

flask --app manager db upgrade
mysql> show tables;
+-----------------+
| Tables_in_main  |
+-----------------+
| alembic_version |
| product         |
| product_user    |
| user            |
+-----------------+
```