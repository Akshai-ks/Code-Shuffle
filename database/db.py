import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in the environment.")


def get_db():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )


def init_db():
    conn = get_db()

    try:
        seed_categories(conn)
        seed_users(conn)
        seed_quotes(conn)
        conn.commit()
    finally:
        conn.close()

    print("Database initialized successfully!")


def seed_categories(conn):
    categories = [
        ('Motivation', 'motivation', '🔥'),
        ('Life', 'life', '🌟'),
        ('Success', 'success', '🏆'),
        ('Study', 'study', '📚'),
        ('Coding', 'coding', '💻'),
        ('Friendship', 'friendship', '🤝'),
        ('Love', 'love', '❤️'),
        ('Happiness', 'happiness', '😊'),
        ('Leadership', 'leadership', '🦁'),
        ('Personal Growth', 'personal-growth', '🌱'),
        ('Funny', 'funny', '😂'),
        ('Education', 'education', '🎓')
    ]

    cursor = conn.cursor()

    for name, slug, icon in categories:
        cursor.execute('''
            INSERT INTO categories (name, slug, icon)
            VALUES (%s, %s, %s)
            ON CONFLICT(slug) DO UPDATE
            SET name = EXCLUDED.name,
                icon = EXCLUDED.icon
        ''', (name, slug, icon))

    conn.commit()


def seed_users(conn):
    cursor = conn.cursor()

    # Admin User
    cursor.execute(
        "SELECT id FROM users WHERE email = 'admin@stthomas.edu.in'"
    )

    if not cursor.fetchone():
        admin_pass = generate_password_hash('admin123')

        cursor.execute('''
            INSERT INTO users (name, email, password_hash, role)
            VALUES (%s, %s, %s, 'admin')
        ''', (
            'Rotaract Admin',
            'admin@stthomas.edu.in',
            admin_pass
        ))

    # Demo Student
    cursor.execute(
        "SELECT id FROM users WHERE email = 'akshai@stthomas.edu.in'"
    )

    if not cursor.fetchone():
        student_pass = generate_password_hash('student123')

        cursor.execute('''
            INSERT INTO users (name, email, password_hash, role)
            VALUES (%s, %s, %s, 'student')
        ''', (
            'Akshai V.S.',
            'akshai@stthomas.edu.in',
            student_pass
        ))

    # Demo Student 2
    cursor.execute(
        "SELECT id FROM users WHERE email = 'ananya@stthomas.edu.in'"
    )

    if not cursor.fetchone():
        student_pass2 = generate_password_hash('student123')

        cursor.execute('''
            INSERT INTO users (name, email, password_hash, role)
            VALUES (%s, %s, %s, 'student')
        ''', (
            'Ananya Menon',
            'ananya@stthomas.edu.in',
            student_pass2
        ))

    conn.commit()


