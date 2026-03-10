  import csv, json, os, urllib.request                                                               
  from datetime import datetime

  SHEET_URL = os.environ.get('SHEET_CSV_URL', '')

  if not SHEET_URL:
      print('Error: SHEET_CSV_URL not set')
      exit(1)

  with urllib.request.urlopen(SHEET_URL) as r:
      content = r.read().decode('utf-8')

  lines = content.splitlines()
  reader = csv.DictReader(lines)

  shows_map = {}
  show_order = []

  for row in reader:
      if not row.get('show_name') or not row.get('city'):
          continue

      name = row['show_name'].strip()
      if name not in shows_map:
          show_order.append(name)
          shows_map[name] = {
              'name': name,
              'performer': row['performer'].strip(),
              'image': row['image'].strip(),
              'sessions': []
          }

      shows_map[name]['sessions'].append({
          'city': row['city'].strip(),
          'venue': row['venue'].strip(),
          'showTime': row['showTime'].strip(),
          'ticketSaleTime': row.get('ticketSaleTime', '').strip(),
          'price': row.get('price', '').strip(),
          'ticketLink': row.get('ticketLink', '').strip(),
          'link_damai':  row.get('link_damai', '').strip(),
          'link_maoyan': row.get('link_maoyan', '').strip(),
          'link_other':  row.get('link_other', '').strip(),
          'source': 'official'
      })

  for show in shows_map.values():
      show['sessions'].sort(key=lambda s: s['showTime'])

  shows = []
  for i, name in enumerate(show_order, start=1):
      show = shows_map[name]
      show['id'] = i
      for j, s in enumerate(show['sessions'], start=1):
          s['id'] = f"s{i}_{j}"
      shows.append(show)

  now = datetime.now().strftime('%Y-%m-%d %H:%M')

  def next_showtime(show):
      upcoming = [s['showTime'] for s in show['sessions'] if s['showTime'] >= now]
      return min(upcoming) if upcoming else '9999'

  shows.sort(key=next_showtime)

  with open('data.json', 'w', encoding='utf-8') as f:
      json.dump(shows, f, ensure_ascii=False, indent=2)

  print(f'data.json updated: {len(shows)} shows, {sum(len(s["sessions"]) for s in shows)} sessions')
