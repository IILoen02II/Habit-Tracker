-- Ejecutar DESPUÉS de schema.sql.
-- Corrige v_weekly_status: la meta se busca con el domingo de cada semana,
-- así la semana en curso aparece aunque la meta empiece a mitad de semana.
CREATE OR REPLACE VIEW v_weekly_status AS
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
                   AND (date_trunc('week', l.log_date)::date + 6) >= g.valid_from
                   AND (g.valid_to IS NULL
                        OR (date_trunc('week', l.log_date)::date + 6) <= g.valid_to)
WHERE h.frequency = 'weekly'
GROUP BY 1, h.id, h.name, g.target;

-- Opcional: las metas iniciales de schema.sql valen desde la fecha en que
-- lo ejecutaste. Si quieres registrar días anteriores, retrocede esa fecha:
-- UPDATE habit_goals SET valid_from = '2026-10-12' WHERE valid_to IS NULL;
