import connection
from typing import List, Dict
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


@connection.connection_handler
def get_questions(cursor, order, directions, limit=0):
    query = f"""
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
            WHERE comment_id = {comment_id}
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
                SET message = {message},submission_time = NOW(),edited_number = edited_number +1
                WHERE comment_id = {comment_id}
            """
    cursor.execute(query)


@connection.connection_handler
def get_comment_by_id(cursor, comment_id):
    query = f"""
                SELECT * 
                FROM comment
                WHERE comment_id = {comment_id} 
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
def create_tag(cursor, name):
    query = f"""
                INSERT INTO tag(name)
                VALUES ('{name}')
            """
    cursor.execute(query)


@connection.connection_handler
def connect_tag_with_question(cursor, tag_id, question_id):
    query = f"""
                INSERT INTO question_tag(question_id, tag_id)
                VALUES ({question_id}, {tag_id})    
            """
    cursor.execute(query)


@connection.connection_handler
def delete_tag(cursor, tag_id):
    query = f"""
                DELETE FROM tag 
                WHERE id = {tag_id};
                DELETE FROM question_tag
                WHERE tag_id = {tag_id}
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
                WHERE tag_id={tag_id}
            """
    cursor.execute(query)


@connection.connection_handler
def get_name_tags_of_specific_questions(cursor):
    query = """ SELECT q.id, ARRAY_AGG(t.name) tags
                FROM question_tag qt
                LEFT JOIN tag t ON qt.tag_id = t.id
                LEFT JOIN question q ON qt.question_id = q.id
                GROUP BY qt.question_id, q.id """
    cursor.execute(query)
    return cursor.fetchall()




