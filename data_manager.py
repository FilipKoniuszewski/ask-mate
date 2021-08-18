import connection


@connection.connection_handler
def get_questions(cursor, order, directions, limit=0):
    query = """
        SELECT id,submission_time, view_number, vote_number, title, message, image
        FROM question
    """
    if limit != 0:
        query += f""" ORDER BY {order} {directions}
        LIMIT {limit}"""
    elif order:
        query += f"ORDER BY {order} {directions}"

    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_question_by_id(cursor, question_id):
    query = f"""
        SELECT id,submission_time, view_number,  vote_number, title, message, image
        FROM question
        WHERE id = {question_id}
    """
    cursor.execute(query)
    return cursor.fetchone()


@connection.connection_handler
def add_question(cursor, title, message, image):
    query = f"""
        INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
        VALUES (NOW(), 0, 0, '{title}', '{message}',
        """
    if image == "":
        query += "null)"
    else:
        query += f"'{image}')"

    cursor.execute(query)


@connection.connection_handler
def delete_question(cursor, question_id):
    query = f"""
            DELETE FROM comment
            WHERE question_id = {question_id};
            DELETE FROM answer
            WHERE question_id = {question_id};
            DELETE FROM question_tag
            WHERE question_id = {question_id};
            DELETE FROM question
            WHERE id = {question_id}
        """
    cursor.execute(query)


@connection.connection_handler
def edit_question(cursor, title, message, image, question_id):
    query = f"""
        UPDATE question SET
        submission_time = NOW(),
        title = '{title}',
        message = '{message}'
    """
    if image != "":
        query += f",image = '{image}'"
    else:
        query += f",image = null"
    query += f" WHERE id = {question_id}"
    cursor.execute(query)


@connection.connection_handler
def get_answers(cursor, question_id):
    query = f"""
            SELECT id,submission_time, vote_number, question_id, message, image
            FROM answer
            WHERE question_id = {question_id}
        """
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_answer_by_id(cursor, answer_id):
    query = f"""
        SELECT id,submission_time, vote_number, question_id, message, image
        FROM answer
        WHERE id = {answer_id}
    """
    cursor.execute(query)
    return cursor.fetchone()


@connection.connection_handler
def add_answer(cursor, question_id, message, image):
    query = f"""
        INSERT INTO answer (submission_time, vote_number, question_id, message, image)
        VALUES (NOW(), 0, {question_id}, '{message}',"""
    if image == "":
        query += "null)"
    else:
        query += f"'{image}')"
    cursor.execute(query)


@connection.connection_handler
def delete_answer(cursor, answer_id):
    query = f"""
            DELETE FROM comment   
            WHERE answer_id = {answer_id};
            DELETE FROM answer 
            WHERE id = {answer_id};
        """
    cursor.execute(query)


@connection.connection_handler
def edit_answer(cursor, message, image, answer_id):
    query = f"""
        UPDATE answer SET
        submission_time = NOW(),
        message = '{message}'
    """
    if image != "":
        query += f",image = '{image}'"
    query += f" WHERE id = {answer_id}"
    cursor.execute(query)


@connection.connection_handler
def delete_comments_by_id(cursor, comment_id):
    query = f"""
            DELETE FROM comment 
            WHERE id = {comment_id}
            """
    cursor.execute(query)


@connection.connection_handler
def add_new_comment_answer(cursor, answer_id, message):
    query = f"""  
        INSERT INTO comment (submission_time,answer_id,message,edited_count)
        VALUES (NOW(), {answer_id}, '{message}',0)
        """
    cursor.execute(query)


@connection.connection_handler
def add_new_comment_question(cursor, question_id, message):
    query = f""" 
        INSERT INTO comment (submission_time,question_id,message,edited_count)
        VALUES (NOW(),{question_id},'{message}',0) 
    """
    cursor.execute(query)


@connection.connection_handler
def voting(cursor, table, rule, element_id):
    query = f"""
    UPDATE {table} SET
    """
    if 'vote_up' in rule.rule:
        query += "vote_number = vote_number + 1"
    else:
        query += "vote_number = vote_number - 1"
    query += f"WHERE id = {element_id}"
    cursor.execute(query)


@connection.connection_handler
def edit_comment(cursor, comment_id, message):
    query = f"""
                UPDATE comment
                SET message = {message},submission_time = NOW(), edited_count = edited_count +1
                WHERE id = {comment_id}
            """
    cursor.execute(query)


