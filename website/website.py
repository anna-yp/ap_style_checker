from flask import Flask, render_template, request, jsonify, stream_with_context, Response
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.build_vectorstore import JsonlVectorPipeline
from rag.search import Prompt


def render_issue_spans(text, issues):
    """Return text with span wrappers for each issue range."""
    if not issues:
        return text

    markers = []

    for issue_index, issue in enumerate(issues):
        start_tag = (
            issue['absolute_start_index'],
            f"<span class=\"red-underline issue-marker\" "
            f"data-issue=\"{issue_index}\" "
            f"data-start=\"{issue['absolute_start_index']}\" "
            f"data-end=\"{issue['absolute_end_index']}\">"
        )
        end_tag = (issue['absolute_end_index'], "</span>")

        markers.append(start_tag)
        markers.append(end_tag)

    markers.sort(key=lambda item: item[0], reverse=True)

    output = text
    for position, marker_html in markers:
        output = output[:position] + marker_html + output[position:]

    return output

app = Flask(__name__)

@app.route('/')
def landing_page():
    return render_template('home.html')

@app.route('/checker', methods=["POST"])
def check_for_grammar():
    payload = request.get_json(silent=True) or {}
    text_content = payload.get('text', '')

    issues = grammar.check_quote_and_pos(text_content)
    text_with_divs = render_issue_spans(text_content, issues)

    return jsonify({
        'text_with_divs': text_with_divs,
        'issues': issues,
    })

@app.route('/chat', methods=["POST"])
def prompt_gpt():
    payload = request.get_json(silent=True) or {}
    text_content = payload.get('text', '')

    query = text_content
    prompt = Prompt('2025-12-31')
    response = prompt.prompt_gpt(query)

    answer_parts = []
    for item in response.output:
        if item.type == "message" and item.role == "assistant":
            for part in item.content:
                if part.type == "output_text":
                    answer_parts.append(part.text)
    answer_text = "".join(answer_parts)

    print(f'answer: {answer_text}')
    return jsonify({"answer": answer_text})


if __name__ == "__main__":
    port = 5000
    app.run(host="0.0.0.0", port=port, debug=True)
