from flask import Flask, request, render_template
import lxml.etree as ET
import uuid
import os
import datetime


# Configuration
DEBUG_MODE = True
DB_ROOT = "db/"
TAGS_DIR = DB_ROOT + "tags/"
NODES_DIR = DB_ROOT + "nodes/"
TAGFILE = TAGS_DIR + "tagfile.txt"

# Helper functions
get_tag_xml_file = lambda filename: TAGS_DIR + filename + ".xml"
get_node_xml_file = lambda filename: NODES_DIR + filename + ".xml"


app = Flask(__name__)

@app.route('/')
def index():
    tags_with_knodes = get_knodes_for_tags(get_all_tags())
    return render_template("layout.html", tags_with_knodes=tags_with_knodes)

@app.route('/', methods=['POST'])
def index_post():
    if 'update' in request.form:
        knode_id = request.form['knode_id']
        title = request.form['title']
        text = request.form['text']
        tag_text = (request.form['tags']).replace(",", "")
        tags = sanitize_tags(tag_text.split(" "))

        #! Don't let them enter 0 tags, or else the knode disappears!
        if (tags.__len__() < 1):
            knode = get_knode(knode_id)
            return render_template('edit.html', title=knode[0], text=knode[1], tags=knode[2], knode_id=knode_id)

        update_knode(knode_id, title, text, tags)
    else:
        text = request.form['knode']
        fields = text.split('::')
        if fields.__len__() > 1:
            title = fields[0]
            text = fields[1]
        else:
            title = ""
            text = text.lstrip()

        tag_text = (request.form['tags']).replace(",", "")
        tags = sanitize_tags(tag_text.split(" "))

        knode_id = create_knode(title, text, tags)
        save_tags(tags, knode_id)

    all_tags = get_all_tags()
    tags_with_knodes = get_knodes_for_tags(all_tags)
    return render_template("layout.html", tags_with_knodes=tags_with_knodes)


@app.route('/edit/<knode_id>')
def edit(knode_id=None):
    knode = get_knode(knode_id)
    return render_template('edit.html', title=knode[0], text=knode[1], tags=knode[2], knode_id=knode_id)


def update_knode(knode_id, new_title, new_text, new_tags):
    knode_file = get_node_xml_file(knode_id)
    if os.path.isfile(knode_file):
        knode_xml = ET.parse(knode_file)
        knode_root = knode_xml.getroot()

        if knode_root.get('title') != new_title:
            knode_root.set('title', new_title) 

        for knode_text in knode_root.findall('text'):
            if knode_text.text != new_text:
                knode_text.text = new_text

        old_tags = []
        for tag in knode_root.findall('tag'):
            old_tags.append(tag.text)
            #! Check if tags have been removed
            if tag.text not in new_tags:
                knode_root.remove(tag)
                #! Remove from tag_file as well
                tag_file = get_tag_xml_file(tag.text)
                tag_xml = ET.parse(tag_file)
                tag_root = tag_xml.getroot()
                for tag_knode_id in tag_root.findall('knode_id'):
                    if tag_knode_id.text == knode_id:
                        tag_root.remove(tag_knode_id)                        
                tag_xml.write(tag_file, pretty_print=True)

        #! Check if new tags have been added
        for new_tag in new_tags:
            if new_tag not in old_tags:
                tag = ET.SubElement(knode_root, 'tag')
                tag.text = new_tag
                #! Add to tag_file as well
                tag_file = get_tag_xml_file(new_tag)
                if os.path.isfile(tag_file):
                    tag_xml = ET.parse(tag_file)
                    tag_root = tag_xml.getroot()
                    tag_knode_id = ET.SubElement(tag_root, 'knode_id')
                    tag_knode_id.text = knode_id
                    tag_xml.write(tag_file, pretty_print=True)
                else: 
                    tag_xml = ET.Element('tag')
                    tag_xml.set('title', tag.text)
                    tag_knode_id = ET.SubElement(tag_xml, 'knode_id')
                    tag_knode_id.text = knode_id
                    tree = ET.ElementTree(tag_xml)    
                    tree.write(tag_file, pretty_print=True)
                    write_tag_to_tagfile(tag.text)   

        knode_xml.write(knode_file, pretty_print=True)

