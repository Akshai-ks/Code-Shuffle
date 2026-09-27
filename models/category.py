from database.db import get_db


class CategoryModel:

    @staticmethod
    def get_all_categories():
        conn = get_db()
        cursor = conn.cursor()

        query = """
            SELECT
                c.id,
                c.name,
                c.slug,
                c.icon,
                c.created_at,
                (
                    SELECT COUNT(*)
                    FROM quotes
                    WHERE category_id = c.id
                      AND status = 'approved'
                ) AS quote_count
            FROM categories c
            ORDER BY c.name ASC
        """

        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def get_category_by_id(cat_id):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM categories WHERE id = %s",
                (cat_id,)
            )

            row = cursor.fetchone()
            return dict(row) if row else None

        finally:
            conn.close()

    @staticmethod
    def get_category_by_slug(slug):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM categories WHERE slug = %s",
                (slug,)
            )

            row = cursor.fetchone()
            return dict(row) if row else None

        finally:
            conn.close()

    @staticmethod
    def create_category(name, slug, icon='✨'):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO categories (name, slug, icon)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (
                name.strip(),
                slug.strip().lower(),
                icon.strip()
            ))

            new_id = cursor.fetchone()['id']
            conn.commit()

            return new_id, None

        except Exception as e:
            conn.rollback()
            return None, str(e)

        finally:
            conn.close()

    @staticmethod
    def update_category(cat_id, name, slug, icon):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE categories
                SET name = %s,
                    slug = %s,
                    icon = %s
                WHERE id = %s
            """, (
                name.strip(),
                slug.strip().lower(),
                icon.strip(),
                cat_id
            ))

            conn.commit()

            return True, None

        except Exception as e:
            conn.rollback()
            return False, str(e)

        finally:
            conn.close()

    @staticmethod
    def delete_category(cat_id):
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM categories WHERE id = %s",
                (cat_id,)
            )

            conn.commit()
            return True

        except Exception:
            conn.rollback()
            return False

        finally:
            conn.close()