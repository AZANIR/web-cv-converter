#!/usr/bin/env python3
"""CV PDF generator using ReportLab — reads data.json + styles.json, outputs a PDF."""

import json
import os
import sys
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Table, TableStyle,
    NextPageTemplate,
)

from components import HeaderBlock, SectionDivider, TechTagRow

PAGE_WIDTH, PAGE_HEIGHT = A4
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def register_fonts():
    """Register LiberationSans font family and return a name mapping dict."""
    font_dir = os.path.join(BASE_DIR, 'fonts')
    names = {
        'regular': 'LiberationSans',
        'bold': 'LiberationSans-Bold',
        'italic': 'LiberationSans-Italic',
    }
    pdfmetrics.registerFont(
        TTFont(names['regular'], os.path.join(font_dir, 'LiberationSans-Regular.ttf'))
    )
    pdfmetrics.registerFont(
        TTFont(names['bold'], os.path.join(font_dir, 'LiberationSans-Bold.ttf'))
    )
    pdfmetrics.registerFont(
        TTFont(names['italic'], os.path.join(font_dir, 'LiberationSans-Italic.ttf'))
    )
    pdfmetrics.registerFontFamily(
        names['regular'],
        normal=names['regular'],
        bold=names['bold'],
        italic=names['italic'],
    )
    return names


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_styles(scfg, font_names):
    """Build named ParagraphStyles from the styles configuration."""
    col = scfg['colors']
    fn = font_names

    section_title = ParagraphStyle(
        'section_title',
        fontName=fn['bold'],
        fontSize=scfg['section_title']['font_size_pt'],
        textColor=HexColor(col['section_title']),
        spaceBefore=scfg['section_title']['margin_top_mm'] * mm,
        spaceAfter=scfg['section_title']['margin_bottom_mm'] * mm,
    )
    body_text = ParagraphStyle(
        'body_text',
        fontName=fn['regular'],
        fontSize=scfg['body_text']['font_size_pt'],
        textColor=HexColor(col['body_text']),
        leading=scfg['body_text']['line_height_mm'] * mm,
    )
    job_title = ParagraphStyle(
        'job_title',
        fontName=fn['bold'],
        fontSize=scfg['experience']['job_title']['font_size_pt'],
        textColor=HexColor(col['body_text']),
        spaceBefore=scfg['experience']['job_title']['margin_top_mm'] * mm,
    )
    company = ParagraphStyle(
        'company',
        fontName=fn['regular'],
        fontSize=scfg['experience']['company']['font_size_pt'],
        textColor=HexColor(col['company_name']),
    )
    date = ParagraphStyle(
        'date',
        fontName=fn['italic'],
        fontSize=scfg['experience']['date']['font_size_pt'],
        textColor=HexColor(col['date_text']),
        alignment=TA_RIGHT,
    )
    project_title = ParagraphStyle(
        'project_title',
        fontName=fn['bold'],
        fontSize=scfg['experience']['project']['title']['font_size_pt'],
        textColor=HexColor(col['project_title']),
        leftIndent=scfg['experience']['project']['title']['indent_mm'] * mm,
        spaceBefore=2 * mm,
    )
    team_info = ParagraphStyle(
        'team_info',
        fontName=fn['italic'],
        fontSize=scfg['experience']['project']['team_info']['font_size_pt'],
        textColor=HexColor(col['body_text']),
        leftIndent=scfg['experience']['project']['team_info']['indent_mm'] * mm,
    )
    skill_label = ParagraphStyle(
        'skill_label',
        fontName=fn['bold'],
        fontSize=scfg['skills']['label']['font_size_pt'],
        textColor=HexColor(col['skill_label']),
    )
    skill_value = ParagraphStyle(
        'skill_value',
        fontName=fn['regular'],
        fontSize=scfg['skills']['value']['font_size_pt'],
        textColor=HexColor(col['body_text']),
    )

    blt = scfg['experience']['project']['bullet']
    project_bullet = ParagraphStyle(
        'project_bullet',
        fontName=fn['regular'],
        fontSize=blt['font_size_pt'],
        textColor=HexColor(col['body_text']),
        leading=blt['line_height_mm'] * mm,
        bulletIndent=blt['indent_mm'] * mm,
        leftIndent=blt['indent_mm'] * mm + 8,
        spaceAfter=blt['spacing_mm'] * mm,
    )

    cert_cfg = scfg['certifications']
    cert_text = ParagraphStyle(
        'cert_text',
        fontName=fn['regular'],
        fontSize=cert_cfg['font_size_pt'],
        textColor=HexColor(col['body_text']),
        leading=cert_cfg['line_height_mm'] * mm,
        bulletIndent=cert_cfg['indent_mm'] * mm,
        leftIndent=cert_cfg['indent_mm'] * mm + 8,
    )

    lang_cfg = scfg['languages']
    lang_text = ParagraphStyle(
        'lang_text',
        fontName=fn['regular'],
        fontSize=lang_cfg['font_size_pt'],
        textColor=HexColor(col['body_text']),
        leading=lang_cfg['line_height_mm'] * mm,
        bulletIndent=lang_cfg['indent_mm'] * mm,
        leftIndent=lang_cfg['indent_mm'] * mm + 8,
    )

    return {
        'section_title': section_title,
        'body_text': body_text,
        'job_title': job_title,
        'company': company,
        'date': date,
        'project_title': project_title,
        'team_info': team_info,
        'skill_label': skill_label,
        'skill_value': skill_value,
        'project_bullet': project_bullet,
        'cert_text': cert_text,
        'lang_text': lang_text,
    }


