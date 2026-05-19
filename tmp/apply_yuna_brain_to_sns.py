from __future__ import annotations

import datetime as dt
import json
from pathlib import Path


SNS_ROOT = Path(r"C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning")
ENGINE = SNS_ROOT / "templates" / "clean01_consumer_growth_engine_v4.js"
VALIDATOR = SNS_ROOT / "tools" / "validate_clean01_consumer_v4_deployment_draft.js"
APPROVAL_TEMPLATE = SNS_ROOT / "templates" / "telegram_approval_message_v4_consumer.md"
REPORT = SNS_ROOT / "reports" / "yuna_growth_brain_live_application_20260519.md"
DAILY_LOG = SNS_ROOT / "telemetry" / "DAILY_EXECUTION_LOG.md"
BACKUP_DIR = SNS_ROOT / "backups" / "yuna_growth_brain_20260519"


def backup(path: Path) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    target = BACKUP_DIR / f"{path.name}.before"
    target.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise RuntimeError(f"missing patch anchor: {old[:120]}")
    return text.replace(old, new, 1)


def patch_engine() -> None:
    backup(ENGINE)
    text = ENGINE.read_text(encoding="utf-8")

    text = replace_once(
        text,
        'const EXPERIMENT_VERSION = "yuna_deal_index_v5_price_judgement";\n',
        '\n'.join(
            [
                'const EXPERIMENT_VERSION = "yuna_deal_index_v6_growth_brain";',
                'const GROWTH_BRAIN_VERSION = "yuna_growth_brain_hq_agents_2026_05_19";',
                'const PRIMARY_GROWTH_METRICS = [',
                '  "follows_per_1000_reach",',
                '  "comments_per_1000_reach",',
                '  "dm_replies_per_1000_reach",',
                '  "save_rate",',
                '  "share_rate",',
                '  "profile_visits",',
                '  "average_watch_time"',
                '];',
                'const HQ_AGENT_ROLES = [',
                '  "HQ Master Controller",',
                '  "15-year SNS Marketing Strategist",',
                '  "Behavioral Psychology PhD",',
                '  "Content Strategist",',
                '  "Data Analyst",',
                '  "Automation Engineer",',
                '  "Community DM Strategist",',
                '  "Safety Reviewer",',
                '  "QA Reviewer"',
                '];',
                'const YUNA_BRAIN_PROMISE = "싼 척하는 전담액상 딜을 실제 가격, 구성, 배송비, 실패비용까지 다시 계산해주는 계정";',
                'const YUNA_FOLLOW_REASON = "매일 전담액상 딜을 사기 전에 YUNA 가격검산표로 다시 확인할 수 있어서 팔로우할 이유가 있음";',
                'const YUNA_COMMENT_CTA = "댓글에 가격/구성/배송비를 남기면 YUNA가 점수표로 다시 계산합니다";',
                'const YUNA_SAVE_CTA = "구매 전에 다시 보려고 저장할 수 있는 가격검산표";',
                '',
            ]
        ),
    )

    # Add explicit growth brain fields to each corner without changing the existing content schedule.
    corner_patches = {
        'hook_type: "visible_price_vs_real_price",': [
            'growth_experiment_id: "yuna-growth-20260519-unit-price-comment-loop",',
            'behavioral_trigger: "loss_aversion_visible_price_gap",',
            'follow_conversion_reason: YUNA_FOLLOW_REASON,',
            'save_reason: YUNA_SAVE_CTA,',
            'comment_cta: YUNA_COMMENT_CTA,',
            'decision_rule: "keep if comments_per_1000_reach or follows_per_1000_reach improves over 7-day median",',
            'experiment_hypothesis: "배송비 전 겉가격과 실제 병당가 차이를 보여주면 저장과 댓글이 증가한다",',
        ],
        'hook_type: "checkout_price_gap",': [
            'growth_experiment_id: "yuna-growth-20260519-checkout-total-gap",',
            'behavioral_trigger: "checkout_surprise_and_control",',
            'follow_conversion_reason: YUNA_FOLLOW_REASON,',
            'save_reason: "결제창 가기 전에 다시 확인할 체크리스트라 저장할 이유가 있음",',
            'comment_cta: "댓글에 결제창 총액/배송비를 남기면 YUNA가 실제 지불가로 다시 계산합니다",',
            'decision_rule: "keep if save_rate and comments_per_1000_reach beat 7-day median",',
            'experiment_hypothesis: "결제창 총액 경고는 구매 직전 불안을 자극해 댓글과 저장을 만든다",',
        ],
        'hook_type: "discount_waste_warning",': [
            'growth_experiment_id: "yuna-growth-20260519-failure-cost-dm-loop",',
            'behavioral_trigger: "waste_avoidance_and_personal_fit",',
            'follow_conversion_reason: "취향/기기 실패비용까지 계산해주기 때문에 팔로우할 이유가 있음",',
            'save_reason: "실패비용 체크 기준으로 다시 볼 수 있어서 저장할 이유가 있음",',
            'comment_cta: "댓글에 취향/기기명/가격을 남기면 YUNA가 실패비용까지 계산합니다",',
            'decision_rule: "keep if dm_replies_per_1000_reach or comment depth improves",',
            'experiment_hypothesis: "못 쓰면 0점이라는 손실 프레임은 DM 상담성 댓글을 늘린다",',
        ],
        'hook_type: "restock_price_timing",': [
            'growth_experiment_id: "yuna-growth-20260519-night-price-radar-follow",',
            'behavioral_trigger: "future_value_and_alert_loop",',
            'follow_conversion_reason: "밤 가격 레이더에 계속 올라오려면 팔로우할 이유가 있음",',
            'save_reason: "재입고/정책 변화 전후 가격을 비교하려고 저장할 이유가 있음",',
            'comment_cta: "댓글에 보고 싶은 상품을 남기면 YUNA 밤 가격 레이더에 올립니다",',
            'decision_rule: "keep if follows_per_1000_reach improves over 7-day median",',
            'experiment_hypothesis: "다음에도 가격 변화를 봐야 한다는 미래가치는 팔로우를 만든다",',
        ],
    }
    for anchor, additions in corner_patches.items():
        text = replace_once(text, anchor, "\n".join([anchor, *[f"    {line}" for line in additions]]))

    text = replace_once(
        text,
        '    "Consumer payoff:",\n    spec.consumer_payoff,\n',
        '    "Consumer payoff:",\n    spec.consumer_payoff,\n    "",\n    "YUNA Brain:",\n    `- Growth experiment: ${spec.growth_experiment_id}`,\n    `- Behavioral trigger: ${spec.behavioral_trigger}`,\n    `- Follow reason: ${spec.follow_conversion_reason}`,\n    `- Save reason: ${spec.save_reason}`,\n    `- Comment CTA: ${spec.comment_cta}`,\n    `- Decision rule: ${spec.decision_rule}`,\n',
    )
    text = replace_once(
        text,
        '    `Primary metric: ${spec.expected_primary_metric}`,\n',
        '    `Primary metric: ${spec.expected_primary_metric}`,\n    `Measurement set: ${PRIMARY_GROWTH_METRICS.join(", ")}`,\n',
    )
    text = replace_once(
        text,
        '      experiment_version: EXPERIMENT_VERSION,\n      strategy_version: STRATEGY_VERSION,\n',
        '      experiment_version: EXPERIMENT_VERSION,\n      growth_brain_version: GROWTH_BRAIN_VERSION,\n      hq_agent_roles: HQ_AGENT_ROLES,\n      primary_growth_metrics: PRIMARY_GROWTH_METRICS,\n      yuna_brain_promise: YUNA_BRAIN_PROMISE,\n      strategy_version: STRATEGY_VERSION,\n',
    )
    text = replace_once(
        text,
        '      expected_primary_metric: spec.expected_primary_metric,\n      risk_level: spec.risk_level,\n',
        '      expected_primary_metric: spec.expected_primary_metric,\n      growth_experiment_id: spec.growth_experiment_id,\n      behavioral_trigger: spec.behavioral_trigger,\n      follow_conversion_reason: spec.follow_conversion_reason,\n      save_reason: spec.save_reason,\n      comment_cta: spec.comment_cta,\n      decision_rule: spec.decision_rule,\n      experiment_hypothesis: spec.experiment_hypothesis,\n      risk_level: spec.risk_level,\n',
    )
    text = replace_once(
        text,
        '      why_follow: "매일 겉가격을 실제 지불가와 실패비용까지 넣어 다시 계산해주는 계정",\n',
        '      why_follow: spec.follow_conversion_reason,\n',
    )
    text = replace_once(
        text,
        '  strategy_version: STRATEGY_VERSION,\n  deployment_stage: DEPLOYMENT_STAGE\n',
        '  strategy_version: STRATEGY_VERSION,\n  growth_brain_version: GROWTH_BRAIN_VERSION,\n  primary_growth_metrics: PRIMARY_GROWTH_METRICS,\n  deployment_stage: DEPLOYMENT_STAGE\n',
    )

    ENGINE.write_text(text, encoding="utf-8")


