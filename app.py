import io
import os
import zipfile

from flask import Flask, abort, jsonify, render_template, request, send_file

app = Flask(__name__, template_folder="templates")
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "projects")


def list_projects():
    if not os.path.isdir(PROJECT_ROOT):
        return []

    projects = [name for name in os.listdir(PROJECT_ROOT) if os.path.isdir(os.path.join(PROJECT_ROOT, name))]
    return sorted(projects)


def find_project_path(project_name):
    project_name = os.path.basename(project_name or "")
    project_path = os.path.join(PROJECT_ROOT, project_name)
    if os.path.isdir(project_path):
        return project_path
    return None


def create_zip_response(project_name):
    project_path = find_project_path(project_name)
    if project_path is None:
        abort(404, description=f"Project '{project_name}' not found")

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zip_buffer:
        for root, _, files in os.walk(project_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                arcname = os.path.relpath(file_path, project_path)
                zip_buffer.write(file_path, arcname)

    memory_file.seek(0)
    try:
        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{project_name}.zip",
        )
    except TypeError:
        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            attachment_filename=f"{project_name}.zip",
        )


@app.route("/")
def home():
    return render_template("index.html", projects=list_projects())


@app.route("/projects.json")
def projects_json():
    return jsonify(projects=list_projects())


@app.route("/download")
def download_query():
    project_name = request.args.get("project", "")
    return create_zip_response(project_name)


@app.route("/download/<project_name>")
def download_project(project_name):
    return create_zip_response(project_name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
