from flask import Flask, render_template, request, redirect, url_for, session
import data_manager
import util

app = Flask(__name__)
app.secret_key = "GoodMorningVietnam"


@app.route("/list", methods=["GET", "POST"])
def all_questions():
    if request.method == "POST":
        order_by = request.form["order_by"]
        order_direction = request.form["order_direction"]
        return redirect(f"/list?order_by={order_by}&order_direction={order_direction}")
    else:
        mode = request.args.get("order_by")
        order = request.args.get("order_direction")
        list_of_questions = data_manager.get_questions(mode, order)
        for element in list_of_questions:
            element["submission_time"] = (str(element["submission_time"]))[:10]
        tags = data_manager.get_name_tags_of_specific_questions()
        for element in list_of_questions:
            element['email'] = element['email'].split('@')[0]
        return render_template("main_page.html", list=list_of_questions, tags=tags)


@app.route("/")
def main_page():
    mode = "submission_time"
    order = "desc"
    list_of_questions = data_manager.get_questions(mode, order, limit=5)
    for element in list_of_questions:
        element['email'] = element['email'].split('@')[0]
    for element in list_of_questions:
        element["submission_time"] = (str(element["submission_time"]))[:10]
    tags = data_manager.get_name_tags_of_specific_questions()
    return render_template("main_page.html", list=list_of_questions, tags=tags)


@app.route('/searching', methods=['GET', 'POST'])
def search():
    phrase = request.args.get('phrase')
    list_of_questions_with_phrase = data_manager.search_for_phrase_in_questions(phrase)
    tags = data_manager.get_name_tags_of_specific_questions()
    for questions in list_of_questions_with_phrase:
        questions["title"] = util.highlight(phrase, questions["title"])
        questions["message"] = util.highlight(phrase, questions["message"])
    return render_template("main_page.html", list=list_of_questions_with_phrase, tags=tags)


@app.route("/add-question", methods=["POST", "GET"])
def add_question_page():
    if request.method == "POST":
        title = request.form["title"]
        message = request.form["message"]
        file = request.files['image']
        image = util.upload_image(file)
        data_manager.add_question(util.un_inject_text(title), util.un_inject_text(message), image, session['id'])
        return redirect(url_for("main_page"))
    return render_template("add_question.html", question=None)


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    data_manager.delete_question(question_id)
    return redirect(url_for("main_page"))


@app.route("/answer/<answer_id>/delete")
def delete_answer(answer_id):
    answer = data_manager.get_answer_by_id(answer_id)
    data_manager.delete_answer(answer_id)
    return redirect(f"/question/{str(answer['question_id'])}")


@app.route("/answer/<answer_id>/edit", methods=['POST', 'GET'])
def edit_answer(answer_id):
    answer = data_manager.get_answer_by_id(answer_id)
    if request.method == 'POST':
        message = request.form['message']
        file = request.files['image']
        image = util.upload_image(file)
        data_manager.edit_answer(util.un_inject_text(message), image, answer_id)
        return redirect(f"/question/{str(answer['question_id'])}")
    return render_template('answer.html', id=answer_id, edit_form=answer)


@app.route("/question/<question_id>", methods=["GET", 'POST'])
def question_page(question_id):
    tags = data_manager.get_tags_by_quest_id(question_id)
    question = data_manager.get_question_by_id(question_id)
    question["submission_time"] = (str(question["submission_time"]))[:10]
    list_of_answers = data_manager.get_answers(question_id)
    for element in list_of_answers:
        element["submission_time"] = (str(element["submission_time"]))[:10]
    comments_to_question = data_manager.get_comments(question_id)
    for element in comments_to_question:
        element['email'] = element['email'].split('@')[0]
    data_manager.add_views(question_id)
    return render_template("question_page.html", question=question, answers=list_of_answers,
                           comments=comments_to_question,
                           tags=tags)


@app.route("/question/<int:question_id>/edit", methods=['POST', 'GET'])
def edit_question_page(question_id):
    question_form = data_manager.get_question_by_id(question_id)
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        file = request.files['image']
        image = util.upload_image(file)
        data_manager.edit_question(util.un_inject_text(title), util.un_inject_text(message), image, question_id)
        return redirect(f"/question/{question_id}")
    return render_template('add_question.html', id=question_id, question=question_form)


@app.route('/question/<string:question_id>/new-answer', methods=['POST', 'GET'])
def answer_page(question_id):
    if request.method == 'POST':
        message = request.form['message']
        file = request.files['image']
        image = util.upload_image(file)
        data_manager.add_answer(question_id, util.un_inject_text(message), image, session['id'])
        return redirect(f"/question/{str(question_id)}")
    return render_template('answer.html', id=None, question_id=question_id)


@app.route('/question/<string:question_id>/vote_up', methods=['POST', 'GET'])
@app.route('/question/<string:question_id>/vote_down', methods=['POST', 'GET'])
def vote_on_question(question_id):
    rule = request.url_rule
    data_manager.voting('question', rule, question_id)
    return redirect(f"/question/{question_id}")


@app.route('/answers/<answer_id>/vote_up', methods=['POST', 'GET'])
@app.route('/answers/<answer_id>/vote_down', methods=['POST', 'GET'])
def vote_on_answers(answer_id):
    answer = data_manager.get_answer_by_id(answer_id)
    rule = request.url_rule
    data_manager.voting('answer', rule, answer_id)
    return redirect(f"/question/{answer['question_id']}")


