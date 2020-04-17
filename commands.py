import click
from flask.cli import with_appcontext
from flask.globals import current_app
from openpyxl import load_workbook
from db_models import db, Manuscript
import asyncio

@click.command()
@click.argument('filename')
@click.option('--sheet', default=1, help='Sheet to use in a multisheet file')
@with_appcontext
def ingest(filename, sheet):
    def get_sheet():
        wb = load_workbook(filename)
        return wb.get_sheet_by_name(wb.get_sheet_names()[sheet-1])

    def clean_decimal(value):
        if type(value) == float:
            return int(value)
        return value

    created = updated = 0
    async def process_row(row):
        nonlocal created, updated
        try:
            heb_name = row[0].value
            print(f'{heb_name}...', end='')
            iiif_manifest_url = row[5].value
            if not iiif_manifest_url:
                print('no manifest', end='')
                return

            manuscript = Manuscript.query.filter_by(heb_name=heb_name).first()
            if not manuscript:
                print('creating', end='')
                created += 1
                manuscript = Manuscript()
                manuscript.heb_name = heb_name
                db.session.add(manuscript)
            else:
                updated += 1
                print('updating', end='')
            manuscript.eng_name = None  # No english name for now
            manuscript.estimated_date = clean_decimal(row[1].value)
            manuscript.shelf_no = clean_decimal(row[2].value)
            manuscript.catalog_no = clean_decimal(row[3].value)
            manuscript.external_url = row[4].value
            manuscript.iiif_manifest_url = iiif_manifest_url
            manuscript.notes = row[8].value
        except Exception as e:
            print(str(e), end='')
        finally:

            print()

    async def process_sheet(sheet):
        row_tasks = [process_row(row) for row in sheet.iter_rows(min_row=2)]
        await asyncio.wait(row_tasks)
        
    sheet = get_sheet()
    asyncio.run(process_sheet(sheet))
    db.session.commit()
    print(f'Created {created} manuscripts, updated {updated} manuscripts')


def init_app(app):
    app.cli.add_command(ingest)
