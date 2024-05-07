from flask import Blueprint, jsonify, request, current_app, render_template, redirect, url_for
from blogwise.models import Article

bp = Blueprint('home', __name__)

@bp.get('/')
def index():
    articles = Article.filter_by(is_featured=True)
    return render_template('index.html', articles=articles)

@bp.get('/articles/<int:article_id>')
def get_article(article_id):
    article = Article.get_by_id(article_id)
    return render_template('articles/detail.html', article=article)

@bp.get('/articles/all')
def get_all_articles():
    articles = Article.get_all()
    return render_template('articles/index.html', articles=articles)

@bp.get('/articles/new')
def create_new_article():
    return render_template('articles/new.html')

@bp.post('/articles')
def create_article():
    article = Article.create(**request.form)
    return redirect(url_for('home.get_article', article_id=article.row_id))

@bp.route('/articles/<int:article_id>', methods=['POST', 'PATCH'])
def update_article(article_id):
    article = Article.update(article_id, request.form)
    return render_template('articles/detail.html', article=article)

@bp.get('/articles/<int:article_id>/edit')
def edit_article(article_id):
    article = Article.get_by_id(article_id)
    return render_template('articles/edit.html', article=article)


@bp.get('/api/v1/articles')
def all_articles():
    articles = Article.get_all()
    return jsonify([article.to_json() for article in articles]), 200


@bp.get('/api/v1/articles/<int:article_id>')
def get_api_article(article_id: int):
    article = Article.get_by_id(article_id)
    return jsonify(article.to_json()), 200


@bp.post('/api/v1/articles')
def create_api_article():
    data = request.json
    article = Article.create(**data)
    return jsonify(article.to_json()), 201


@bp.route('/api/v1/articles/<int:article_id>', methods=['POST', 'PATCH'])
def update_api_article(article_id: int):
    updated_article = Article.update(article_id, request.json.copy())
    return jsonify(updated_article.to_json()), 200


@bp.route('/api/v1/articles/<int:article_id>', methods=['DELETE'])
def delete_article(article_id: int):
    Article.delete(article_id)
    empty = Article.get_by_id(article_id)  # example 
    return jsonify(empty), 204
