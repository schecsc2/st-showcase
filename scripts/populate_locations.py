import csv
import json
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent.parent
WORKBOOK_PATH = ROOT / 'data/event_content/Poster Tracking_Current.xlsx'
SIDEWALK_DEMOS_PATH = ROOT / 'data/event_content/sidewalk_demos.csv'
FEATURE_BOOTHS_PATH = ROOT / 'data/event_content/feature_booths.md'
SCT_GEOMETRY_PATH = ROOT / 'data/live/map/geometries/scts'
LOCATIONS_PATH = ROOT / 'data/live/map/locations.json'
MAIN_NAMESPACE = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
RELATIONSHIP_NAMESPACE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PACKAGE_RELATIONSHIP_NAMESPACE = 'http://schemas.openxmlformats.org/package/2006/relationships'
NAMESPACES = {'main': MAIN_NAMESPACE}
REQUIRED_COLUMNS = ['Map Location', 'IRAD/PG Title', 'Presenter', 'Category (Primary)', 'Description', 'Demo', 'Distribution', 'RRT Status']


def get_cell_column(reference):
    return ''.join(character for character in reference if character.isalpha())


def get_cell_value(cell, shared_strings):
    if cell.get('t') == 'inlineStr':
        return ''.join(node.text or '' for node in cell.findall('.//main:t', NAMESPACES))

    value = cell.find('main:v', NAMESPACES)

    if value is None or value.text is None:
        return ''

    if cell.get('t') == 's':
        return shared_strings[int(value.text)]

    return value.text


def read_workbook_rows():
    with zipfile.ZipFile(WORKBOOK_PATH) as workbook:
        shared_strings = []

        if 'xl/sharedStrings.xml' in workbook.namelist():
            root = ElementTree.fromstring(workbook.read('xl/sharedStrings.xml'))
            shared_strings = [
                ''.join(node.text or '' for node in item.findall('.//main:t', NAMESPACES))
                for item in root.findall('main:si', NAMESPACES)
            ]

        root = ElementTree.fromstring(workbook.read('xl/workbook.xml'))
        sheet = root.find('main:sheets/main:sheet', NAMESPACES)
        relationship_id = sheet.get(f'{{{RELATIONSHIP_NAMESPACE}}}id')
        relationships = ElementTree.fromstring(workbook.read('xl/_rels/workbook.xml.rels'))
        targets = {
            relationship.get('Id'): relationship.get('Target')
            for relationship in relationships.findall(f'{{{PACKAGE_RELATIONSHIP_NAMESPACE}}}Relationship')
        }
        target = targets[relationship_id]
        sheet_path = target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('xl', target))
        root = ElementTree.fromstring(workbook.read(sheet_path))
        rows = []

        for row in root.findall('main:sheetData/main:row', NAMESPACES):
            rows.append({
                get_cell_column(cell.get('r')): get_cell_value(cell, shared_strings)
                for cell in row.findall('main:c', NAMESPACES)
            })

    return rows


def read_feature_booths():
    feature_booths = {}
    title = None

    for line in FEATURE_BOOTHS_PATH.read_text().splitlines():
        if line.startswith('- '):
            title = line[2:].strip()
            feature_booths[title] = ''
        elif title and line.strip().startswith('- '):
            feature_booths[title] = line.strip()[2:].strip()

    return feature_booths


def read_sct_coordinates():
    coordinates = {}

    for geometry_path in SCT_GEOMETRY_PATH.iterdir():
        match = re.search(r'\bd="M\s*(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)', geometry_path.read_text())

        if match:
            coordinates[geometry_path.name] = {
                'x': float(match.group(1)),
                'y': float(match.group(2))
            }

    return coordinates


def populate_locations():
    rows = read_workbook_rows()
    headers = {value.strip(): column for column, value in rows[0].items()}
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in headers]

    if missing_columns:
        raise ValueError(f'Missing required columns: {", ".join(missing_columns)}')

    with LOCATIONS_PATH.open() as locations_file:
        locations = json.load(locations_file)

    with SIDEWALK_DEMOS_PATH.open(newline='') as demos_file:
        sidewalk_demos = list(csv.DictReader(demos_file))

    feature_booths = read_feature_booths()
    sct_coordinates = read_sct_coordinates()
    sct_geometry_ids = {
        'Achieving Robust Homeland Defense': 'homeland_defense',
        "Revitalizing the Nation's Strategic Capabilities": 'strategic_capabilities',
        'Accelerating Warfighting Capabilities for the Pacific Theater': 'warfighting_capabilities',
        'Enabling Space Superiority': 'space_superiority'
    }

    for sct in locations.get('scts', []):
        if feature_booths.get(sct['title']):
            sct['description'] = feature_booths[sct['title']]
        if sct_geometry_ids.get(sct['title']) in sct_coordinates:
            sct.update(sct_coordinates[sct_geometry_ids[sct['title']]])

    locations['demos'] = [{
        'id': 'sidewalk',
        'title': 'Demos',
        'shape': 'zone',
        'demos': [
            {
                'id': f'sidewalk-demo-{index}',
                'title': demo['demo_name'].strip(),
                'authors': (demo.get('author') or '').strip(),
                'description': demo['description'].strip()
            }
            for index, demo in enumerate(sidewalk_demos, start=1)
        ]
    }] + [demo for demo in locations['demos'] if demo['id'] != 'sidewalk']

    neighborhoods = {neighborhood['title']: neighborhood for neighborhood in locations['neighborhoods']}

    for neighborhood in neighborhoods.values():
        neighborhood['posters'] = []

    included = 0
    skipped = 0

    poster_rows = []

    for row_number, row in enumerate(rows[1:], start=2):
        if row.get(headers['RRT Status'], '').strip().lower() != 'approved':
            skipped += 1
            continue

        category = row.get(headers['Category (Primary)'], '').strip()
        category = re.sub(r'^\d+\.\s*', '', category)

        if category not in neighborhoods:
            skipped += 1
            continue

        poster_rows.append((row_number, row, category))

    def map_location_key(value):
        parts = tuple(int(part) for part in value.split('.') if part.isdigit())

        return (1,) if not parts else (0,) + parts

    for row_number, row, category in sorted(poster_rows, key=lambda entry: map_location_key(entry[1].get(headers['Map Location'], '').strip())):
        is_distro_a = re.sub(r'[^a-z]', '', row.get(headers['Distribution'], '').lower()) == 'distroanotcui'
        is_demo = row.get(headers['Demo'], '').strip() == 'Yes'
        item = {
            'id': str(row_number),
            'title': row.get(headers['IRAD/PG Title'], '').strip() if is_distro_a else f'{category} {"Demo" if is_demo else "Poster"}',
            'authors': row.get(headers['Presenter'], '').strip(),
            'description': row.get(headers['Description'], '').strip() if is_distro_a else f'This {"demo" if is_demo else "poster"} will be available for viewing during the morning session only'
        }

        if is_demo:
            item['demo'] = True

        neighborhoods[category]['posters'].append(item)

        included += 1

    with LOCATIONS_PATH.open('w') as locations_file:
        json.dump(locations, locations_file, indent=2, ensure_ascii=False)
        locations_file.write('\n')

    print(f'Updated {LOCATIONS_PATH.relative_to(ROOT)} with {included} records; skipped {skipped}.')


if __name__ == '__main__':
    populate_locations()
