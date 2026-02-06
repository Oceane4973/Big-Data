CREATE USER "grafana_user" WITH PASSWORD 'grafana_password_123';

GRANT CONNECT ON DATABASE sncf_organized_data TO "grafana_user";

\c sncf_organized_data

GRANT USAGE ON SCHEMA public TO "grafana_user";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "grafana_user";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO "grafana_user";