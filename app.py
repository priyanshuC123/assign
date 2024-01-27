from flask import Flask, request
import requests
from datetime import datetime

app = Flask(__name__)


def filter_comments(comments, author, date_from, date_to, likes_from, likes_to, replies_from, replies_to, search_text):
    filtered_comments = []
    for comment in comments:
        # Convert string to datetime for comparison
        comment_date = datetime.strptime(comment['at'], '%a, %d %b %Y %H:%M:%S GMT')
        date_from_obj = datetime.strptime(date_from, '%d-%m-%Y') if date_from else datetime.min
        date_to_obj = datetime.strptime(date_to, '%d-%m-%Y') if date_to else datetime.max

        # Check each filter condition
        if (not author or author.lower() in comment['author'].lower()) and \
           (not date_from or date_from_obj <= comment_date) and \
           (not date_to or comment_date <= date_to_obj) and \
           (not likes_from or likes_from <= comment['like']) and \
           (not likes_to or comment['like'] <= likes_to) and \
           (not replies_from or replies_from <= comment['reply']) and \
           (not replies_to or comment['reply'] <= replies_to) and \
           (not search_text or search_text.lower() in comment['text'].lower()):
            filtered_comments.append(comment)

    return filtered_comments

@app.route("/search/", methods=['GET'])
def search():
    # Fetch all comments from the API
    req = requests.get("https://app.ylytic.com/ylytic/test")
    comments = req.json()['comments']

    # Retrieve query parameters
    author = request.args.get('search_author', None)
    date_from = request.args.get('at_from', None)
    date_to = request.args.get('at_to', None)
    likes_from = int(request.args.get('like_from', 0)) if request.args.get('like_from') else None
    likes_to = int(request.args.get('like_to', float('inf'))) if request.args.get('like_to') else None
    replies_from = int(request.args.get('reply_from', 0)) if request.args.get('reply_from') else None
    replies_to = int(request.args.get('reply_to', float('inf'))) if request.args.get('reply_to') else None
    search_text = request.args.get('search_text', None)

    # Filter comments based on query parameters
    if any(v is not None for v in [author, date_from, date_to, likes_from, likes_to, replies_from, replies_to, search_text]):
        filtered_comments = filter_comments(comments, author, date_from, date_to, likes_from, likes_to, replies_from, replies_to, search_text)
    else:
        filtered_comments = comments  # No filtering if no query parameters

    # Print the filtered comments to the console
    print(filtered_comments)

    # Construct an HTML response
    html_response = "<div>"
    for comment in filtered_comments:
        html_response += f"<p><strong>Author:</strong> {comment['author']}</p>"
        html_response += f"<p><strong>Date:</strong> {comment['at']}</p>"
        html_response += f"<p><strong>Likes:</strong> {comment['like']}</p>"
        html_response += f"<p><strong>Replies:</strong> {comment['reply']}</p>"
        html_response += f"<p><strong>Comment:</strong> {comment['text']}</p>"
        html_response += "<hr>"
    html_response += "</div>"

    # Return the HTML response
    return html_response

# This route will just redirect to the /search/ route
@app.route("/", methods=['GET'])
def index():
    return search()


