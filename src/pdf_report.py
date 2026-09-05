import io
import html

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)


# =========================================================
# RISKLENS PDF THEME
# =========================================================

NAVY = colors.HexColor("#151A28")
NAVY_SOFT = colors.HexColor("#202638")

BURGUNDY = colors.HexColor("#812D2A")
BURGUNDY_LIGHT = colors.HexColor("#A8443F")

IVORY = colors.HexColor("#DFDCC7")
IVORY_LIGHT = colors.HexColor("#F4F1E5")

TEXT = colors.HexColor("#2F3442")
MUTED = colors.HexColor("#74716A")

BORDER = colors.HexColor("#D8D4C7")

GREEN = colors.HexColor("#4F8C70")
AMBER = colors.HexColor("#B88732")

WHITE = colors.white


def safe_text(value):
    """
    Escape external/generated text before inserting it
    into ReportLab Paragraph markup.
    """
    if value is None:
        return ""

    return html.escape(str(value))


def money(value):
    """
    Use INR instead of the rupee symbol because ReportLab's
    built-in Helvetica font does not reliably support ₹.
    """
    return f"INR {float(value):,.2f}"


def add_page_number(canvas, doc):
    """
    Add a small RiskLens footer to every PDF page.
    """

    canvas.saveState()

    width, _ = A4

    canvas.setStrokeColor(
        colors.HexColor("#D9D5C8")
    )
    canvas.setLineWidth(0.4)

    canvas.line(
        18 * mm,
        12 * mm,
        width - 18 * mm,
        12 * mm,
    )

    canvas.setFont(
        "Helvetica",
        7,
    )

    canvas.setFillColor(
        colors.HexColor("#77736C")
    )

    canvas.drawString(
        18 * mm,
        7.5 * mm,
        "RiskLens AI - Transaction Risk Investigation Report",
    )

    canvas.drawRightString(
        width - 18 * mm,
        7.5 * mm,
        f"Page {doc.page}",
    )

    canvas.restoreState()


