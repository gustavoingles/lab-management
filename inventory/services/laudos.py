"""Geração de laudo PDF para Ordem de Serviço usando reportlab."""

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

_styles = getSampleStyleSheet()

_title_style = ParagraphStyle(
    "title",
    parent=_styles["Heading1"],
    fontSize=16,
    spaceAfter=4,
)
_subtitle_style = ParagraphStyle(
    "subtitle",
    parent=_styles["Normal"],
    fontSize=9,
    textColor=colors.HexColor("#6b7280"),
    spaceAfter=12,
)
_section_style = ParagraphStyle(
    "section",
    parent=_styles["Heading2"],
    fontSize=11,
    spaceBefore=14,
    spaceAfter=6,
    textColor=colors.HexColor("#111827"),
)
_body_style = ParagraphStyle(
    "body",
    parent=_styles["Normal"],
    fontSize=10,
    leading=14,
)
_label_style = ParagraphStyle(
    "label",
    parent=_styles["Normal"],
    fontSize=8,
    textColor=colors.HexColor("#6b7280"),
)


def _hr():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb"), spaceAfter=8)


def _field_row(label: str, value: str):
    return [Paragraph(label, _label_style), Paragraph(value or "—", _body_style)]


def gerar_laudo_os(ordem) -> bytes:
    """Retorna bytes do PDF do laudo da OrdemServico."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    story = []

    # Cabeçalho
    story.append(Paragraph("LabManager", _title_style))
    story.append(Paragraph("Sistema de Controle de Laboratório", _subtitle_style))
    story.append(_hr())

    story.append(Paragraph(f"Laudo de Ordem de Serviço #{ordem.pk}", _section_style))

    # Informações gerais
    eq = ordem.equipamento
    info_data = [
        _field_row("Equipamento", f"{eq.item.nome} — Nº série: {eq.numero_serie}"),
        _field_row("Status", ordem.get_status_display()),
        _field_row("Prioridade", ordem.get_prioridade_display()),
        _field_row(
            "Solicitante",
            ordem.solicitante.nome if ordem.solicitante else "—",
        ),
        _field_row(
            "Técnico responsável",
            ordem.tecnico_responsavel.nome if ordem.tecnico_responsavel else "—",
        ),
        _field_row(
            "Aberta em",
            ordem.aberta_em.strftime("%d/%m/%Y %H:%M") if ordem.aberta_em else "—",
        ),
        _field_row(
            "Encerrada em",
            ordem.encerrada_em.strftime("%d/%m/%Y %H:%M") if ordem.encerrada_em else "—",
        ),
    ]
    info_table = Table(info_data, colWidths=[4 * cm, None])
    info_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (0, -1), 0),
        ])
    )
    story.append(info_table)

    # Descrição do problema
    story.append(Paragraph("Descrição do Problema", _section_style))
    story.append(_hr())
    story.append(Paragraph(ordem.descricao_problema or "—", _body_style))

    # Serviço executado
    story.append(Paragraph("Serviço Executado", _section_style))
    story.append(_hr())
    story.append(Paragraph(ordem.descricao_servico or "—", _body_style))

    # Manutenções
    manutencoes = list(ordem.manutencoes.all())
    story.append(Paragraph("Manutenções Registradas", _section_style))
    story.append(_hr())

    if manutencoes:
        header = [
            Paragraph("Tipo", _label_style),
            Paragraph("Realizada em", _label_style),
            Paragraph("Próx. venc.", _label_style),
            Paragraph("Custo (R$)", _label_style),
            Paragraph("Resultado", _label_style),
        ]
        rows = [header]
        for m in manutencoes:
            rows.append([
                Paragraph(m.get_tipo_manutencao_display(), _body_style),
                Paragraph(
                    m.realizada_em.strftime("%d/%m/%Y") if m.realizada_em else "—",
                    _body_style,
                ),
                Paragraph(
                    m.proximo_vencimento.strftime("%d/%m/%Y") if m.proximo_vencimento else "—",
                    _body_style,
                ),
                Paragraph(
                    f"{m.custo_estimado:.2f}" if m.custo_estimado else "—",
                    _body_style,
                ),
                Paragraph(m.resultado or "—", _body_style),
            ])
        m_table = Table(rows, colWidths=[3 * cm, 3 * cm, 3 * cm, 2.5 * cm, None])
        m_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(m_table)
    else:
        story.append(Paragraph("Nenhuma manutenção registrada.", _body_style))

    # Assinatura
    story.append(Spacer(1, 1.5 * cm))
    story.append(_hr())
    sig_data = [
        [
            Paragraph("_______________________________", _body_style),
            Paragraph("_______________________________", _body_style),
        ],
        [
            Paragraph("Técnico Responsável", _label_style),
            Paragraph("Responsável pelo Laboratório", _label_style),
        ],
    ]
    sig_table = Table(sig_data, colWidths=["50%", "50%"])
    sig_table.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(sig_table)

    doc.build(story)
    return buf.getvalue()
