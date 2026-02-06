CREATE TABLE IF NOT EXISTS marseille_arrivals (
    train_id TEXT PRIMARY KEY,
    departure_scheduled TIMESTAMPTZ,
    departure_actual TIMESTAMPTZ,
    arrival_scheduled TIMESTAMPTZ,
    arrival_actual TIMESTAMPTZ,
    stop_name TEXT NOT NULL,
    train_type TEXT,
    train_name TEXT,
    departure_is_late BOOLEAN,
    arrival_is_late BOOLEAN 
);
