from flask import Flask, request, render_template
import os
import random

import database_engine as DB
from config import DEBUG_MODE

# Helper functions
remove_commas = lambda string: string.replace(",", " ")
has_one_or_more_tags = lambda tags: tags.__len__() < 1
has_knowledge_node = lambda text: text.lstrip().__len__() < 1
create_tag_list = lambda tag_text: DB.sanitize_tags(tag_text.split(" "))


app = Flask(__name__)

@app.route('/')
def index():
    tags_with_knodes = DB.get_knodes_for_tags(DB.get_all_tags())
    return render_template("layout.html", tags_with_knodes=tags_with_knodes)

@app.route('/', methods=['POST'])
def index_post():
    if 'update_button' in request.form:
        knode_id = request.form['knode_id']
        title = request.form['title']
        text = request.form['text']
        tags = create_tag_list(remove_commas(request.form['tags']))
        if has_one_or_more_tags(tags) or has_knowledge_node(text):
            knode = DB.get_knode(knode_id)
            return render_template('edit.html', title=knode[0], text=knode[1], tags=knode[2], question=knode[3], answer=knode[4], comments=knode[5], knode_id=knode_id)
        else:
            DB.update_knode(knode_id, title, text, tags, request.form['question'], request.form['answer'], request.form['comments'])

    elif 'delete_button' in request.form:
        knode_id = request.form['knode_id']
        DB.remove_knodefile(DB.get_node_xml_file(knode_id))
        tags = create_tag_list(remove_commas(request.form['tags']))
        DB.remove_knode_id_from_tagfiles(knode_id, tags)
    else:
        text = request.form['knode']
        fields = text.split('::')
        if fields.__len__() > 1:
            title = fields[0]
            text = fields[1]
        else:
            title = ""
            text = text.lstrip()
        tags = create_tag_list(remove_commas(request.form['tags']))
        knode_id = DB.create_knode(title, text, tags)
        DB.save_tags(tags, knode_id)
    all_tags = DB.get_all_tags()
    tags_with_knodes = DB.get_knodes_for_tags(all_tags)
    return render_template("layout.html", tags_with_knodes=tags_with_knodes)

@app.route('/edit/<knode_id>')
def edit(knode_id=None):
    knode = DB.get_knode(knode_id)
    return render_template('edit.html', title=knode[0], text=knode[1], tags=knode[2], question=knode[3], answer=knode[4], comments=knode[5], knode_id=knode_id)

@app.route('/quiz', methods=['POST'])
def quiz(quiz_knodes=None):
    #! Should try to avoid reordering knode object
    #! Come up with a standard object that contains all information
    #! Use different funcs in DB to return types of knodes for different purposes
    tags_with_knodes = DB.get_knodes_for_tags(DB.get_all_tags())
    quiz_tags = request.form.getlist("quiz_tag")
    quiz_knodes = DB.get_knode_list(quiz_tags)

    #! Remove knodes w/o questions
    all_quiz_knodes = quiz_knodes
    for knode in all_quiz_knodes:
        print knode
        if knode[3] == None:
            quiz_knodes.remove(knode)

    total_questions = quiz_knodes.__len__()
    knode_id_list = request.form.getlist("knode_id")
    if knode_id_list:
        quiz_knodes = []
        if knode_id_list[0] == 'END':
            return render_template("layout.html", tags_with_knodes=tags_with_knodes)
        for knode_id in knode_id_list:
            if knode_id != "END":
                next_knode = DB.get_knode(knode_id)
                next_knode.pop(2)
                next_knode.insert(0, knode_id)
                quiz_knodes.append(next_knode)
    next_question_knode = random.choice(quiz_knodes)
    quiz_knodes.remove(next_question_knode)
    question_number = total_questions - quiz_knodes.__len__()
    return render_template("quiz.html", quiz_tags=quiz_tags, next_question_knode=next_question_knode, question_number=question_number, total_questions=total_questions, quiz_knodes=quiz_knodes, tags_with_knodes=tags_with_knodes)

if __name__ == '__main__':
    DB.create_database_if_needed()
    app.run(debug=DEBUG_MODE)
