-- Creates the test database alongside the main one at container startup
SELECT 'CREATE DATABASE taskmanager_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'taskmanager_test')\gexec
