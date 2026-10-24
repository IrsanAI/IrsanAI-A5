CREATE TABLE evidence (evidence_id TEXT PRIMARY KEY, target TEXT, provider TEXT, file_path TEXT, offset TEXT, sha256 TEXT, confidence TEXT, confidence_score REAL, limitation TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE diagnosis (diagnosis_id TEXT PRIMARY KEY, best_diagnosis TEXT, torwart_status TEXT, survival TEXT, residual TEXT, overall_confidence REAL, status TEXT);
