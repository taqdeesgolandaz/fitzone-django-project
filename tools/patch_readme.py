from pathlib import Path

readme = Path(__file__).resolve().parent.parent / 'README.md'
text = readme.read_text(encoding='utf-8')
old = "```bash\npython manage.py createsuperuser\n```\n\n---\n\n## ?? Running the Project"
new = "```bash\npython manage.py createsuperuser\n```\n\n### Step 7: Prepare Render Data Sync\n\nIf you want to send your local database data to Render, run:\n\n```bash\n./render_db_sync.sh\n```\n\nThis generates `render_data.json`, which you can import in Render after deployment.\n\n---\n\n## ?? Running the Project"
if old not in text:
    raise RuntimeError('Expected substring not found in README.md')
text = text.replace(old, new)
readme.write_text(text, encoding='utf-8')
print('README.md updated')
