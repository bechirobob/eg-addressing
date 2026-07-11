-- PostGIS Phase 2: canonical address-record geometry.
-- This migration only derives geometry from canonical address_records WGS84 columns.
-- Raw citizen/geotag intake rows remain evidence and are not made official geometry here.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis') THEN
        RAISE EXCEPTION 'PostGIS extension must be installed before applying 005_address_record_postgis_geometry.sql';
    END IF;
END $$;

ALTER TABLE address_records
    ADD COLUMN IF NOT EXISTS geom geography(Point, 4326);

UPDATE address_records
SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography
WHERE geom IS NULL
  AND latitude BETWEEN -90 AND 90
  AND longitude BETWEEN -180 AND 180;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'address_records_latitude_valid'
          AND conrelid = 'address_records'::regclass
    ) THEN
        ALTER TABLE address_records
            ADD CONSTRAINT address_records_latitude_valid
            CHECK (latitude BETWEEN -90 AND 90) NOT VALID;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'address_records_longitude_valid'
          AND conrelid = 'address_records'::regclass
    ) THEN
        ALTER TABLE address_records
            ADD CONSTRAINT address_records_longitude_valid
            CHECK (longitude BETWEEN -180 AND 180) NOT VALID;
    END IF;
END $$;

ALTER TABLE address_records VALIDATE CONSTRAINT address_records_latitude_valid;
ALTER TABLE address_records VALIDATE CONSTRAINT address_records_longitude_valid;

CREATE INDEX IF NOT EXISTS idx_address_records_geom
    ON address_records
    USING gist (geom);
