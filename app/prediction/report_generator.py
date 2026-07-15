"""
Report Generator Module — Phase 6.6.
Generates structured markdown reports (Change Impact, PR Risk, and Architecture Migration).
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Renders structured markdown reports combining graph analysis, risk metrics, and recommendations.
    """

    def generate_impact_report(
        self,
        root: str,
        impact_results: dict[str, Any],
        risk_results: dict[str, Any],
        recs: dict[str, Any]
    ) -> str:
        """
        Generate a comprehensive Change Impact Report in markdown format.
        """
        # Format lists
        files_str = "\n".join(f"- `{f}`" for f in impact_results["affected_files"][:10])
        if len(impact_results["affected_files"]) > 10:
            files_str += f"\n- *and {len(impact_results['affected_files']) - 10} more files...*"

        services_str = ", ".join(f"`{s}`" for s in impact_results["affected_services"]) if impact_results["affected_services"] else "*None*"
        apis_str = "\n".join(f"- `{api}`" for api in impact_results["affected_apis"][:10])
        if len(impact_results["affected_apis"]) > 10:
            apis_str += f"\n- *and {len(impact_results['affected_apis']) - 10} more endpoints...*"
        if not apis_str:
            apis_str = "*No API endpoints directly affected.*"

        justifications_str = "\n".join(f"- {j}" for j in risk_results["justifications"])
        reviewers_str = ", ".join(f"@{r}" for r in recs["reviewers"])
        tests_str = "\n".join(f"- `{t}`" for t in recs["tests"])
        monitoring_str = "\n".join(f"- {m}" for m in recs["monitoring"])

        report = f"""# Change Impact Assessment Report

## Executive Summary
This report analyzes the downstream ripple effects and associated risks of modifying component `{root}`.

- **Impact Level**: {impact_results['total_files']} files | {impact_results['total_services']} services | {impact_results['total_apis']} APIs
- **Risk Score**: `{risk_results['score']}/100` (**{risk_results['level']} RISK**)
- **Target Services**: {services_str}

---

## Technical Analysis

### Affected Code Files
Changes to `{root}` directly or indirectly cascade to:
{files_str}

### Affected API Endpoints
The following exposed endpoints map to handlers along the dependency path:
{apis_str}

---

## Risk Profile & Justifications
{justifications_str}

---

## Actionable Safeguards & Recommendations

### Recommended Reviewers
Based on historical ownership and file activity: {reviewers_str}

### Target Test Suite
Run the following test commands to verify downstream regressions:
{tests_str}

### Rollout Strategy
{recs['rollout']}

### Monitoring & Observability
Monitor these metrics during deployment:
{monitoring_str}
"""
        return report.strip()

    def generate_pr_report(
        self,
        pr_number: int,
        title: str,
        impact_results: dict[str, Any],
        risk_results: dict[str, Any],
        recs: dict[str, Any]
    ) -> str:
        """
        Generate a PR Risk report.
        """
        report = f"""# Pull Request Risk Assessment: PR #{pr_number}

## Summary
- **Title**: {title}
- **PR Risk Score**: `{risk_results['score']}/100` (**{risk_results['level']}**)

## Blast Radius Overview
- **Total Modified files**: {impact_results['total_files']}
- **Impacted Microservices**: {", ".join(impact_results['affected_services']) if impact_results['affected_services'] else 'None'}
- **Associated Risk Factor**: {risk_results['level']}

## Suggested Actions
- **Assigned Reviewers**: {', '.join(f'@{r}' for r in recs['reviewers'])}
- **Recommended Verification Tests**:
{"\n".join(f"  - `{t}`" for t in recs['tests'])}
"""
        return report.strip()
