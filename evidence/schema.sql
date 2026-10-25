-- IrsanAI-A5 Evidence Graph Schema
-- Compatible with SQLite (Termux-First)

CREATE TABLE IF NOT EXISTS evidence (
  evidence_id       TEXT PRIMARY KEY,
  target            TEXT NOT NULL,
  provider          TEXT NOT NULL,
  file_path         TEXT,
  file_line         TEXT,
  offset            TEXT,
  sha256            TEXT NOT NULL,
  confidence        TEXT NOT NULL,
  confidence_score  REAL,
  limitation        TEXT,
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS diagnosis (
  diagnosis_id      TEXT PRIMARY KEY,
  evidence_id       TEXT REFERENCES evidence(evidence_id),
  best_diagnosis    TEXT NOT NULL,
  torwart_status    TEXT,
  survival          TEXT,
  residual          TEXT,
  overall_confidence REAL,
  boundary_map      TEXT,
  status            TEXT,
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR REPLACE INTO evidence (
  evidence_id, target, provider, file_path, file_line, offset,
  sha256, confidence, confidence_score, limitation
) VALUES (
  'spd-melee-baseline-001',
  'Shattered Pixel Dungeon',
  'spd_cli',
  'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/items/weapon/melee/MeleeWeapon.java',
  NULL,
  'damageRoll',
  'PLACEHOLDER_SHA256_OF_MELEEWEAPON',
  'observed',
  0.95,
  'static source only; runtime Barrier.absorb vs Normal(DRMin,DRMax) order residual remains'
);

INSERT OR REPLACE INTO diagnosis (
  diagnosis_id, evidence_id, best_diagnosis, torwart_status, survival,
  residual, overall_confidence, boundary_map, status
) VALUES (
  'diag-spd-barrier-dr-001',
  'spd-melee-baseline-001',
  'effective = Glyph(Barrier.absorb(buffed) - Normal(DRMin,DRMax)); raw = NormalIntRange(min,max)*aug + Uniform(0,exStr); DRMax = tier*(2+lvl) with overflow',
  'pending_aap_v1_2',
  NULL,
  'Barrier absorb applied before DR subtraction – order may invert under certain glyph/buff combinations',
  0.80,
  NULL,
  'open'
);
