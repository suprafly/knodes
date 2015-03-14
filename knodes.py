from flask import Flask, request, render_template
import os
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
    print knode
    return render_template('edit.html', title=knode[0], text=knode[1], tags=knode[2], question=knode[3], answer=knode[4], comments=knode[5], knode_id=knode_id)

if __name__ == '__main__':
    DB.create_database_if_needed()
    app.run(debug=DEBUG_MODE)
