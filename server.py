from flask import Flask, render_template, request, redirect, url_for
import data_manager
import util

app = Flask(__name__)


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
        return render_template("questions_list.html", list=list_of_questions, tags=tags)


@app.route("/")
def main_page():
    mode = "submission_time"
    order = "desc"
    list_of_questions = data_manager.get_questions(mode, order, limit=5)
    for element in list_of_questions:
        element["submission_time"] = (str(element["submission_time"]))[:10]
    tags = data_manager.get_name_tags_of_specific_questions()
    return render_template("questions_list.html", list=list_of_questions, tags=tags)


@app.route('/searching', methods=['GET', 'POST'])
def search():
    phrase = request.args.get('phrase')
    list_of_questions_with_phrase = data_manager.search_for_phrase_in_questions(phrase)
    for questions in list_of_questions_with_phrase:
        questions["title"] = util.highlight(phrase, questions["title"])
        questions["message"] = util.highlight(phrase, questions["message"])
    return render_template("questions_list.html", list=list_of_questions_with_phrase)


@app.route("/add-question", methods=["POST", "GET"])
def add_question_page():
    if request.method == "POST":
        title = request.form["title"]
        message = request.form["message"]
        file = request.files['image']
        image = util.upload_image(file)
        data_manager.add_question(util.un_inject_text(title), util.un_inject_text(message), image)
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
    data_manager.add_views(question_id)
    return render_template("question.html", question=question, answers=list_of_answers, comments=comments_to_question,
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
    return render_template('add_question.html', id=id, question=question_form)


@app.route('/question/<string:question_id>/new-answer', methods=['POST', 'GET'])
def answer_page(question_id):
    if request.method == 'POST':
        message = request.form['message']
        file = request.files['image']
        image = util.upload_image(file)
        data_manager.add_answer(question_id, util.un_inject_text(message), image)
        return redirect(f"/question/{str(question_id)}")
    return render_template('answer.html', id=None, question_id=question_id)


@app.route('/question/<string:question_id>/vote_up', methods=['POST', 'GET'])
@app.route('/question/<string:question_id>/vote_down', methods=['POST', 'GET'])
def vote_on_question(question_id):
    rule = request.url_rule
    data_manager.voting('question', rule, question_id)
    return redirect(f"/question/{question_id}")


@app.route('/answers/<string:answer_id>/vote_up', methods=['POST', 'GET'])
@app.route('/answers/<string:answer_id>/vote_down', methods=['POST', 'GET'])
def vote_on_answers(answer_id):
    answer = data_manager.get_answer_by_id(answer_id)
    rule = request.url_rule
    data_manager.voting('answer', rule, answer_id)
    return redirect(f"/question/{answer['question_id']}")


@app.route('/answer/<string:answer_id>/new_comment', methods=['POST', 'GET'])
def new_comment_answer(answer_id):
    if request.method == 'POST':
        message = request.form['message']
        data_manager.add_new_comment_answer(answer_id, message)
        answer = data_manager.get_answer_by_id(answer_id)
        return redirect(f"/question/{str(answer['question_id'])}")
    return render_template('comments_form.html', answer_id=answer_id, question_id=None)


@app.route('/question/<string:question_id>/new_comment', methods=['POST', 'GET'])
def new_comment_question(question_id):
    if request.method == 'POST':
        message = request.form['message']
        data_manager.add_new_comment_question(question_id, message)
        return redirect(f"/question/{str(question_id)}")
    return render_template('comments_form.html', question_id=question_id, answer_id=None)


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


def edit_comments_page(comment_id):
    edit_form = data_manager.get_comment_by_id(comment_id)
    if request.method == 'POST':
        message = request.form['message']
        data_manager.edit_comment(comment_id, message)
        return redirect('/')
    return render_template('add_question.html', edit_form=edit_form)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
