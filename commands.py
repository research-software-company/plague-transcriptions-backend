import click
from flask.cli import with_appcontext
from flask.globals import current_app
from openpyxl import load_workbook
from db_models import db, Manuscript

@click.command()
@click.argument('filename')
@click.option('--sheet', default=1, help='Sheet to use in a multisheet file')
@with_appcontext
def ingest(filename, sheet):
    def get_sheet():
        wb = load_workbook(filename)
        return wb.get_sheet_by_name(wb.get_sheet_names()[sheet-1])

    def process_row(row):
        heb_name = row[0]
        iiif_manifest_url = row[5]
        if not iiif_manifest_url:
            return

        manuscript = Manuscript.query.filter_by(heb_name=heb_name).first()
        if not manuscript:
            manuscript = Manuscript()
            manuscript.heb_name = heb_name
            db.session.add(manuscript)
        manuscript.eng_name = None  # No english name for now
        manuscript.estimated_date = row[1]
        manuscript.shelf_no = row[2]
        manuscript.catalog_no = row[3]
        manuscript.external_url = row[4]
        manuscript.iiif_manifest_url = iiif_manifest_url
        manuscript.notes = row[8]

    sheet = get_sheet()
    for row in sheet.iter_rows(min_row=2, values_only=True):
        process_row(row)
    db.session.commit()


def init_app(app):
    app.cli.add_command(ingest)