def generate_pdf_report(result):
    """
    Generate a professional investigator-facing PDF
    using an already completed RiskLens analysis.

    Gemini is NOT called again.
    """

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,

        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=18 * mm,

        title="RiskLens AI Investigation Report",
        author="RiskLens AI",
    )

    styles = getSampleStyleSheet()

    # =====================================================
    # STYLES
    # =====================================================

    title_style = ParagraphStyle(
        "RiskLensTitle",
        parent=styles["Title"],

        fontName="Helvetica-Bold",

        fontSize=21,
        leading=24,

        textColor=NAVY,

        alignment=TA_LEFT,

        spaceAfter=2,
    )

    subtitle_style = ParagraphStyle(
        "RiskLensSubtitle",
        parent=styles["Normal"],

        fontName="Helvetica",

        fontSize=8,
        leading=11,

        textColor=MUTED,

        spaceAfter=12,
    )

    section_style = ParagraphStyle(
        "RiskLensSection",

        parent=styles["Heading2"],

        fontName="Helvetica-Bold",

        fontSize=10.5,
        leading=13,

        textColor=BURGUNDY,

        spaceBefore=9,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "RiskLensBody",

        parent=styles["BodyText"],

        fontName="Helvetica",

        fontSize=8.2,
        leading=12,

        textColor=TEXT,

        alignment=TA_LEFT,

        spaceAfter=4,
    )

    small_style = ParagraphStyle(
        "RiskLensSmall",

        parent=body_style,

        fontSize=7.4,
        leading=10.5,

        textColor=MUTED,
    )

    assessment_style = ParagraphStyle(
        "Assessment",

        parent=body_style,

        fontName="Helvetica-Bold",

        fontSize=8.8,
        leading=13,

        textColor=NAVY,
    )

    warning_style = ParagraphStyle(
        "Warning",

        parent=body_style,

        fontName="Helvetica-Bold",

        fontSize=8.2,
        leading=12,

        textColor=BURGUNDY,
    )

    white_small_style = ParagraphStyle(
        "WhiteSmall",

        parent=small_style,

        fontName="Helvetica-Bold",

        textColor=WHITE,

        alignment=TA_CENTER,
    )

    story = []

    report = result["report"]
    baseline = result["baseline"]
    ai_response = result["ai_investigation"]

    structured_ai = ai_response.get(
        "structured",
        {},
    )

    # =====================================================
    # HEADER
    # =====================================================

    story.append(
        Paragraph(
            "RiskLens AI",
            title_style,
        )
    )

    story.append(
        Paragraph(
            (
                "TRANSACTION RISK INVESTIGATION ASSISTANT"
                " &nbsp;&nbsp;|&nbsp;&nbsp; "
                "EVIDENCE-GROUNDED REPORT"
            ),
            subtitle_style,
        )
    )

    # Decorative header line

    header_bar = Table(
        [[""]],
        colWidths=[178 * mm],
        rowHeights=[2.2 * mm],
    )

    header_bar.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    BURGUNDY,
                ),
            ]
        )
    )

    story.append(header_bar)

    story.append(
        Spacer(
            1,
            7,
        )
    )

    # =====================================================
    # PRIMARY FINDING
    # =====================================================

    story.append(
        Paragraph(
            "PRIMARY FINDING",
            section_style,
        )
    )

    status = report["status"]

    if status == "ATTENTION RECOMMENDED":
        status_background = colors.HexColor(
            "#F4E7E4"
        )

        status_color = BURGUNDY

    else:
        status_background = colors.HexColor(
            "#E8F2EC"
        )

        status_color = GREEN

    status_table = Table(
        [
            [
                Paragraph(
                    f"<b>{safe_text(status)}</b>",
                    assessment_style,
                ),
                Paragraph(
                    safe_text(
                        report["summary"]
                    ),
                    body_style,
                ),
            ]
        ],

        colWidths=[
            48 * mm,
            130 * mm,
        ],
    )

    status_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, 0),
                    status_background,
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (0, 0),
                    status_color,
                ),

                (
                    "BACKGROUND",
                    (1, 0),
                    (1, 0),
                    colors.HexColor(
                        "#FAF9F5"
                    ),
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    BORDER,
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
            ]
        )
    )

    story.append(status_table)

    # =====================================================
    # METRICS
    # =====================================================

    story.append(
        Spacer(
            1,
            7,
        )
    )

    metric_headers = [
        "TRANSACTIONS",
        "FLAGGED",
        "AMOUNT UNDER REVIEW",
        "RULES TRIGGERED",
    ]

    metric_values = [
        str(
            baseline["transaction_count"]
        ),

        str(
            len(
                report[
                    "flagged_transaction_ids"
                ]
            )
        ),

        money(
            report["total_flagged_amount"]
        ),

        str(
            len(
                report["triggered_rules"]
            )
        ),
    ]

    metric_table = Table(
        [
            metric_headers,
            metric_values,
        ],

        colWidths=[
            40 * mm,
            36 * mm,
            58 * mm,
            44 * mm,
        ],
    )

    metric_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    NAVY,
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    IVORY,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, 0),
                    6.8,
                ),

                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, 1),
                    colors.HexColor(
                        "#F4F1E5"
                    ),
                ),

                (
                    "TEXTCOLOR",
                    (0, 1),
                    (-1, 1),
                    NAVY,
                ),

                (
                    "FONTNAME",
                    (0, 1),
                    (-1, 1),
                    "Helvetica-Bold",
                ),

                (
                    "FONTSIZE",
                    (0, 1),
                    (-1, 1),
                    8.5,
                ),

                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    BORDER,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(metric_table)

    # =====================================================
    # CUSTOMER BASELINE
    # =====================================================

    story.append(
        Paragraph(
            "CUSTOMER BASELINE",
            section_style,
        )
    )

    common_channel = "-"

    if baseline["channels"]:
        common_channel = next(
            iter(
                baseline[
                    "channels"
                ].keys()
            )
        )

    baseline_data = [
        [
            "Median transaction",
            money(
                baseline["amount"]["median"]
            ),
        ],

        [
            "Average transaction",
            money(
                baseline["amount"]["mean"]
            ),
        ],

        [
            "Typical activity",
            (
                f"{baseline['time']['typical_start_time']}"
                f" - "
                f"{baseline['time']['typical_end_time']}"
            ),
        ],

        [
            "Most common channel",
            safe_text(
                common_channel
            ),
        ],
    ]

    baseline_table = Table(
        baseline_data,

        colWidths=[
            73 * mm,
            105 * mm,
        ],
    )

    baseline_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor(
                        "#EFEBDD"
                    ),
                ),

                (
                    "BACKGROUND",
                    (1, 0),
                    (1, -1),
                    colors.HexColor(
                        "#FBFAF7"
                    ),
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, -1),
                    TEXT,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),

                (
                    "FONTNAME",
                    (1, 0),
                    (1, -1),
                    "Helvetica",
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7.5,
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    BORDER,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5.5,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5.5,
                ),
            ]
        )
    )

    story.append(baseline_table)

    # =====================================================
    # TRIGGERED RULES
    # =====================================================

    story.append(
        Paragraph(
            "TRIGGERED RISK RULES",
            section_style,
        )
    )

    if report["triggered_rules"]:

        rule_cells = []

        for rule in report["triggered_rules"]:

            rule_cells.append(
                [
                    Paragraph(
                        safe_text(
                            rule["rule_id"]
                        ),
                        warning_style,
                    ),

                    Paragraph(
                        safe_text(
                            rule["rule_name"]
                        ),
                        body_style,
                    ),
                ]
            )

        rules_table = Table(
            rule_cells,

            colWidths=[
                27 * mm,
                151 * mm,
            ],
        )

        rules_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.HexColor(
                            "#F4E8E5"
                        ),
                    ),

                    (
                        "BACKGROUND",
                        (1, 0),
                        (1, -1),
                        colors.HexColor(
                            "#FCFBF8"
                        ),
                    ),

                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.35,
                        BORDER,
                    ),

                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.25,
                        BORDER,
                    ),

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                ]
            )
        )

        story.append(
            rules_table
        )

    else:

        story.append(
            Paragraph(
                "No risk rules were triggered.",
                body_style,
            )
        )

    # =====================================================
    # FLAGGED TRANSACTIONS
    # =====================================================

    story.append(
        Paragraph(
            "FLAGGED TRANSACTIONS",
            section_style,
        )
    )

    if report["findings"]:

        transaction_data = [
            [
                "ID",
                "DATE / TIME",
                "PAYEE",
                "AMOUNT",
                "CHANNEL",
            ]
        ]

        for finding in report["findings"]:

            transaction_data.append(
                [
                    safe_text(
                        finding[
                            "transaction_id"
                        ]
                    ),

                    safe_text(
                        finding[
                            "datetime"
                        ]
                    ),

                    safe_text(
                        finding[
                            "payee"
                        ]
                    ),

                    money(
                        finding[
                            "amount"
                        ]
                    ),

                    safe_text(
                        finding[
                            "channel"
                        ]
                    ),
                ]
            )

        transaction_table = Table(
            transaction_data,

            repeatRows=1,

            colWidths=[
                21 * mm,
                43 * mm,
                41 * mm,
                37 * mm,
                36 * mm,
            ],
        )

        transaction_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        BURGUNDY,
                    ),

                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        WHITE,
                    ),

                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),

                    (
                        "FONTNAME",
                        (0, 1),
                        (-1, -1),
                        "Helvetica",
                    ),

                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        6.8,
                    ),

                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.HexColor(
                                "#FFFFFF"
                            ),
                            colors.HexColor(
                                "#F8F6EF"
                            ),
                        ],
                    ),

                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.35,
                        BORDER,
                    ),

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        story.append(
            transaction_table
        )

    else:

        story.append(
            Paragraph(
                (
                    "No transaction evidence "
                    "requires investigator review."
                ),
                body_style,
            )
        )

    # =====================================================
    # AI INVESTIGATOR
    # NO FORCED PAGE BREAK
    # =====================================================

    story.append(
        Paragraph(
            "AI INVESTIGATOR",
            section_style,
        )
    )

    if (
        ai_response.get("available")
        and structured_ai
    ):

        # ---------------------------------------------
        # ATTENTION ASSESSMENT
        # ---------------------------------------------

        assessment = safe_text(
            structured_ai.get(
                "attention_assessment",
                "",
            )
        )

        if assessment:

            assessment_table = Table(
                [
                    [
                        Paragraph(
                            "<b>01</b>",
                            warning_style,
                        ),

                        Paragraph(
                            "<b>ATTENTION ASSESSMENT</b><br/>"
                            + assessment,
                            body_style,
                        ),
                    ]
                ],

                colWidths=[
                    14 * mm,
                    164 * mm,
                ],
            )

            assessment_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (0, 0),
                            colors.HexColor(
                                "#F0E1DE"
                            ),
                        ),

                        (
                            "BACKGROUND",
                            (1, 0),
                            (1, 0),
                            colors.HexColor(
                                "#FAF7F3"
                            ),
                        ),

                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            0.4,
                            colors.HexColor(
                                "#DEC9C5"
                            ),
                        ),

                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),

                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            7,
                        ),

                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            7,
                        ),
                    ]
                )
            )

            story.append(
                assessment_table
            )

            story.append(
                Spacer(
                    1,
                    5,
                )
            )

        # ---------------------------------------------
        # TWO COLUMN AI INSIGHT CARDS
        # ---------------------------------------------

        def bullet_content(items):

            if not items:
                return Paragraph(
                    "No additional findings.",
                    small_style,
                )

            parts = []

            for item in items:

                parts.append(
                    "&#8226; "
                    + safe_text(item)
                )

            return Paragraph(
                "<br/><br/>".join(parts),
                body_style,
            )

        key_findings = bullet_content(
            structured_ai.get(
                "key_findings",
                [],
            )
        )

        connected = bullet_content(
            structured_ai.get(
                "connected_activity",
                [],
            )
        )

        deviations = bullet_content(
            structured_ai.get(
                "deviation_from_normal_behaviour",
                [],
            )
        )

        priorities = (
            structured_ai.get(
                "investigator_priority",
                [],
            )
        )

        if priorities:

            priority_parts = []

            for index, item in enumerate(
                priorities,
                start=1,
            ):

                priority_parts.append(
                    (
                        f"<b>{index:02d}</b>"
                        f"&nbsp;&nbsp;"
                        f"{safe_text(item)}"
                    )
                )

            priority_content = Paragraph(
                "<br/><br/>".join(
                    priority_parts
                ),
                body_style,
            )

        else:

            priority_content = Paragraph(
                "No additional investigator action.",
                small_style,
            )

        ai_grid_data = [
            [
                Paragraph(
                    "<b>02 &nbsp; KEY FINDINGS</b>",
                    warning_style,
                ),

                Paragraph(
                    "<b>03 &nbsp; CONNECTED ACTIVITY</b>",
                    warning_style,
                ),
            ],

            [
                key_findings,
                connected,
            ],

            [
                Paragraph(
                    "<b>04 &nbsp; BEHAVIOUR DEVIATION</b>",
                    warning_style,
                ),

                Paragraph(
                    "<b>05 &nbsp; INVESTIGATOR PRIORITY</b>",
                    warning_style,
                ),
            ],

            [
                deviations,
                priority_content,
            ],
        ]

        ai_grid = Table(
            ai_grid_data,

            colWidths=[
                88 * mm,
                88 * mm,
            ],

            hAlign="LEFT",
        )

        ai_grid.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor(
                            "#F2E5E2"
                        ),
                    ),

                    (
                        "BACKGROUND",
                        (0, 2),
                        (-1, 2),
                        colors.HexColor(
                            "#F2E5E2"
                        ),
                    ),

                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, 1),
                        colors.HexColor(
                            "#FCFBF8"
                        ),
                    ),

                    (
                        "BACKGROUND",
                        (0, 3),
                        (-1, 3),
                        colors.HexColor(
                            "#FCFBF8"
                        ),
                    ),

                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        BORDER,
                    ),

                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.3,
                        BORDER,
                    ),

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),

                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(
            ai_grid
        )

        # ---------------------------------------------
        # LIMITATION
        # ---------------------------------------------

        limitation = safe_text(
            structured_ai.get(
                "limitation",
                "",
            )
        )

        if limitation:

            story.append(
                Spacer(
                    1,
                    6,
                )
            )

            limitation_table = Table(
                [
                    [
                        Paragraph(
                            "<b>HUMAN REVIEW LIMITATION</b>",
                            warning_style,
                        ),

                        Paragraph(
                            limitation,
                            body_style,
                        ),
                    ]
                ],

                colWidths=[
                    44 * mm,
                    134 * mm,
                ],
            )

            limitation_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (0, 0),
                            colors.HexColor(
                                "#F5ECD8"
                            ),
                        ),

                        (
                            "BACKGROUND",
                            (1, 0),
                            (1, 0),
                            colors.HexColor(
                                "#FCFAF4"
                            ),
                        ),

                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            0.4,
                            colors.HexColor(
                                "#DFD2B7"
                            ),
                        ),

                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),

                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            7,
                        ),

                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            7,
                        ),
                    ]
                )
            )

            story.append(
                limitation_table
            )

    else:

        story.append(
            Paragraph(
                (
                    "<b>AI explanation temporarily unavailable.</b><br/>"
                    "The deterministic investigation results remain "
                    "fully available for human review."
                ),
                body_style,
            )
        )

    # =====================================================
    # FINAL HUMAN REVIEW NOTICE
    # =====================================================

    story.append(
        Spacer(
            1,
            7,
        )
    )

    human_notice = Table(
        [
            [
                Paragraph(
                    "<b>HUMAN JUDGMENT REMAINS AUTHORITATIVE</b>",
                    warning_style,
                ),

                Paragraph(
                    (
                        "RiskLens identifies and explains activity "
                        "requiring review. Risk indicators do not "
                        "establish that fraud occurred. Final judgment "
                        "remains with the human investigator."
                    ),
                    body_style,
                ),
            ]
        ],

        colWidths=[
            58 * mm,
            120 * mm,
        ],
    )

    human_notice.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(
                        "#F7F3EA"
                    ),
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    BURGUNDY,
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(
        human_notice
    )

    # =====================================================
    # BUILD PDF
    # =====================================================

    doc.build(
        story,

        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    buffer.seek(0)

    return buffer