def _section(story, title, styles, divider_cfg, colors):
    """Append a section title + divider."""
    story.append(Paragraph(escape(title), styles['section_title']))
    story.append(SectionDivider(divider_cfg, colors))


def build_story(data, scfg, styles, font_names, include_header_image: bool = True):
    """Assemble the full document story from CV data."""
    story = []
    col = scfg['colors']
    page_cfg = scfg['page']
    content_padding = page_cfg['content_padding_left_mm'] * mm
    content_width = PAGE_WIDTH - 2 * content_padding
    divider_cfg = scfg['section_title']['divider']

    # --- Header ---
    banner_rel = scfg['header'].get('banner_image')
    banner_path = os.path.join(BASE_DIR, banner_rel) if (banner_rel and include_header_image) else None

    story.append(HeaderBlock(
        data['name'], data['title'], data['contacts'],
        PAGE_WIDTH, content_padding,
        scfg['header'], col, font_names,
        banner_image_path=banner_path,
    ))
    story.append(NextPageTemplate('rest'))
    story.append(Spacer(1, 6 * mm))

    # --- Professional Summary ---
    if data.get('summary'):
        _section(story, 'PROFESSIONAL SUMMARY', styles, divider_cfg, col)
        story.append(Paragraph(escape(data['summary']), styles['body_text']))
        story.append(Spacer(1, 2 * mm))

    # --- Technical Skills ---
    if data.get('skills'):
        _section(story, 'TECHNICAL SKILLS', styles, divider_cfg, col)
        label_w = scfg['skills']['label']['column_width_mm'] * mm
        value_w = content_width - label_w

        skill_rows = []
        for s in data['skills']:
            skill_rows.append([
                Paragraph(escape(s['label'] + ':'), styles['skill_label']),
                Paragraph(escape(s['value']), styles['skill_value']),
            ])

        skill_table = Table(skill_rows, colWidths=[label_w, value_w])
        skill_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        story.append(skill_table)
        story.append(Spacer(1, 2 * mm))

    # --- Certifications & Teaching ---
    if data.get('certifications'):
        _section(story, 'CERTIFICATIONS & TEACHING', styles, divider_cfg, col)
        for cert in data['certifications']:
            story.append(Paragraph(escape(cert), styles['cert_text'], bulletText='\u2022'))
        story.append(Spacer(1, 2 * mm))

    # --- Professional Experience ---
    if data.get('experience'):
        _section(story, 'PROFESSIONAL EXPERIENCE', styles, divider_cfg, col)

        tag_config = dict(scfg['experience']['project']['tech_tag'])
        tag_config['bg_color'] = col['tech_tag_bg']
        tag_config['text_color'] = col['tech_tag_text']

        date_col_w = 130
        company_col_w = content_width - date_col_w

        for job in data['experience']:
            story.append(Paragraph(escape(job['job_title']), styles['job_title']))

            company_para = Paragraph(escape(job.get('company', '')), styles['company'])
            date_para = Paragraph(escape(job.get('date', '')), styles['date'])
            cd_table = Table(
                [[company_para, date_para]],
                colWidths=[company_col_w, date_col_w],
            )
            cd_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(cd_table)

            if job.get('description'):
                story.append(Spacer(1, 2 * mm))
                story.append(Paragraph(escape(job['description']), styles['body_text']))
                story.append(Spacer(1, 1 * mm))
                for bullet in job.get('bullets', []):
                    story.append(
                        Paragraph(escape(bullet), styles['project_bullet'], bulletText='\u2022')
                    )

            for proj in job.get('projects', []):
                story.append(Paragraph(escape(proj['name']), styles['project_title']))
                if proj.get('tech_tags'):
                    story.append(TechTagRow(proj['tech_tags'], tag_config, font_names['regular']))
                if proj.get('team_info'):
                    story.append(Paragraph(escape(proj['team_info']), styles['team_info']))
                for bullet in proj.get('bullets', []):
                    story.append(
                        Paragraph(escape(bullet), styles['project_bullet'], bulletText='\u2022')
                    )

        story.append(Spacer(1, 2 * mm))

    # --- Education ---
    if data.get('education'):
        _section(story, 'EDUCATION', styles, divider_cfg, col)
        date_col_w = 130
        edu_col_w = content_width - date_col_w
        for edu in data['education']:
            story.append(Paragraph(escape(edu['degree']), styles['job_title']))
            inst_para = Paragraph(escape(edu.get('institution', '')), styles['company'])
            date_para = Paragraph(escape(edu.get('date', '')), styles['date'])
            edu_table = Table(
                [[inst_para, date_para]],
                colWidths=[edu_col_w, date_col_w],
            )
            edu_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(edu_table)
        story.append(Spacer(1, 2 * mm))

    # --- Languages ---
    if data.get('languages'):
        _section(story, 'LANGUAGES', styles, divider_cfg, col)
        for lang in data['languages']:
            text = f"{lang['language']} \u2014 {lang['level']}"
            story.append(Paragraph(escape(text), styles['lang_text'], bulletText='\u2022'))

    return story


