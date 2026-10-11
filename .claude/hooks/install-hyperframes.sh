#!/usr/bin/env bash
# Instala el plugin HyperFrames en sesiones de Claude Code en la nube,
# donde los marketplaces declarados en settings.json no se instalan solos.
[ "$CLAUDE_CODE_REMOTE" = "true" ] || exit 0
claude plugin list 2>/dev/null | grep -q 'hyperframes@hyperframes' && exit 0
claude plugin marketplace add heygen-com/hyperframes >/dev/null 2>&1
claude plugin install hyperframes@hyperframes >/dev/null 2>&1
exit 0
