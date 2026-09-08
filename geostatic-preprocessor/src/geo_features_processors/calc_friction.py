from src.core.db_redis_manager.db_query_handler import *
import asyncpg

async def update_friction_coefficients(app):

    async def update(conn: asyncpg.Connection):

        await conn.execute("""
            INSERT INTO simulation_cell_state (
                h3_index,
                elevation,
                friction_coefficient
            )
            SELECT
                p.h3_index,
                p.elevation_m,
                0.35 * (
                    1.0
                    + 0.45 * LEAST(
                        1.0,
                        p.roughness / 10.0
                    )
                    + 0.30 *
                        CASE p.lulc
                            WHEN 10 THEN 0.10
                            WHEN 20 THEN 0.20
                            WHEN 30 THEN 0.15
                            WHEN 40 THEN 0.10
                            WHEN 50 THEN 1.00
                            WHEN 60 THEN 0.05
                            WHEN 70 THEN 0.00
                            WHEN 80 THEN 0.00
                            WHEN 90 THEN 0.25
                            WHEN 95 THEN 0.15
                            WHEN 100 THEN 0.15
                            ELSE 0.20
                        END
                    + 0.25 *
                        CASE
                            WHEN (
                                p.soil_sand +
                                p.soil_silt +
                                p.soil_clay
                            ) > 0
                            THEN
                                0.15 * p.soil_sand /
                                (
                                    p.soil_sand +
                                    p.soil_silt +
                                    p.soil_clay
                                )
                                +
                                0.30 * p.soil_silt /
                                (
                                    p.soil_sand +
                                    p.soil_silt +
                                    p.soil_clay
                                )
                                +
                                0.55 * p.soil_clay /
                                (
                                    p.soil_sand +
                                    p.soil_silt +
                                    p.soil_clay
                                )
                            ELSE 0.0
                        END
                )
            FROM prediction_parameters p
            ON CONFLICT (h3_index)
            DO UPDATE SET
                elevation = EXCLUDED.elevation,
                friction_coefficient = EXCLUDED.friction_coefficient
        """)

        print("Friction coefficients and elevations upserted successfully.")

    await query_db(update, app)