@connection.connection_handler
def get_comment_by_id(cursor, comment_id):
    query = f"""
                SELECT * 
                FROM comment
                WHERE id = {comment_id} 
            """
    cursor.execute(query)


@connection.connection_handler
def add_views(cursor, question_id):
    query = f"""
                UPDATE question
                SET view_number = view_number +1
                WHERE id = {question_id}
            """
    cursor.execute(query)


@connection.connection_handler
def get_comments(cursor, question_id):
    query = f"""
        SELECT comment.*, answer.question_id as answer_question_id
        FROM comment LEFT JOIN answer ON comment.answer_id = answer.id
        WHERE comment.question_id = {question_id} or answer.question_id = {question_id}
        """
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def search_for_phrase_in_questions(cursor, phrase):
    query = f"""
                SELECT DISTINCT question.*
                FROM question LEFT JOIN answer ON question.id = answer.question_id
                WHERE LOWER(answer.message) LIKE LOWER('%{phrase}%') or 
                LOWER(question.title) LIKE LOWER('%{phrase}%') or LOWER(question.message) LIKE LOWER('%{phrase}%')
            """
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def create_tag(cursor, tag_name, question_id):
    query = f"""
                INSERT INTO tag(name)
                VALUES ('{tag_name}');
            """
    tag_id = select_id_tag_by_name(tag_name)
    if tag_id:
        connect_tag_with_question(tag_id["id"], question_id)
    else:
        cursor.execute(query)
        new_tag_id = select_id_tag_by_name(tag_name)
        connect_tag_with_question(new_tag_id["id"], question_id)


@connection.connection_handler
def connect_tag_with_question(cursor, tag_id, question_id):
    query = f"""
                INSERT INTO question_tag(question_id, tag_id)
                VALUES ({question_id}, {tag_id})    
            """
    cursor.execute(query)


@connection.connection_handler
def delete_tag(cursor, question_id, tag_id):
    query = f"""
                DELETE FROM question_tag
                WHERE tag_id = {tag_id} AND question_id = {question_id}
            """
    cursor.execute(query)


@connection.connection_handler
def select_tag(cursor):
    query = f"""
                SELECT *
                FROM tag
            """
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def select_tag_by_id(cursor, tag_id):
    query = f"""
                SELECT *
                FROM tag
                WHERE id={tag_id}
            """
    cursor.execute(query)


@connection.connection_handler
def select_id_tag_by_name(cursor, name):
    query = f"""
                SELECT id FROM tag WHERE name = '{name}'
            """
    cursor.execute(query)
    return cursor.fetchone()


@connection.connection_handler
def get_name_tags_of_specific_questions(cursor):
    query = """ SELECT q.id, ARRAY_AGG(t.name) tags
                FROM question_tag qt
                LEFT JOIN tag t ON qt.tag_id = t.id
                LEFT JOIN question q ON qt.question_id = q.id
                GROUP BY qt.question_id, q.id """
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_tags_by_quest_id(cursor, question_id):
    query = f"""
            SELECT * FROM tag t
            LEFT JOIN question_tag qt ON t.id = qt.tag_id
            WHERE qt.question_id = {question_id} """
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def check_if_user_in_database(cursor, email):
    query = f""" SELECT * 
                FROM users 
                WHERE email = '{email}'
    
            """
    cursor.execute(query)
    result = cursor.fetchone()
    return result


@connection.connection_handler
def save_user(cursor, email, password):
    query = f"""INSERT INTO users(email,password)
                VALUES  ('{email}', '{password}')  
    
            """
    return cursor.execute(query)


@connection.connection_handler
def check_password(cursor, email, password):
    query = f"""SELECT *
                FROM users
                WHERE email = '{email}' AND password = '{password}'
            """
    cursor.execute(query)
    result = cursor.fetchone()
    return result


@connection.connection_handler
def find_user_id_by_email(cursor, email):
    query = f"""SELECT id
                FROM users
                WHERE email = '{email}'
            """
    cursor.execute(query)
    return cursor.fetchone()


@connection.connection_handler
def find_user(cursor, user_id):
    query = f"""
                SELECT * FROM users
                WHERE users.id = {user_id}
            """
    cursor.execute(query)
    return cursor.fetchall()