@app.route('/answer/<string:answer_id>/new_comment', methods=['POST', 'GET'])
def new_comment_answer(answer_id):
    if request.method == 'POST':
        message = request.form['message']
        data_manager.add_new_comment_answer(answer_id, message, session['id'])
        answer = data_manager.get_answer_by_id(answer_id)
        return redirect(f"/question/{str(answer['question_id'])}")
    return render_template('comments_form.html', answer_id=answer_id, question_id=None, edit=False)


@app.route('/question/<string:question_id>/new_comment', methods=['POST', 'GET'])
def new_comment_question(question_id):
    if request.method == 'POST':
        message = request.form['message']
        data_manager.add_new_comment_question(question_id, message, session['id'])
        return redirect(f"/question/{str(question_id)}")
    return render_template('comments_form.html', question_id=question_id, answer_id=None, edit=False)


@app.route('/comments/<comment_id>/delete')
def delete_comments(comment_id):
    data_manager.delete_comments_by_id(comment_id)
    return redirect('/')


@app.route('/<question_id>/create-tag', methods=["POST", "GET"])
def create_tag(question_id):
    if request.method == "POST":
        tag_name = request.form["tag"]
        data_manager.create_tag(tag_name, question_id)
        return redirect("/")
    return render_template('create_new_tag.html', question_id=question_id)


@app.route('/question/<question_id>/new-tag', methods=["POST", "GET"])
def add_tags(question_id):
    tags = data_manager.select_tag()
    if request.method == "POST":
        tag_id = request.form["add-tag"]
        data_manager.connect_tag_with_question(tag_id, question_id)
        return redirect(f"/question/{question_id}")
    return render_template('add_tags.html', tags=tags, question_id=question_id)


@app.route('/question/<question_id>/tag/<tag_id>/delete')
def delete_tags(question_id, tag_id):
    data_manager.delete_tag(question_id, tag_id)
    return redirect(f"/question/{question_id}")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        if not data_manager.check_if_user_in_database(request.form['email']):
            email = request.form['email']
            password = util.hash_password(request.form['password'])
            data_manager.save_user(email, password)
            return redirect('/')
        else:
            return render_template('register_page.html', info="Sorry but that mail is already in use")
    return render_template('register_page.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if data_manager.check_if_user_in_database(request.form['email']):
            password = request.form['password']
            saved_password = data_manager.get_password_by_email(request.form['email'])['password']
            if util.verify_password(password, saved_password):
                user = request.form['email']
                username = user.split('@')
                user_id = data_manager.find_user_id_by_email(user)
                session['id'] = user_id['id']
                session['username'] = username[0]
                session['user'] = user
                return redirect('/')
            else:
                return render_template('login_page.html', info="Your login or password is incorrect")
        else:
            return render_template('login_page.html', info="user with such e-mail does not exist")
    return render_template('login_page.html')


@app.route('/comments/<comment_id>/edit', methods=['POST', 'GET'])
def edit_comments_page(comment_id):
    edit_form = data_manager.get_comment_by_id(comment_id)
    if request.method == 'POST':
        message = request.form['message']
        data_manager.edit_comment(comment_id, message)
        return redirect(request.url)
    return render_template('comments_form.html', edit_form=edit_form, edit=True, comment_id=comment_id)


@app.route('/user/<user_id>', methods=["POST", "GET"])
def users_page(user_id):
    logged_user = data_manager.find_user(user_id)
    num_of_questions = data_manager.number_of_questions(user_id)
    num_of_answers = data_manager.number_of_answers(user_id)
    num_of_comments = data_manager.number_of_comments(user_id)
    questions_posted_by_user = data_manager.get_questions_by_user_id(user_id)
    answers_posted_by_user = data_manager.get_answers_by_user_id(user_id)
    comments_posted_by_user = data_manager.get_comments_by_user_id(user_id)
    return render_template('users_page.html', user=logged_user,
                           num_questions=num_of_questions,
                           num_answers=num_of_answers,
                           num_comments=num_of_comments,
                           questions=questions_posted_by_user,
                           answers=answers_posted_by_user,
                           comments=comments_posted_by_user)


@app.route("/logout")
def logout():
    session.pop("id", None)
    session.pop("user", None)
    return redirect('/')


@app.route("/users")
def print_users_list():
    users_form = data_manager.get_list_of_users()
    for element in users_form:
        num_of_questions = data_manager.number_of_questions(element['id'])
        num_of_answers = data_manager.number_of_answers(element['id'])
        num_of_comments = data_manager.number_of_comments(element['id'])
        element['num_of_questions'] = num_of_questions
        element['num_of_answers'] = num_of_answers
        element['num_of_comments'] = num_of_comments
    return render_template('users_list.html', users_form=users_form)


@app.route("/print_tags")
def print_tags():
    tag_table = data_manager.get_list_of_tags()
    return render_template('tags_pages.html', tag_table=tag_table)


@app.route("/acceptance/<id>/<question_id>")
def accept(id, question_id):
    data_manager.accepting_the_answer(id)
    return redirect(f"/question/{question_id}")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
