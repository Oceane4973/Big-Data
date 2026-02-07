CREATE TABLE Perturbations (
    id_perturbation VARCHAR(100) PRIMARY KEY,
    origine varchar(200)
);

CREATE TABLE Endroits (
    id_endroit VARCHAR(100) PRIMARY KEY,
    nom VARCHAR(200),
    longitude REAL,
    latitude REAL
);

CREATE TABLE points_arrets (
    id_perturbation VARCHAR(100),
    id_endroit VARCHAR(100),
    base_arrival_time INTEGER,
    base_departure_time INTEGER,
    amended_arrival_time INTEGER,
    amended_departure_time INTEGER,
    CONSTRAINT fk_perturb FOREIGN KEY(id_perturbation) REFERENCES Perturbations(id_perturbation),
    CONSTRAINT fk_endroits FOREIGN KEY(id_endroit) REFERENCES Endroits(id_endroit)
);