# Database Schema
+------------------+------------------------------------------------------+
| Table: users |
+------------------+------------------------------------------------------+
| id | INT PRIMARY KEY AUTO_INCREMENT |
| username | VARCHAR(50) UNIQUE NOT NULL |
| password_hash | VARCHAR(255) NOT NULL |
| role | ENUM('player','admin') NOT NULL |
| score | INT DEFAULT 0 |
| solve_count | INT DEFAULT 0 |
| last_solve_time | DATETIME NULL |
| created_at | DATETIME DEFAULT CURRENT_TIMESTAMP |
+------------------+------------------------------------------------------+

+------------------+------------------------------------------------------+
| Table: categories |
+------------------+------------------------------------------------------+
| id | INT PRIMARY KEY AUTO_INCREMENT |
| name | VARCHAR(100) UNIQUE NOT NULL |
+------------------+------------------------------------------------------+

+------------------+------------------------------------------------------+
| Table: challenges |
+------------------+------------------------------------------------------+
| id | INT PRIMARY KEY AUTO_INCREMENT |
| title | VARCHAR(200) NOT NULL |
| description | TEXT |
| category_id | INT (FK -> categories.id) |
| points | INT NOT NULL |
| flag | VARCHAR(255) NOT NULL |
| file_path | VARCHAR(500) NULL |
| created_at | DATETIME DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME ON UPDATE CURRENT_TIMESTAMP |
+------------------+------------------------------------------------------+

+------------------+------------------------------------------------------+
| Table: submissions |
+------------------+------------------------------------------------------+
| id | INT PRIMARY KEY AUTO_INCREMENT |
| user_id | INT (FK -> users.id) |
| challenge_id | INT (FK -> challenges.id) |
| submitted_flag | VARCHAR(255) NOT NULL |
| is_correct | BOOLEAN NOT NULL |
| points_awarded | INT DEFAULT 0 |
| submitted_at | DATETIME DEFAULT CURRENT_TIMESTAMP |
+------------------+------------------------------------------------------+

+------------------+------------------------------------------------------+
| Table: event_status |
+------------------+------------------------------------------------------+
| id | INT PRIMARY KEY AUTO_INCREMENT |
| status | ENUM('running','closed') NOT NULL DEFAULT 'closed' |
| updated_at | DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE |
+------------------+------------------------------------------------------+

## ER Diagram
![ER Diagram](diagrams/er_diagram.svg)
