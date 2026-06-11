import json
import os
import sys

def main():
    agent_context_path = '.codex/agent_context.json'
    if not os.path.exists(agent_context_path):
        print(f"No {agent_context_path} — skipping (run copilot-agent-vars-bootstrap first)")
        return

    print(f"Injecting repo variable context from {agent_context_path}")
    try:
        with open(agent_context_path, encoding='utf-8') as handle:
            context = json.load(handle)
        
        github_env_path = os.environ.get('GITHUB_ENV')
        if not github_env_path:
            print("Warning: GITHUB_ENV environment variable not set.")
            return

        injected = 0
        with open(github_env_path, 'a', encoding='utf-8') as github_env:
            for key, value in context.items():
                if not key.startswith('_') and value:
                    github_env.write(f'{key}={value}\n')
                    injected += 1
        print(f'Injected {injected} variables into GITHUB_ENV')
    except Exception as exc:
        print(f'Warning: {exc}')

if __name__ == '__main__':
    main()
