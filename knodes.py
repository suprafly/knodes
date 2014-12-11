from flask import Flask, request, render_template
import lxml.etree as ET
import uuid

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("layout.html")

@app.route('/', methods=['POST'])
def index_post():
    text = request.form['knode']
    fields = text.split(':')
    name = fields[0]
    text = fields[1]
    tag_text = request.form['tags']
    tags = tag_text.split(",")
    knode_id = create_knode(name, text, tags)
    save_tags(tags, knode_id)
    return render_template("layout.html")   


def create_knode(name, text, tags):
    knode_xml = ET.Element('knode')

    #! And other data sanitization
    knode_name = ET.SubElement(knode_xml, 'name')
    knode_name.text = name.lstrip()

    knode_text = ET.SubElement(knode_xml, 'text')
    knode_text.text = text.lstrip()

    knode_created = ET.SubElement(knode_xml, 'created')
    knode_created.text = text.lstrip()    

    knode_last_updated = ET.SubElement(knode_xml, 'last_updated')
    knode_last_updated.text = text.lstrip()    


    for tag_text in tags:
        tag = ET.SubElement(knode_xml, 'tag')
        tag.text = tag_text.lstrip()
  
    u_id = str(uuid.uuid4())
    knode_id = ET.SubElement(knode_xml, 'id')
    knode_id.text = str(u_id)

    tree = ET.ElementTree(knode_xml)
    filename = "nodes/%s.xml" % u_id
    tree.write(filename, pretty_print=True)
    return u_id


def save_tags(tags, knode_id):
    for tag in tags:
        tag_text = tag.lstrip()
        filename = "tags/%s.xml" % tag_text
        # if Exists != open(filename, 'r'):
        if True:
            # if tag file doesnt exist
            tag_xml = ET.Element('tag')
            
            tag_name = ET.SubElement(tag_xml, 'name')
            tag_name.text = tag_text
            
            tag_knode_id = ET.SubElement(tag_xml, 'knode_id')
            tag_knode_id.text = knode_id

            tree = ET.ElementTree(tag_xml)    
            tree.write(filename, pretty_print=True)

            

if __name__ == '__main__':
    app.run()
