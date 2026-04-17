path = r'C:\Users\edmon\.codex\config.toml'
with open(path, 'r') as f:
    content = f.read()

# Replace hyphenated keys with quoted versions
content = content.replace('.n8n-lt', '."n8n-lt"')
content = content.replace('[mcp_servers.n8n-lt]', '[mcp_servers."n8n-lt"]')

with open(path, 'w') as f:
    f.write(content)
print("Config updated successfully.")