def generate_pdf(styles_path, data_path, output_path):
    font_names = register_fonts()

    scfg = load_json(styles_path)
    data = load_json(data_path)
    styles = create_styles(scfg, font_names)

    page_cfg = scfg['page']
    content_padding = page_cfg['content_padding_left_mm'] * mm
    content_width = PAGE_WIDTH - 2 * content_padding
    bottom_margin = page_cfg['margin_bottom_mm'] * mm
    rest_top_margin = 28

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    first_frame = Frame(
        0, bottom_margin,
        PAGE_WIDTH, PAGE_HEIGHT - bottom_margin,
        leftPadding=content_padding, rightPadding=content_padding,
        topPadding=0, bottomPadding=0,
        id='first_frame',
    )
    rest_frame = Frame(
        content_padding, bottom_margin,
        content_width, PAGE_HEIGHT - bottom_margin - rest_top_margin,
        leftPadding=0, rightPadding=0,
        topPadding=0, bottomPadding=0,
        id='rest_frame',
    )

    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=0,
        bottomMargin=bottom_margin,
        leftMargin=0,
        rightMargin=0,
    )
    doc.addPageTemplates([
        PageTemplate(id='first', frames=[first_frame]),
        PageTemplate(id='rest', frames=[rest_frame]),
    ])

    story = build_story(data, scfg, styles, font_names)
    doc.build(story)
    print(f'PDF generated: {output_path}')


def build_pdf_bytes(cv_data: dict, include_header_image: bool = True) -> bytes:
    """Build PDF in memory from CV dict (used by FastAPI)."""
    import tempfile

    styles_path = os.path.join(BASE_DIR, 'styles.json')
    font_names = register_fonts()
    scfg = load_json(styles_path)
    styles = create_styles(scfg, font_names)

    page_cfg = scfg['page']
    content_padding = page_cfg['content_padding_left_mm'] * mm
    content_width = PAGE_WIDTH - 2 * content_padding
    bottom_margin = page_cfg['margin_bottom_mm'] * mm
    rest_top_margin = 28

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        first_frame = Frame(
            0, bottom_margin,
            PAGE_WIDTH, PAGE_HEIGHT - bottom_margin,
            leftPadding=content_padding, rightPadding=content_padding,
            topPadding=0, bottomPadding=0,
            id='first_frame',
        )
        rest_frame = Frame(
            content_padding, bottom_margin,
            content_width, PAGE_HEIGHT - bottom_margin - rest_top_margin,
            leftPadding=0, rightPadding=0,
            topPadding=0, bottomPadding=0,
            id='rest_frame',
        )

        doc = BaseDocTemplate(
            tmp_path,
            pagesize=A4,
            topMargin=0,
            bottomMargin=bottom_margin,
            leftMargin=0,
            rightMargin=0,
        )
        doc.addPageTemplates([
            PageTemplate(id='first', frames=[first_frame]),
            PageTemplate(id='rest', frames=[rest_frame]),
        ])

        story = build_story(cv_data, scfg, styles, font_names, include_header_image)
        doc.build(story)

        with open(tmp_path, 'rb') as f:
            return f.read()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


if __name__ == '__main__':
    styles_path = sys.argv[1] if len(sys.argv) > 1 else 'styles.json'
    data_path = sys.argv[2] if len(sys.argv) > 2 else 'data.json'
    output_path = sys.argv[3] if len(sys.argv) > 3 else 'output/CV_Generated.pdf'
    generate_pdf(styles_path, data_path, output_path)
