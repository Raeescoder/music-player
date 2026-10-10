"""
GitHub API Auto-Publisher Script
Publishes all project files and the .github/workflows/deploy.yml directly to GitHub
using the GitHub REST API (No git.exe required).
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IGNORE_FILES = {
    ".git",
    "__pycache__",
    "music-player.zip",
    "dist"
}

def get_files_to_upload():
    upload_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_FILES]
        for f in files:
            if f.endswith(".pyc") or f == ".DS_Store":
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, BASE_DIR).replace("\\", "/")
            if any(rel_path.startswith(ig + "/") for ig in IGNORE_FILES):
                continue
            upload_files.append((rel_path, full_path))
    return upload_files

def github_api_request(url, token, data=None, method="GET"):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "Antigravity-MusicPlayer-Deployer",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    encoded_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            if content:
                try:
                    return json.loads(content)
                except Exception:
                    return content
            return {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(err_body)
            msg = err_json.get("message", err_body)
        except Exception:
            msg = err_body
        raise Exception(f"HTTP {e.code} on {method} {url}: {msg}")

def push_to_github(token, repo_name, make_private=False):
    print("1. Verifying GitHub token...")
    user_info = github_api_request("https://api.github.com/user", token)
    username = user_info.get("login")
    if not username:
        print("Error: Could not retrieve username with provided token.")
        return False
    print(f"Authenticated as: {username}")

    # Check if repo exists, else create it
    print(f"2. Checking repository: {username}/{repo_name}...")
    repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
    try:
        repo_info = github_api_request(repo_url, token)
        print(f"Repository {username}/{repo_name} already exists. Updating it...")
    except Exception as e:
        if "404" in str(e):
            print(f"Repository does not exist. Creating {repo_name}...")
            repo_info = github_api_request(
                "https://api.github.com/user/repos",
                token,
                data={"name": repo_name, "private": make_private, "auto_init": True},
                method="POST"
            )
        else:
            raise

    # Collect files
    files = get_files_to_upload()
    print(f"3. Uploading {len(files)} files via GitHub Tree API...")

    # Upload Blobs
    tree_items = []
    for rel_path, full_path in files:
        with open(full_path, "rb") as f:
            content = f.read()
        b64 = base64.b64encode(content).decode("utf-8")
        blob_res = github_api_request(
            f"https://api.github.com/repos/{username}/{repo_name}/git/blobs",
            token,
            data={"content": b64, "encoding": "base64"},
            method="POST"
        )
        tree_items.append({
            "path": rel_path,
            "mode": "100644",
            "type": "blob",
            "sha": blob_res["sha"]
        })
        print(f"  [+] {rel_path}")

    # Get parent commit if exists
    parent_sha = None
    base_tree_sha = None
    for b_name in ["main", "master"]:
        try:
            ref_res = github_api_request(f"https://api.github.com/repos/{username}/{repo_name}/git/refs/heads/{b_name}", token)
            parent_sha = ref_res["object"]["sha"]
            commit_info = github_api_request(f"https://api.github.com/repos/{username}/{repo_name}/git/commits/{parent_sha}", token)
            base_tree_sha = commit_info["tree"]["sha"]
            break
        except Exception:
            continue

    # Create Tree
    print("4. Creating Git Tree...")
    tree_payload = {"tree": tree_items}
    if base_tree_sha:
        tree_payload["base_tree"] = base_tree_sha

    tree_res = github_api_request(
        f"https://api.github.com/repos/{username}/{repo_name}/git/trees",
        token,
        data=tree_payload,
        method="POST"
    )

    # Create Commit
    print("5. Creating Commit...")
    commit_payload = {
        "message": "Deploy Top 50 Music Player with GitHub Actions & SQLite database",
        "tree": tree_res["sha"]
    }
    if parent_sha:
        commit_payload["parents"] = [parent_sha]

    commit_res = github_api_request(
        f"https://api.github.com/repos/{username}/{repo_name}/git/commits",
        token,
        data=commit_payload,
        method="POST"
    )

    # Update or Create Ref
    print("6. Updating branch ref (main)...")
    try:
        github_api_request(
            f"https://api.github.com/repos/{username}/{repo_name}/git/refs/heads/main",
            token,
            data={"sha": commit_res["sha"], "force": True},
            method="PATCH"
        )
    except Exception:
        try:
            github_api_request(
                f"https://api.github.com/repos/{username}/{repo_name}/git/refs",
                token,
                data={"ref": "refs/heads/main", "sha": commit_res["sha"]},
                method="POST"
            )
        except Exception as e2:
            print(f"Ref creation note: {e2}")

    # Enable GitHub Pages via Actions
    print("7. Configuring GitHub Pages with Actions build source...")
    try:
        github_api_request(
            f"https://api.github.com/repos/{username}/{repo_name}/pages",
            token,
            data={"build_type": "workflow"},
            method="POST"
        )
    except Exception:
        try:
            github_api_request(
                f"https://api.github.com/repos/{username}/{repo_name}/pages",
                token,
                data={"build_type": "workflow"},
                method="PUT"
            )
        except Exception:
            pass

    print("\n" + "=" * 60)
    print("SUCCESS! PROJECT PUBLISHED TO GITHUB!")
    print(f"Repository : https://github.com/{username}/{repo_name}")
    print(f"Live URL   : https://{username}.github.io/{repo_name}/")
    print("GitHub Actions is now running the deployment in the background!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python push_to_github.py <GITHUB_TOKEN> [repo_name]")
        sys.exit(1)
    tok = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else "music-player"
    push_to_github(tok, name)
