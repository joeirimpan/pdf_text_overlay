"""Pdf text overlay."""
# -*- coding: utf-8 -*-
import StringIO

from pyPdf import PdfFileReader
from pyPdf import PdfFileWriter

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


class WriteToPdf(object):
    """Write text on top of pdf."""

    def __init__(
        self, original_pdf, configuration,
        values, font=None, font_size=10
    ):
        """
        Iitialise.

        :param original_pdf (file obj): original pdf file object
        :param configuration (dict): configuration dict
        :param values (dict): values to be printed
        :param font (file obj): font
        """
        self.font_size = font_size

        pdfmetrics.registerFont(TTFont('font_style', font))

        self.values = values
        self.original_pdf = original_pdf
        self.configuration = configuration

    # create a new PDF with Reportlab
    def create_pew_pdf(self, configuration):
        """
        Return pdf object.

        :param configuration: configuration data
        """
        pdf = StringIO.StringIO()
        values = self.values

        can = canvas.Canvas(pdf, pagesize=letter)
        can.setFont('font_style', self.font_size)

        for config_data in configuration:

            key = config_data['name']
            self.set_font_size(can, config_data)
            can.setStrokeColorRGB(0,0,0)
            can.setFillColorRGB(
                    0,0,0
                )

            if 'conditional_coordinates' in config_data:
                for co_ordinates in config_data['conditional_coordinates']:
                    if co_ordinates['if_value'] == values[key]:
                        x = co_ordinates['x-coordinate']
                        y = co_ordinates['y-coordinate']
                        if co_ordinates['print_pattern'] is False:
                            value = co_ordinates['if_value']
                        else:
                            value = co_ordinates['print_pattern']
                try:
                    can.drawString(x, y, value)
                except NameError:
                    raise ValueError('could not find co ordinates for key({}) value {}'.format(key, values[key]))
            elif 'draw_shape' in config_data:

                from reportlab.lib.units import inch
                # move the origin up and to the left

                can.translate(inch,inch)

                can.setStrokeColorRGB(0,0,0)
                #     config_data['draw_shape']['r'],
                #     config_data['draw_shape']['g'],
                #     config_data['draw_shape']['b']
                # )
                can.setFillColorRGB(
                    config_data['draw_shape']['r'],
                    config_data['draw_shape']['g'],
                    config_data['draw_shape']['b']
                )

                if config_data['draw_shape']['shape'] == 'Line':


                    x0 = config_data['draw_shape']['x0-coordinate']
                    x1 = config_data['draw_shape']['x1-coordinate']
                    y0 = config_data['draw_shape']['y0-coordinate']
                    y1 = config_data['draw_shape']['y1-coordinate']

                    can.line(x0*inch,y0*inch, x1*inch, y1*inch)
                if config_data['draw_shape']['shape'] == 'Rectangle':
                    x0 = config_data['draw_shape']['x0-coordinate']
                    x1 = config_data['draw_shape']['x1-coordinate']
                    y0 = config_data['draw_shape']['y0-coordinate']
                    y1 = config_data['draw_shape']['y1-coordinate']
                    fill = config_data['draw_shape'].get('fill', 1)

                    can.rect(x0*inch,y0*inch, x1*inch, y1*inch, fill=fill)
            elif 'image' in config_data:
                x = config_data['image']['x-coordinate']
                y = config_data['image']['y-coordinate']
                w = config_data['image']['width']
                h = config_data['image']['height']
                can.drawImage(values[key], x, y, width=w, height=h)

            else:
                x = config_data['x-coordinate']
                y = config_data['y-coordinate']
                value = config_data.get('value', None)

                if not value:
                    value = values[key]

                try:
                    can.drawString(x, y, value)
                except NameError:
                    raise ValueError('could not find co ordinates for key({}) value {}'.format(key, values[key]))

        can.save()

        return pdf

    def set_font_size(self, can, config_data):
        """Set font size."""
        if 'font_size' in config_data:
            can.setFont('font_style', config_data["font_size"])

    def parse_configuration(self, page_number):
        """
        Return configuration variables.

        :params page_number: pdf page number
        """
        configuration = self.configuration
        for i in range(len(configuration)):
            if configuration[i]['page_number'] == page_number:
                return configuration[i]['variables']
        return -1

    def edit_and_save_pdf(self):
        """Return file object."""
        original_pdf = PdfFileReader(self.original_pdf)
        output = PdfFileWriter()
        for i in range(original_pdf.numPages):
            configuration = self.parse_configuration(i)
            page = original_pdf.getPage(i)
            if configuration != -1:
                new_pdf = PdfFileReader(self.create_pew_pdf(configuration))
                page.mergePage(new_pdf.getPage(0))

            output.addPage(page)
        return output


def pdf_writer(original_pdf, configuration, data, font, font_size=10):
    """
    Return file object.

    :param original_pdf (file obj): original pdf file object
    :param configuration (dict): configuration dict
    :param values (dict): values to be printed
    :param font (file obj): font
    """
    x = WriteToPdf(original_pdf, configuration, data, font)
    output = x.edit_and_save_pdf()
    return output

version = 0.1