def write_tag_to_tagfile(tag):
    tagfile_f = open(TAGFILE, 'a')
    tagfile_f.write(tag + '\n')
    tagfile_f.close()

def get_knode(knode_id):
    knode_file = get_node_xml_file(knode_id)
    if os.path.isfile(knode_file):
        knode_xml = ET.parse(knode_file)
        knode_root = knode_xml.getroot()
        knode_title = knode_root.get('title')
        for text in knode_root.findall('text'):
            knode_text = text.text
        tags = ""
        for tag in knode_root.findall('tag'):
            tags = tags + " " + tag.text

        return [knode_title, knode_text, tags.lstrip()]
    else:
        return None

def get_all_tags():
    if os.path.isfile(TAGFILE):
        tagfile_f = open(TAGFILE, 'r')
        all_tags = tagfile_f.readlines()
        cleaned_tags = []
        for tag in all_tags:
            cleaned_tag = tag.split('\n')[0]
            cleaned_tags.append(cleaned_tag)
        return cleaned_tags
    else:
        return None

def get_knodes_for_tags(all_tags):
    if not all_tags:
        return None
    tags_with_knodes = []
    for tag in all_tags:
        filename = get_tag_xml_file(tag)
        tag_xml = ET.parse(filename)
        tag_root = tag_xml.getroot()
        knodes = []
        for knode_id in tag_root.findall('knode_id'):
            knode_file = get_node_xml_file(knode_id.text)
            knode_xml = ET.parse(knode_file)
            knode_root = knode_xml.getroot()
            knode_title = knode_root.get('title')
            for text in knode_root.findall('text'):
                knode_text = text.text
                knodes.append([knode_id.text, knode_title, knode_text])
        tags_with_knodes.append([tag, knodes])
    return tags_with_knodes

def sanitize_tags(tags):
    new_tags = []
    for tag in tags:
        if tag != "":
            new_tags.append(tag.lstrip())
    return new_tags

def create_knode(title, text, tags):
    knode_xml = ET.Element('knode')

    if title:
        knode_xml.set('title', title.lstrip())

    u_id = str(uuid.uuid4())
    knode_xml.set('knode_id', u_id)
      
    time_created =  datetime.datetime.now().strftime("%b %d, %Y %H:%M:%S")
    knode_created = ET.SubElement(knode_xml, 'created')
    knode_created.text = time_created
    knode_last_updated = ET.SubElement(knode_xml, 'last_updated')
    knode_last_updated.text = time_created

    #! And other data sanitization
    knode_text = ET.SubElement(knode_xml, 'text')
    knode_text.text = text.lstrip()

    for tag_text in tags:
        tag = ET.SubElement(knode_xml, 'tag')
        tag.text = tag_text

    tree = ET.ElementTree(knode_xml)
    filename = get_node_xml_file(u_id)
    tree.write(filename, pretty_print=True)
    return u_id


def save_tags(tags, knode_id):
    for tag in tags:
        tag_text = tag
        filename = get_tag_xml_file(tag_text)

        new_tags = []
        if not os.path.isfile(filename):
            tag_xml = ET.Element('tag')
            tag_xml.set('title', tag_text)
            tag_knode_id = ET.SubElement(tag_xml, 'knode_id')
            tag_knode_id.text = knode_id
            tree = ET.ElementTree(tag_xml)    
            tree.write(filename, pretty_print=True)
            new_tags.append(tag_text)
        else:
            tag_xml = ET.parse(filename)
            root = tag_xml.getroot()
            tag_knode_id = ET.SubElement(root, 'knode_id')
            tag_knode_id.text = knode_id
            tag_xml.write(filename, pretty_print=True)

        tagfile_f = open(TAGFILE, 'a')
        for new_tag in new_tags:
            tagfile_f.write(new_tag + '\n')
        tagfile_f.close()

if __name__ == '__main__':
    app.run(debug=DEBUG_MODE)