def patch_validator() -> None:
    backup(VALIDATOR)
    text = VALIDATOR.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '    assert(j.brand_name === "YUNA DEAL INDEX", "brand_name must be YUNA DEAL INDEX");\n',
        '    assert(j.brand_name === "YUNA DEAL INDEX", "brand_name must be YUNA DEAL INDEX");\n    assert(j.growth_brain_version === "yuna_growth_brain_hq_agents_2026_05_19", "growth_brain_version missing");\n    assert(Array.isArray(j.hq_agent_roles) && j.hq_agent_roles.includes("Behavioral Psychology PhD"), "HQ agent roles missing behavioral psychologist");\n    assert(Array.isArray(j.primary_growth_metrics) && j.primary_growth_metrics.includes("follows_per_1000_reach"), "primary growth metrics missing follows_per_1000_reach");\n',
    )
    text = replace_once(
        text,
        '    assert(j.visible_price && j.hidden_cost && j.verdict_line, "price judgement fields required");\n',
        '    assert(j.visible_price && j.hidden_cost && j.verdict_line, "price judgement fields required");\n    assert(j.growth_experiment_id && j.behavioral_trigger && j.follow_conversion_reason, "growth brain fields required");\n    assert(j.save_reason && j.comment_cta && j.decision_rule && j.experiment_hypothesis, "experiment decision fields required");\n',
    )
    text = replace_once(
        text,
        '    "retention_hook",\n',
        '    "retention_hook",\n    "growth_brain_version",\n    "hq_agent_roles",\n    "primary_growth_metrics",\n    "growth_experiment_id",\n    "behavioral_trigger",\n    "follow_conversion_reason",\n    "save_reason",\n    "comment_cta",\n    "decision_rule",\n    "experiment_hypothesis",\n',
    )
    text = replace_once(
        text,
        '    assert(j.telegram_approval_text.includes("Retention hook"), "approval text missing retention hook");\n',
        '    assert(j.telegram_approval_text.includes("Retention hook"), "approval text missing retention hook");\n    assert(j.telegram_approval_text.includes("YUNA Brain"), "approval text missing YUNA Brain section");\n    assert(j.telegram_approval_text.includes("Behavioral trigger"), "approval text missing behavioral trigger");\n    assert(j.telegram_approval_text.includes("Decision rule"), "approval text missing decision rule");\n',
    )
    VALIDATOR.write_text(text, encoding="utf-8")


