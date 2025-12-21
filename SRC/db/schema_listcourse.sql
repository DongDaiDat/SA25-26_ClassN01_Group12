BEGIN;

-- ========= 1) miscore_listcourse =========
CREATE TABLE IF NOT EXISTS public.miscore_listcourse (
  id               BIGSERIAL PRIMARY KEY,
  semester_no      SMALLINT NOT NULL CHECK (semester_no >= 0),
  requirement_type VARCHAR(20) NOT NULL,
  category         VARCHAR(50) NOT NULL DEFAULT '',
  notes            TEXT        NOT NULL DEFAULT '',
  is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
  course_id        BIGINT      NOT NULL,
  curriculum_id    BIGINT      NOT NULL
);

-- FKs & UNIQUE (guard bằng DO $$ ... $$)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname='miscore_listcourse_course_id_daecabef_fk_miscore_course_id'
  ) THEN
    ALTER TABLE public.miscore_listcourse
      ADD CONSTRAINT miscore_listcourse_course_id_daecabef_fk_miscore_course_id
      FOREIGN KEY (course_id) REFERENCES public.miscore_course (id) DEFERRABLE INITIALLY DEFERRED;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname='miscore_listcourse_curriculum_id_fb8f74f6_fk_miscore_c'
  ) THEN
    ALTER TABLE public.miscore_listcourse
      ADD CONSTRAINT miscore_listcourse_curriculum_id_fb8f74f6_fk_miscore_c
      FOREIGN KEY (curriculum_id) REFERENCES public.miscore_curriculum (id) DEFERRABLE INITIALLY DEFERRED;
  END IF;

  -- Chống trùng (curriculum_id, course_id)
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname='listcourse_unique_cur_course'
  ) THEN
    ALTER TABLE public.miscore_listcourse
      ADD CONSTRAINT listcourse_unique_cur_course UNIQUE (curriculum_id, course_id);
  END IF;
END $$;

-- Indexes
CREATE INDEX IF NOT EXISTS miscore_listcourse_course_id_daecabef     ON public.miscore_listcourse (course_id);
CREATE INDEX IF NOT EXISTS miscore_listcourse_curriculum_id_fb8f74f6 ON public.miscore_listcourse (curriculum_id);
CREATE INDEX IF NOT EXISTS miscore_lc_cur_sem_idx ON public.miscore_listcourse (curriculum_id, semester_no);
CREATE INDEX IF NOT EXISTS miscore_lc_cur_req_idx ON public.miscore_listcourse (curriculum_id, requirement_type);
CREATE INDEX IF NOT EXISTS miscore_lc_cur_cat_idx ON public.miscore_listcourse (curriculum_id, category);
CREATE INDEX IF NOT EXISTS miscore_lc_course_idx  ON public.miscore_listcourse (course_id);

-- ========= 2) miscore_listcourserelation =========
CREATE TABLE IF NOT EXISTS public.miscore_listcourserelation (
  id              BIGSERIAL PRIMARY KEY,
  relation_type   VARCHAR(20) NOT NULL,
  course_item_id  BIGINT      NOT NULL,
  curriculum_id   BIGINT      NOT NULL,
  related_item_id BIGINT      NOT NULL
);

DO $$
BEGIN
  -- Unique bộ (curriculum_id, course_item_id, related_item_id, relation_type)
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname='miscore_listcourserelati_curriculum_id_course_ite_eee67d4b_uniq'
  ) THEN
    ALTER TABLE public.miscore_listcourserelation
      ADD CONSTRAINT miscore_listcourserelati_curriculum_id_course_ite_eee67d4b_uniq
      UNIQUE (curriculum_id, course_item_id, related_item_id, relation_type);
  END IF;

  -- FKs
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname='miscore_listcoursere_course_item_id_baff81de_fk_miscore_l'
  ) THEN
    ALTER TABLE public.miscore_listcourserelation
      ADD CONSTRAINT miscore_listcoursere_course_item_id_baff81de_fk_miscore_l
      FOREIGN KEY (course_item_id) REFERENCES public.miscore_listcourse (id) DEFERRABLE INITIALLY DEFERRED;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname='miscore_listcoursere_curriculum_id_6b084ab9_fk_miscore_c'
  ) THEN
    ALTER TABLE public.miscore_listcourserelation
      ADD CONSTRAINT miscore_listcoursere_curriculum_id_6b084ab9_fk_miscore_c
      FOREIGN KEY (curriculum_id) REFERENCES public.miscore_curriculum (id) DEFERRABLE INITIALLY DEFERRED;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname='miscore_listcoursere_related_item_id_a8966abd_fk_miscore_l'
  ) THEN
    ALTER TABLE public.miscore_listcourserelation
      ADD CONSTRAINT miscore_listcoursere_related_item_id_a8966abd_fk_miscore_l
      FOREIGN KEY (related_item_id) REFERENCES public.miscore_listcourse (id) DEFERRABLE INITIALLY DEFERRED;
  END IF;
END $$;

-- Indexes phụ trợ
CREATE INDEX IF NOT EXISTS miscore_listcourserelation_course_item_id_baff81de ON public.miscore_listcourserelation (course_item_id);
CREATE INDEX IF NOT EXISTS miscore_listcourserelation_curriculum_id_6b084ab9 ON public.miscore_listcourserelation (curriculum_id);
CREATE INDEX IF NOT EXISTS miscore_listcourserelation_related_item_id_a8966abd ON public.miscore_listcourserelation (related_item_id);
CREATE INDEX IF NOT EXISTS miscore_lis_curricu_79b083_idx ON public.miscore_listcourserelation (curriculum_id, course_item_id);
CREATE INDEX IF NOT EXISTS miscore_lis_curricu_9cd107_idx ON public.miscore_listcourserelation (curriculum_id, related_item_id);
CREATE INDEX IF NOT EXISTS miscore_lis_curricu_f08364_idx ON public.miscore_listcourserelation (curriculum_id, relation_type);

COMMIT;
