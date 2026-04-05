"""Custom Flowable components for the CV PDF generator."""

import os

from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Flowable
from reportlab.pdfbase import pdfmetrics


class HeaderBlock(Flowable):
    """Full-width header with optional banner image over a solid background."""

    def __init__(self, name, title, contacts, page_width, content_padding,
                 header_cfg, colors, font_names, banner_image_path=None):
        Flowable.__init__(self)
        self.name_text = name
        self.title_text = title
        self.contacts = contacts
        self.page_width = page_width
        self.content_padding = content_padding

        self.height = header_cfg['height_mm'] * mm
        self.padding_top = header_cfg['padding_top_mm'] * mm

        self.name_font_size = header_cfg['name']['font_size_pt']
        self.title_font_size = header_cfg['title']['font_size_pt']
        self.title_margin_top = header_cfg['title']['margin_top_mm'] * mm
        self.contacts_font_size = header_cfg['contacts']['font_size_pt']
        self.contacts_margin_top = header_cfg['contacts']['margin_top_mm'] * mm
        self.contacts_separator = header_cfg['contacts']['separator']

        self.bg_color = HexColor(colors['header_bg'])
        self.name_color = HexColor(colors['header_name'])
        self.title_color = HexColor(colors['header_title'])
        self.contacts_color = HexColor(colors['header_contacts'])

        self.banner_name_color = HexColor(colors.get('header_banner_name', '#FFFFFF'))
        self.banner_title_color = HexColor(colors.get('header_banner_title', '#FFFFFF'))
        self.banner_contacts_color = HexColor(colors.get('header_banner_contacts', '#D0E8E6'))

        self.font_bold = font_names['bold']
        self.font_regular = font_names['regular']

        self.banner_image_path = banner_image_path
        self.banner_overlay_opacity = header_cfg.get('banner_overlay_opacity', 0.4)

    def wrap(self, availWidth, availHeight):
        return (availWidth, self.height)

    def _has_banner(self):
        return bool(self.banner_image_path and os.path.isfile(self.banner_image_path))

    def draw(self):
        c = self.canv
        has_banner = self._has_banner()

        c.setFillColor(self.bg_color)
        c.rect(
            -self.content_padding, 0,
            self.page_width, self.height,
            fill=1, stroke=0,
        )

        if has_banner:
            img = ImageReader(self.banner_image_path)
            c.drawImage(
                img,
                -self.content_padding, 0,
                width=self.page_width,
                height=self.height,
                preserveAspectRatio=False,
                mask='auto',
            )
            c.saveState()
            c.setFillColor(self.bg_color)
            c.setFillAlpha(self.banner_overlay_opacity)
            c.rect(
                -self.content_padding, 0,
                self.page_width, self.height,
                fill=1, stroke=0,
            )
            c.restoreState()

        name_clr = self.banner_name_color if has_banner else self.name_color
        title_clr = self.banner_title_color if has_banner else self.title_color
        contacts_clr = self.banner_contacts_color if has_banner else self.contacts_color

        name_y = self.height - self.padding_top - self.name_font_size
        c.setFillColor(name_clr)
        c.setFont(self.font_bold, self.name_font_size)
        c.drawString(0, name_y, self.name_text.upper())

        title_y = name_y - self.title_font_size - self.title_margin_top
        c.setFillColor(title_clr)
        c.setFont(self.font_regular, self.title_font_size)
        c.drawString(0, title_y, self.title_text)

        contacts_y = title_y - self.contacts_font_size - self.contacts_margin_top
        c.setFillColor(contacts_clr)
        c.setFont(self.font_regular, self.contacts_font_size)
        c.drawString(0, contacts_y, self.contacts_separator.join(self.contacts))


class SectionDivider(Flowable):
    """Two-color horizontal divider: blue segment then gray."""

    def __init__(self, divider_cfg, colors):
        Flowable.__init__(self)
        self.blue_width = divider_cfg['blue_width_mm'] * mm
        self.blue_line_width = divider_cfg['blue_line_width_pt']
        self.gray_line_width = divider_cfg['gray_line_width_pt']
        self.blue_color = HexColor(colors['divider_blue'])
        self.gray_color = HexColor(colors['divider_gray'])
        self.height = divider_cfg.get('spacing_after_mm', 2) * mm

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        y = self.height / 2

        c.setLineWidth(self.blue_line_width)
        c.setStrokeColor(self.blue_color)
        c.line(0, y, self.blue_width, y)

        c.setLineWidth(self.gray_line_width)
        c.setStrokeColor(self.gray_color)
        c.line(self.blue_width, y, self.width, y)


class TechTagRow(Flowable):
    """Inline technology badges that auto-wrap when exceeding available width."""

    def __init__(self, tags, config, font_name):
        Flowable.__init__(self)
        self.tags = tags
        self.font_name = font_name
        self.font_size = config.get('font_size_pt', 7.5)
        self.pad_h = config.get('padding_h_mm', 2.5) * mm
        self.pad_v = config.get('padding_v_mm', 1) * mm
        self.gap = config.get('gap_mm', 1.5) * mm
        self.indent = config.get('indent_mm', 4) * mm
        self.radius = config.get('border_radius_mm', 1) * mm
        self.bg_color = HexColor(config.get('bg_color', '#E8F0F8'))
        self.text_color = HexColor(config.get('text_color', '#29629B'))
        self._rows = []

    def wrap(self, availWidth, availHeight):
        if not self.tags:
            return (availWidth, 0)
        self._avail = availWidth
        self._do_layout()
        return (availWidth, self.height)

    def _do_layout(self):
        self._rows = []
        row = []
        x = self.indent
        tag_h = self.font_size + 2 * self.pad_v
        self._row_step = tag_h + 3

        for tag in self.tags:
            tw = pdfmetrics.stringWidth(tag, self.font_name, self.font_size)
            w = tw + 2 * self.pad_h
            if row and x + w > self._avail:
                self._rows.append(row)
                row = []
                x = self.indent
            row.append((tag, x, w))
            x += w + self.gap

        if row:
            self._rows.append(row)
        self.height = len(self._rows) * self._row_step + 2

    def draw(self):
        c = self.canv
        tag_h = self.font_size + 2 * self.pad_v

        for i, row in enumerate(self._rows):
            base_y = self.height - (i + 1) * self._row_step
            for tag, x, w in row:
                c.setFillColor(self.bg_color)
                c.roundRect(x, base_y, w, tag_h, self.radius, fill=1, stroke=0)

                c.setFillColor(self.text_color)
                c.setFont(self.font_name, self.font_size)
                c.drawString(x + self.pad_h, base_y + self.pad_v, tag)
