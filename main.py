from flask import Flask, render_template, redirect, url_for, jsonify, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime

dt = datetime.datetime


## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField(label='Blog Content', validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    blog = BlogPost.query.all()
    return render_template("index.html", all_posts=blog)


@app.route("/post/<int:index>")
def show_post(index):
    posts = BlogPost.query.all()
    requested_post = None
    for blog_post in posts:
        if blog_post.id == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if request.method == "POST":
        content = request.form['body'][3:-6]
        now = dt.now()
        title = request.form['title']
        id = len(BlogPost.query.all()) + 1
        author = request.form['author']
        img_url = request.form['img_url']
        subtitle = request.form['subtitle']

        post.id = id
        post.body = content
        post.title = title
        post.author = author
        post.img_url = img_url
        post.subtitle = subtitle

        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template('make_post.html', act='Edit Post', form=edit_form)


@app.route('/new-post', methods=['GET','POST'])
def add_new_posts():
    forms = CreatePostForm()
    if request.method == "POST":
        content = request.form['body'][3:-6]
        now = dt.now()
        date = now.strftime("%B %d, %Y")
        title = request.form['title']
        id = len(BlogPost.query.all())+1
        author = request.form['author']
        img_url = request.form['img_url']
        subtitle = request.form['subtitle']

        new_post = BlogPost(id=id, title=title, date=date, body=content, author=author, img_url=img_url, subtitle=subtitle)
        db.session.add(new_post)
        db.session.commit()

    return render_template("make_post.html", form=forms, act='New Post')

@app.route('/delete/<int:post_id>')
def delete_posts(post_id):
    post = BlogPost.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

if __name__ == "__main__":
    app.run(debug=True)