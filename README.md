# Appointment Reservation System

## Table of Contents
- [Project Overview](#project-overview)
- [Repository Structure](#repository-structure)
- [Objectives](#objectives)
- [System Design](#system-design)
- [Installation and Usage](#installation-and-usage)
- [Features](#features)
- [Achievements](#achievements)
- [Future Work](#future-work)
- [Contributors](#contributors)

## Project Overview
This project was developed to gain experience with database application development and learn how to use SQL within Python via pymssql. We have built an appointment scheduler for vaccinations, where users are patients and caregivers managing vaccine stock and appointments. The application is designed to run on a command line terminal and connect to a database server on a Microsoft Azure account.

## Repository Structure

| Project Directories | Brief Description |
|---|---|
| [`/src`](./src) | Contains the source code for the project, subdivided into [`/resources`](./src/resources) for the SQL script and design document, and [`/scheduler`](./src/scheduler) for the application's scheduling functions. |
| `.gitignore` | A file specifying patterns of files/directories to ignore in git operations. |
| `LICENSE` | This file contains the license under which the project is released. |
| `README.md` | This file contains detailed information about the project, its architecture, and its usage. |
| `requirements.txt` | This file lists the Python dependencies that need to be installed to run the project. |

## Objectives
The primary objectives of this project were:
- Designing the database schema with an E/R diagram and `create table` statements.
- Implementing the code that stores patient information and allows users to interactively schedule their vaccine appointments.

<p align="center">
  <img src="src//resources//ER_design.png"><br>
  <em>Fig.0 - E/R diagram of the database schema.</em>
</p>

## System Design
The appointment reservation system was designed with a focus on user interaction and data management. It allows for account creation, login, caregiver schedule searching, appointment reservation, viewing scheduled appointments, and user logout.

<p align="center">
  <img src="images//pipeline.png"><br>
  <em>Fig.0 - Abstract Pipeline for Heart Rate Detection.</em>
</p>


## Installation and Usage
To use this application, Python, pymssql, and Anaconda need to be installed on your computer. After cloning the repository to your local machine and navigating to the project directory, you can run `Scheduler.py` to start the application.

## Features
This system implements the following features:
1. Account creation for patients
2. Patient login
3. Search for caregiver schedule
4. Reserving an appointment
5. Displaying scheduled appointments for the current user
6. User logout

## Achievements
Through this project, we successfully implemented a command-line interface application that allows users to create accounts, log in, search for available caregivers, reserve appointments, view scheduled appointments, and log out. We also designed and implemented a database schema to support these operations.

## Future Work
While the current version of the application fulfills all the specified requirements, there are several potential enhancements that could make it more robust and user-friendly:
- Addition of a graphical user interface (GUI) to provide a more intuitive user experience.
- Implementing additional error checking to handle all possible exceptions.
- Improving the login system to include features like password recovery and multi-factor authentication.


## Contributors
- **[Contributor's Name]**: [Short bio or description of contributions]

Please replace `[Contributor's Name]` with the actual contributors' names and provide a short bio or description of what they contributed to the project.
