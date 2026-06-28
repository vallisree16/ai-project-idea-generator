CREATE DATABASE IF NOT EXISTS project_ideas_db;
USE project_ideas_db;

CREATE TABLE IF NOT EXISTS generated_ideas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profession VARCHAR(100) NOT NULL,
    experience_level VARCHAR(50),
    tech_stack VARCHAR(255),
    idea_title VARCHAR(255),
    idea_description TEXT,
    difficulty VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);