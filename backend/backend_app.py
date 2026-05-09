from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """ Gets all posts, sorts them and returns a jsonified response """
    sort_field = request.args.get('sort')
    direction = request.args.get('direction', 'asc')

    valid_sort_fields = ['title', 'content']
    valid_directions = ['asc', 'desc']

    if sort_field and sort_field not in valid_sort_fields:
        return jsonify({ "error": f"Invalid sort field. Allowed values are: {', '.join(valid_sort_fields)}" }), 400

    if direction not in valid_directions:
        return jsonify({ "error": f"Invalid direction. Allowed values are: asc, desc" }), 400

    result = POSTS.copy()

    if sort_field:
        reverse = direction == 'desc'
        result.sort(key=lambda post: post[sort_field].lower(), reverse=reverse)

    return jsonify(result), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    """ Adds a post with POST request and returns a jsonified response """
    data = request.get_json()

    missing_fields = []

    if not data.get('title'):
        missing_fields.append('title')

    if not data.get('content'):
        missing_fields.append('content')

    if missing_fields:
        return jsonify({ "error": f"Missing fields: {', '.join(missing_fields)}" }), 400

    new_id = max(post['id'] for post in POSTS) + 1 if POSTS else 1

    new_post = {
        "id": new_id,
        "title": data['title'],
        "content": data['content']
    }

    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """ Deletes a post with DELETE request and returns a jsonified response if successful """
    global POSTS

    post = next((post for post in POSTS if post['id'] == post_id), None)

    if post is None:
        return jsonify({ "error": f"Post with id {post_id} not found." }), 404

    POSTS = [post for post in POSTS if post['id'] != post_id]

    return jsonify({ "message": f"Post with id {post_id} has been deleted successfully." }), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """ Updates a post with PUT request and returns a jsonified response """
    data = request.get_json()

    post = next((post for post in POSTS if post['id'] == post_id), None)

    if post is None:
        return jsonify({ "error": f"Post with id {post_id} not found." }), 404

    if 'title' in data:
        post['title'] = data['title']

    if 'content' in data:
        post['content'] = data['content']

    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """ Requests all posts of given search term and returns a jsonified response """
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    filtered_posts = POSTS

    if title_query:
        filtered_posts = [
            post for post in filtered_posts
            if title_query in post['title'].lower()
        ]

    if content_query:
        filtered_posts = [
            post for post in filtered_posts
            if content_query in post['content'].lower()
        ]

    return jsonify(filtered_posts), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
