#!/bin/bash
aerich init -t settings.TORTOISE_ORM
aerich init-db
aerich migrate
aerich upgrade
uvicorn main:app --host 0.0.0.0 --port 8000