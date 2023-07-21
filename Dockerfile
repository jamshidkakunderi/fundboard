FROM odoo:16.0
ENV PYTHONUNBUFFERED 1
RUN pip3 install psycopg2-binary
RUN pip3 install bravado-core
COPY ./config/odoo.conf /etc/odoo/
COPY ./addons /mnt/extra-addons/
