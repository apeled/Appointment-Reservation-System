CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Caregivers_username varchar(255) REFERENCES Caregivers(Username),
    Available INT,
    PRIMARY KEY (Time, Caregivers_username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Appointments (
    appointment_id varchar(255),
    Patients_username varchar(255) REFERENCES Patients(Username),
    Vaccines_name varchar(255) REFERENCES Vaccines(Name),
    Caregivers_username varchar(255),
    Time date,
    FOREIGN KEY(Time, Caregivers_username) REFERENCES Availabilities(Time, Caregivers_username),
    PRIMARY KEY (appointment_id)
);
