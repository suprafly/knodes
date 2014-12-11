from flask import Flask, request, render_template
import lxml.etree as ET
import uuid
import os
import datetime

app = Flask(__name__)


@app.route('/')
def index():
    all_tags = get_all_tags()
    tags_with_knodes = get_knodes_for_tags(all_tags)
    return render_template("layout.html", tags_with_knodes=tags_with_knodes)

@app.route('/', methods=['POST'])
def index_post():
    text = request.form['knode']
    fields = text.split(':')
    name = fields[0]
    text = fields[1]
    tag_text = request.form['tags']
    tags = sanitize_tags(tag_text.split(","))

    knode_id = create_knode(name, text, tags)
    save_tags(tags, knode_id)

    all_tags = get_all_tags()
    tags_with_knodes = get_knodes_for_tags(all_tags)
    return render_template("layout.html", tags_with_knodes=tags_with_knodes)

def get_all_tags():
    if os.path.isfile('tags/tagfile.txt'):
        tagfile = open('tags/tagfile.txt', 'r')
        all_tags = tagfile.readlines()
        cleaned_tags = []
        for tag in all_tags:
            cleaned_tag = tag.split('\n')[0]
            cleaned_tags.append(cleaned_tag)
        return cleaned_tags
    else:
        return None

def get_knodes_for_tags(all_tags):
    tags_with_knodes = []
    for tag in all_tags:
        filename = 'tags/%s.xml' % tag
        tag_xml = ET.parse(filename)
        tag_root = tag_xml.getroot()
        knodes = []
        for knode_id in tag_root.findall('knode_id'):
            knode_file = 'nodes/%s.xml' % knode_id.text
            knode_xml = ET.parse(knode_file)
            knode_root = knode_xml.getroot()
            knode_name = knode_root.get('name')
            for text in knode_root.findall('text'):
                knode_text = text.text
                knodes.append([knode_name, knode_text])
        tags_with_knodes.append([tag, knodes])
    return tags_with_knodes

def sanitize_tags(tags):
    new_tags = []
    for tag in tags:
        new_tags.append(tag.lstrip())
    return new_tags

def create_knode(name, text, tags):
    knode_xml = ET.Element('knode')

    if name:
        knode_xml.set('name', name.lstrip())

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
    filename = "nodes/%s.xml" % u_id
    tree.write(filename, pretty_print=True)
    return u_id


def save_tags(tags, knode_id):
    for tag in tags:
        tag_text = tag
        filename = "tags/%s.xml" % tag_text

        new_tags = []
        if not os.path.isfile(filename):
            tag_xml = ET.Element('tag')
            tag_xml.set('name', tag_text)
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

        tagfile = open('tags/tagfile.txt', 'a')
        for new_tag in new_tags:
            tagfile.write(new_tag + '\n')
        tagfile.close()

if __name__ == '__main__':
    app.run(debug=True)
