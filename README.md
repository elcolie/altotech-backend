# Note
Postgres is TimescaleDB in docker container
`esb_subscriber.py` is in the same folder of `manage.py`

# IAQ_sensor/iaq_publisher.py
1. Run `source export.sh` to export the AWS credential
2. Run the `iaq_publisher.py` to publish the message
3. Run the `iaq_subscriber.py` to subscribe the message

# LifeBeing Sensor
Run into SNS error then use direct SQS to bypass the problem.
1. Run `export.sh` to export the AWS credential
1. Run [life_being_publisher.py](LifeBeing_sensor/life_being_publisher.py) to publish the message
2. Run [life_being_subscriber.py](LifeBeing_sensor/life_being_subscriber.py) to subscribe the message

# Run Event Streaming Bus
1. cd to same folder of `manage.py`
2. python `esb_subscriber.py`
3. Observe the Django `raw_data` table

# Prepare Timeseries Database
Use Django custom command to fill the Power Meter (kW) in TimescaleDB
`python manage.py prepare_timeseries_data`

# Realtime database:
1. `source export.sh` with supabase database url to open for connection and store latest sensor readings
1. `raw_data` table has `db_index=True` for efficient querying.

# 2. Django-python
http://localhost:8000/api/hotels/ List and SearchFilter
http://localhost:8000/api/hotels/26/floors/ Access floors in a hotel
http://localhost:8000/api/floors/26/rooms/ List room on a floor
http://localhost:8000/api/rooms/101/data/ Latest IoT data of a room 101
http://localhost:8000/api/rooms/101/data/life_being  Latest Life Being sensor
http://localhost:8000/api/rooms/101/data/iaq/  Latest IAQ sensor
http://localhost:8000/api/hotels/1/energy_summary/?resolution=1day&subsystem=lighting&start_time=2024-03-01T00:00:00&end_time=2025-08-10T23:59:59&format1=csv  Returns CSV. It haven't finished yet.


# claude_mcp
It must a new project `pyenv` is messed up with `uv`.
`/Users/sarit/learn_mcp/altotech_smart_building/altotech_smart_building`

https://github.com/elcolie/altotech-mcp-demo

# Docker compose. Bring up the Django project. Postgres TimescaleDB
- `docker compose -f docker-compose.local.yml build`
- `docker compose -f docker-compose.local.yml build up`.
- Continue on https://github.com/elcolie/altotech-backend for MCP and Chat Interface.

# To generate database diagram.
1. `python manage.py graph_models -a -o my_diagram.dot`
1. `dot -Tpng my_diagram.dot -o my_diagram.png`