def patch_approval_template() -> None:
    backup(APPROVAL_TEMPLATE)
    text = APPROVAL_TEMPLATE.read_text(encoding="utf-8")
    if "YUNA Brain" not in text:
        text = replace_once(
            text,
            "Consumer payoff:\n{{promised_payoff}}\n\nFollow conversion:\n",
            "Consumer payoff:\n{{promised_payoff}}\n\nYUNA Brain:\n- Growth experiment: {{growth_experiment_id}}\n- Behavioral trigger: {{behavioral_trigger}}\n- Follow reason: {{follow_conversion_reason}}\n- Save reason: {{save_reason}}\n- Comment CTA: {{comment_cta}}\n- Decision rule: {{decision_rule}}\n\nFollow conversion:\n",
        )
    APPROVAL_TEMPLATE.write_text(text, encoding="utf-8")


def write_report() -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "\n".join(
            [
                "# YUNA Growth Brain Live Application - 2026-05-19",
                "",
                "## Status",
                "",
                "`LOCAL_PATCH_READY_FOR_DEPLOY`",
                "",
                "## Applied Locally",
                "",
                "- Added `growth_brain_version` to clean_01 candidate output.",
                "- Added HQ agent roles including 15-year SNS strategy and behavioral psychology.",
                "- Added primary metrics: follows per reach, comments per reach, DM replies per reach, save rate, share rate, profile visits, average watch time.",
                "- Added per-corner experiment ids, behavioral triggers, follow reasons, save reasons, comment CTAs, hypotheses, and keep/kill decision rules.",
                "- Added a visible `YUNA Brain` section to Telegram approval text.",
                "- Updated validation so future candidate generation fails if these growth fields disappear.",
                "",
                "## Safety",
                "",
                "- No Instagram post was published by this patch.",
                "- No manual comment or DM test was sent.",
                "- No credential value was printed.",
                "- The existing approval gate remains in place.",
                "",
                "## Next",
                "",
                "Run validator, deploy the Build Simulation Content node, then verify the live workflow keeps the new `growth_brain_version` marker.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def append_log() -> None:
    entry = f"""

## 2026-05-19 - YUNA Growth Brain Live Application

- Applied TAC YUNA brain system to the SNS automation planning workspace.
- Added growth experiment metadata to clean_01 candidate generation.
- Added Telegram approval visibility for behavioral trigger, follow reason, save reason, comment CTA, and decision rule.
- Strengthened validation to require the new growth brain fields.
- No Instagram publish, manual DM/comment test, credential output, or production publish action was performed by the patch script.
"""
    DAILY_LOG.write_text(DAILY_LOG.read_text(encoding="utf-8") + entry, encoding="utf-8")


def main() -> None:
    patch_engine()
    patch_validator()
    patch_approval_template()
    write_report()
    append_log()
    print(
        json.dumps(
            {
                "status": "PASS",
                "engine": str(ENGINE),
                "validator": str(VALIDATOR),
                "approval_template": str(APPROVAL_TEMPLATE),
                "report": str(REPORT),
                "backup_dir": str(BACKUP_DIR),
                "live_operations_performed": False,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
