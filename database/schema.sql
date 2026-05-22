-- =========================================================
-- TABLE 1: characters
-- Stocke les 16 acteurs/personnages Harry Potter
-- =========================================================

CREATE TABLE IF NOT EXISTS characters (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    actor_name VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- TABLE 2: images
-- Chaque image du dataset
-- =========================================================

CREATE TABLE IF NOT EXISTS images (
    id INT PRIMARY KEY AUTO_INCREMENT,
    character_id INT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255),
    image_size INT,
    dataset_type ENUM('train', 'test', 'validation'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

-- =========================================================
-- TABLE 3: embeddings
-- Vecteurs faciaux extraits par FaceNet (128D)
-- embedding_vector = 128 nombres stockés en binaire
-- =========================================================

CREATE TABLE IF NOT EXISTS embeddings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    image_id INT NOT NULL,
    character_id INT NOT NULL,
    embedding_vector LONGBLOB NOT NULL,
    embedding_dim INT DEFAULT 128,
    model_version VARCHAR(50),
    processing_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES images(id),
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

-- =========================================================
-- TABLE 4: predictions
-- Historique COMPLET des prédictions
-- =========================================================

CREATE TABLE IF NOT EXISTS predictions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    image_id INT NOT NULL,
    predicted_character_id INT,
    predicted_character_name VARCHAR(100),
    true_character_id INT,
    confidence_score FLOAT NOT NULL,
    distance_euclidean FLOAT,
    is_correct BOOLEAN,
    inference_time_ms INT,
    model_version VARCHAR(50),
    run_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES images(id),
    FOREIGN KEY (predicted_character_id) REFERENCES characters(id),
    FOREIGN KEY (true_character_id) REFERENCES characters(id)
);

-- =========================================================
-- TABLE 5: execution_logs
-- Stats globales pour chaque "run" (exécution)
-- =========================================================

CREATE TABLE IF NOT EXISTS execution_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    run_id VARCHAR(100) NOT NULL UNIQUE,
    total_images INT,
    correct_predictions INT,
    accuracy FLOAT,
    total_processing_time_s FLOAT,
    avg_inference_time_ms FLOAT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- INSERT: Insérer les 16 personnages Harry Potter
-- =========================================================

INSERT IGNORE INTO characters (name, actor_name) VALUES
('Severus Snape', 'Alan Rickman'),
('Dean Thomas', 'Alfred Enoch'),
('Ginny Weasley', 'Bonnie Wright'),
('Harry Potter', 'Daniel Radcliffe'),
('Hermione Granger', 'Emma Watson'),
('Luna Lovegood', 'Evanna Lynch'),
('Bellatrix Lestrange', 'Helena Bonham Carter'),
('Molly Weasley', 'Julie Walters'),
('Minerva McGonagall', 'Maggie Smith'),
('Arthur Weasley', 'Mark Williams'),
('Neville Longbottom', 'Matthew Lewis'),
('Albus Dumbledore', 'Michael Gambon'),
('Lord Voldemort', 'Ralph Fiennes'),
('Rubeus Hagrid', 'Robbie Coltrane'),
('Ron Weasley', 'Rupert Grint'),
('Draco Malfoy', 'Tom Felton');