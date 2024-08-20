-- Adminer 4.8.1 PostgreSQL 13.16 dump

-- DROP TABLE IF EXISTS "role";
-- DROP SEQUENCE IF EXISTS role_id_seq;
-- CREATE SEQUENCE role_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

-- CREATE TABLE "public"."role" (
--     "id" integer DEFAULT nextval('role_id_seq') NOT NULL,
--     "name" character varying NOT NULL,
--     "description" character varying,
--     "created_at" integer,
--     "updated_at" integer,
--     "is_deleted" boolean,
--     CONSTRAINT "role_name_key" UNIQUE ("name"),
--     CONSTRAINT "role_pkey" PRIMARY KEY ("id")
-- ) WITH (oids = false);

INSERT INTO "role" ("id", "name", "description", "created_at", "updated_at", "is_deleted") VALUES
(2,	'doctor',	'doctor role',	NULL,	NULL,	NULL),
(1,	'admin',	'full access',	NULL,	NULL,	NULL),
(3,	'patient',	'patient role',	NULL,	NULL,	NULL);

-- -- 2024-08-12 17:06:21.0559+00
-- -- Xóa tất cả dữ liệu từ bảng user_roles
-- DELETE FROM user_roles;

-- -- Xóa tất cả dữ liệu từ bảng patient
-- DELETE FROM patient;

-- -- Xóa tất cả dữ liệu từ bảng user
-- DELETE FROM "user";
