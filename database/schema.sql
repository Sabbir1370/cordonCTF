-- CordonCTF Database Schema
-- Run this file to create all tables and insert default data.

CREATE DATABASE IF NOT EXISTS cordonctf CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE cordonctf;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('player', 'admin') NOT NULL DEFAULT 'player',
    score INT DEFAULT 0,
    solve_count INT DEFAULT 0,
    last_solve_time DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Challenges table
CREATE TABLE IF NOT EXISTS challenges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INT,
    points INT NOT NULL,
    flag VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
);

-- Submissions table
CREATE TABLE IF NOT EXISTS submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    challenge_id INT NOT NULL,
    submitted_flag VARCHAR(255) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    points_awarded INT DEFAULT 0,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (challenge_id) REFERENCES challenges (id) ON DELETE CASCADE
);

-- Event status table (singleton)
CREATE TABLE IF NOT EXISTS event_status (
    id INT PRIMARY KEY DEFAULT 1,
    status ENUM('running', 'closed') NOT NULL DEFAULT 'closed',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default event status if not exists
INSERT IGNORE INTO event_status (id, status) VALUES (1, 'closed');

-- (Optional) Insert some default categories
INSERT IGNORE INTO
    categories (name)
VALUES ('Web'),
    ('Crypto'),
    ('Forensics'),
    ('Reverse Engineering'),
    ('Pwn'),
    ('Misc');