def seed_quotes(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS cnt FROM quotes")

    if cursor.fetchone()['cnt'] > 0:
        return

    # Map category names to IDs
    cursor.execute("SELECT id, name FROM categories")

    cat_map = {
        row['name']: row['id']
        for row in cursor.fetchall()
    }

    # Get admin user ID for attribution
    cursor.execute(
        "SELECT id FROM users WHERE email = 'admin@stthomas.edu.in'"
    )

    admin_id = cursor.fetchone()['id']

    # Get student IDs
    cursor.execute(
        "SELECT id FROM users WHERE email = 'akshai@stthomas.edu.in'"
    )

    akshai_id = cursor.fetchone()['id']

    cursor.execute(
        "SELECT id FROM users WHERE email = 'ananya@stthomas.edu.in'"
    )

    ananya_id = cursor.fetchone()['id']

    initial_quotes = [

        # Motivation
        (
            "The future depends on what you do today.",
            "Mahatma Gandhi",
            "Motivation",
            admin_id,
            'approved',
            True,
            True
        ),

        (
            "It always seems impossible until it's done.",
            "Nelson Mandela",
            "Motivation",
            admin_id,
            'approved',
            True,
            False
        ),

        (
            "Don't watch the clock; do what it does. Keep going.",
            "Sam Levenson",
            "Motivation",
            akshai_id,
            'approved',
            False,
            False
        ),

        (
            "Believe you can and you're halfway there.",
            "Theodore Roosevelt",
            "Motivation",
            ananya_id,
            'approved',
            False,
            False
        ),

        # Study & Education
        (
            "Education is the most powerful weapon which you can use to change the world.",
            "Nelson Mandela",
            "Education",
            admin_id,
            'approved',
            True,
            False
        ),

        (
            "The beautiful thing about learning is that no one can take it away from you.",
            "B.B. King",
            "Study",
            akshai_id,
            'approved',
            False,
            False
        ),

        (
            "Small steps every day add up to big achievements in exam season!",
            "St. Thomas Scholar",
            "Study",
            ananya_id,
            'approved',
            False,
            False
        ),

        # Leadership & Service
        (
            "Service Above Self is not just a motto, it is our way of life.",
            "Rotaract STC",
            "Leadership",
            admin_id,
            'approved',
            True,
            False
        ),

        (
            "Leadership is not about being in charge. It's about taking care of those in your charge.",
            "Simon Sinek",
            "Leadership",
            akshai_id,
            'approved',
            False,
            False
        ),

        # Coding & Technology
        (
            "First, solve the problem. Then, write the code.",
            "John Johnson",
            "Coding",
            akshai_id,
            'approved',
            False,
            False
        ),

        (
            "Code is like humor. When you have to explain it, it's bad.",
            "Cory House",
            "Coding",
            ananya_id,
            'approved',
            False,
            False
        ),

        (
            "Make it work, make it right, make it fast.",
            "Kent Beck",
            "Coding",
            admin_id,
            'approved',
            False,
            False
        ),

        # Life & Personal Growth
        (
            "In the middle of every difficulty lies opportunity.",
            "Albert Einstein",
            "Life",
            admin_id,
            'approved',
            True,
            False
        ),

        (
            "Growth begins at the end of your comfort zone.",
            "Neale Donald Walsch",
            "Personal Growth",
            akshai_id,
            'approved',
            False,
            False
        ),

        (
            "Your time is limited, so don't waste it living someone else's life.",
            "Steve Jobs",
            "Personal Growth",
            ananya_id,
            'approved',
            False,
            False
        ),

        # Friendship & Happiness
        (
            "A real friend is one who walks in when the rest of the world walks out.",
            "Walter Winchell",
            "Friendship",
            akshai_id,
            'approved',
            False,
            False
        ),

        (
            "Happiness is not something readymade. It comes from your own actions.",
            "Dalai Lama",
            "Happiness",
            ananya_id,
            'approved',
            False,
            False
        ),

        # Pending Quote examples
        (
            "Strive for excellence, not perfection. Every day at St. Thomas is a gift!",
            "Rotaract Freshman",
            "Personal Growth",
            akshai_id,
            'pending',
            False,
            False
        ),

        (
            "Late night campus study sessions build lifelong memories.",
            "Anonymous Senior",
            "Study",
            ananya_id,
            'pending',
            False,
            False
        )
    ]

    for (
        text,
        author,
        cat_name,
        sub_id,
        status,
        is_feat,
        is_mom
    ) in initial_quotes:

        cat_id = cat_map.get(cat_name)

        if cat_id:
            cursor.execute('''
                INSERT INTO quotes (
                    text,
                    author,
                    category_id,
                    submitted_by_id,
                    status,
                    is_featured,
                    is_quote_of_the_moment
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                text,
                author,
                cat_id,
                sub_id,
                status,
                is_feat,
                is_mom
            ))

    conn.commit()


if __name__ == '__main__':
    init_db()
