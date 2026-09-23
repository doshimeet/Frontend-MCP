"""
Impeccable Design Critique MCP Prompt Template
Pre-engineered prompt guiding AI agents through the anti-slop design critique passes.
"""

from mcp.server.fastmcp import FastMCP


def register_critique_ui_prompt(mcp: FastMCP) -> None:
    """Registers the Impeccable design critique prompt template on FastMCP server."""

    @mcp.prompt("impeccable_design_critique")
    def impeccable_design_critique(tsx_code: str) -> str:
        """
        Guided workflow executing the Impeccable anti-slop design critique pass on generated code.
        """
        return f"""You are a Principal Product Designer reviewing frontend implementation code.
Audit the following TSX code against the Impeccable Design Standards in DESIGN.md:

### Candidate Code:
```tsx
{tsx_code}
```

### Review Protocol:
1. **/distill**: Identify cognitive clutter. Are there nested cards inside cards? Is there "status-chip soup"? Simplify the hierarchy so primary metrics stand out.
2. **/polish**: Remove AI tells (random italicized words in headings, washed-out AI beige backgrounds, inconsistent padding).
3. **/clarify**: Inspect user-facing micro-copy. Replace generic verbs ('Submit', 'Click here') with descriptive, human action text.
4. **/harden**: Ensure empty states, loading skeletons, and accessible labels exist. Check color contrast against tokens.

Output the refined TSX code with line-by-line justification for every improvement made.
"""
