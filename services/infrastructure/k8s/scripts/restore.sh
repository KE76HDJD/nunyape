#!/bin/bash
cat $1 | docker exec -i postgres psql -U user -d appdb