-- =====================================================
-- Habit tracker - esquema PostgreSQL
-- Uso personal (un solo usuario), semana de lunes a domingo
-- =====================================================

CREATE EXTENSION IF NOT EXISTS btree_gist;  -- para evitar metas solapadas

-- -----------------------------------------------------
-- 1. Hábitos (nunca se borran, se desactivan)
-- -----------------------------------------------------
CREATE TABLE habits (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    unit        TEXT NOT NULL,                       -- 'litros', 'horas', 'minutos', 'veces'
    frequency   TEXT NOT NULL DEFAULT 'daily'
                CHECK (frequency IN ('daily', 'weekly')),
    direction   TEXT NOT NULL DEFAULT 'min'
                CHECK (direction IN ('min', 'max')), -- min = "al menos", max = "como máximo"
    active      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- -----------------------------------------------------
-- 2. Historial de metas (cada día se evalúa con la meta vigente ese día)
--    Para hábitos weekly, target = meta por semana (ej. 3 veces)
-- -----------------------------------------------------
CREATE TABLE habit_goals (
    id          SERIAL PRIMARY KEY,
    habit_id    INT NOT NULL REFERENCES habits(id),
    target      NUMERIC(8,2) NOT NULL CHECK (target >= 0),
    valid_from  DATE NOT NULL,
    valid_to    DATE,                                -- NULL = meta vigente
    CHECK (valid_to IS NULL OR valid_to >= valid_from),
    EXCLUDE USING gist (
        habit_id WITH =,
        daterange(valid_from, valid_to, '[]') WITH &&
    )
);

-- -----------------------------------------------------
-- 3. Registros: una fila por hábito y día
--    El sueño se registra en el día en que despiertas
--    Hábitos sí/no: value = 1 (hecho) o 0 (no hecho)
-- -----------------------------------------------------
CREATE TABLE daily_logs (
    id          SERIAL PRIMARY KEY,
    habit_id    INT NOT NULL REFERENCES habits(id),
    log_date    DATE NOT NULL,
    value       NUMERIC(8,2) NOT NULL CHECK (value >= 0),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (habit_id, log_date)
);

CREATE INDEX idx_logs_date ON daily_logs (log_date);

-- -----------------------------------------------------
-- 4. Vista: cumplimiento diario (hábitos daily)
-- -----------------------------------------------------
CREATE VIEW v_daily_status AS
SELECT
    l.log_date,
    h.id   AS habit_id,
    h.name AS habit,
    l.value,
    g.target,
    h.direction,
    CASE WHEN h.direction = 'min' THEN l.value >= g.target
         ELSE l.value <= g.target
    END AS met
FROM daily_logs l
JOIN habits h       ON h.id = l.habit_id
JOIN habit_goals g  ON g.habit_id = l.habit_id
                   AND l.log_date >= g.valid_from
                   AND (g.valid_to IS NULL OR l.log_date <= g.valid_to)
WHERE h.frequency = 'daily';

-- -----------------------------------------------------
-- 5. Vista: cumplimiento semanal (lunes a domingo)
--    date_trunc('week') en Postgres ya empieza en lunes
-- -----------------------------------------------------
CREATE VIEW v_weekly_status AS
SELECT
    date_trunc('week', l.log_date)::date AS week_start,
    h.id   AS habit_id,
    h.name AS habit,
    SUM(l.value) AS total,
    g.target,
    SUM(l.value) >= g.target AS met
FROM daily_logs l
JOIN habits h       ON h.id = l.habit_id
JOIN habit_goals g  ON g.habit_id = l.habit_id
                   AND date_trunc('week', l.log_date)::date >= g.valid_from
                   AND (g.valid_to IS NULL OR date_trunc('week', l.log_date)::date <= g.valid_to)
WHERE h.frequency = 'weekly'
GROUP BY 1, h.id, h.name, g.target;

-- -----------------------------------------------------
-- 6. Datos iniciales (METAS DE EJEMPLO: ajústalas a las tuyas)
-- -----------------------------------------------------
INSERT INTO habits (name, unit, frequency, direction) VALUES
    ('Agua',          'litros',  'daily',  'min'),
    ('Sueño',         'horas',   'daily',  'min'),
    ('Ejercicio',     'veces',   'weekly', 'min'),
    ('Estudio',       'horas',   'daily',  'min'),
    ('Videojuegos',   'horas',   'daily',  'max'),
    ('Estudio bíblico','minutos','daily',  'min');

INSERT INTO habit_goals (habit_id, target, valid_from)
SELECT id, t.target, CURRENT_DATE
FROM habits h
JOIN (VALUES
    ('Agua', 2.0), ('Sueño', 7.0), ('Ejercicio', 3.0),
    ('Estudio', 2.0), ('Videojuegos', 2.0), ('Estudio bíblico', 15.0)
) AS t(name, target) ON t.name = h.name;

-- =====================================================
-- CONSULTAS ÚTILES
-- =====================================================

-- A) Rachas de días cumplidos (gaps and islands) para hábitos diarios
-- WITH islands AS (
--     SELECT habit_id, habit, log_date,
--            log_date - (ROW_NUMBER() OVER (PARTITION BY habit_id ORDER BY log_date))::int AS grp
--     FROM v_daily_status
--     WHERE met
-- )
-- SELECT habit, MIN(log_date) AS inicio, MAX(log_date) AS fin, COUNT(*) AS dias
-- FROM islands
-- GROUP BY habit_id, habit, grp
-- ORDER BY habit, inicio DESC;

-- B) % de cumplimiento de los últimos 30 días
-- SELECT habit, ROUND(100.0 * COUNT(*) FILTER (WHERE met) / COUNT(*), 1) AS pct
-- FROM v_daily_status
-- WHERE log_date >= CURRENT_DATE - 30
-- GROUP BY habit;

-- C) Semanas cumplidas de ejercicio
-- SELECT week_start, total, target, met FROM v_weekly_status
-- WHERE habit = 'Ejercicio' ORDER BY week_start DESC;

-- D) Mejor día de la semana por hábito
-- SELECT habit, TO_CHAR(log_date, 'Day') AS dia,
--        ROUND(100.0 * AVG(met::int), 1) AS pct
-- FROM v_daily_status GROUP BY habit, 2 ORDER BY habit, pct DESC;
