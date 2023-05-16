


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

``` py
# routing_key에 따라 다른 앱으로 publish
def publish():
    channel.basic_publish(exchange='', routing_key='main', body='hello')
```

``` bash
# PUT/POST/DELETE

# main - flask
mysql> select * from product;
+----+-----------+-----------+
| id | title     | image     |
+----+-----------+-----------+
|  2 | new title | new image |
+----+-----------+-----------+
```

TypeError: Object of type Product is not JSON serializable
