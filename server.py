#!/usr/bin/env python3
"""
Baseline v3 — Personal Health & Fitness Tracker
Self-hosted. Multi-profile. No cloud required.

New in v3:
- Health Auto Export webhook receiver
- GPX file storage and serving
- Workout history with route metadata
- 60-day data pruning
- Dashboard auto-refresh support
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory, Response

app = Flask(__name__, static_folder='public')

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
GPX_DIR  = os.path.join(DATA_DIR, 'gpx')
DB_FILE  = os.path.join(DATA_DIR, 'baseline.json')

# ── Database helpers ──────────────────────────────────────────

def load_db():
    if not os.path.exists(DB_FILE):
        return {'profiles': {}}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(db):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = DB_FILE + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(db, f, indent=2)
    os.replace(tmp, DB_FILE)

def hash_pin(pin):
    return hashlib.sha256(str(pin).encode()).hexdigest()

def get_empty_profile():
    return {'profile': {}, 'logs': [], 'food': [], 'workouts': [], 'kv': {}}

def prune_old_data(profile, days=60):
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    profile['logs'] = [l for l in profile.get('logs', []) if l.get('date', '') >= cutoff]
    profile['food'] = [f for f in profile.get('food', []) if f.get('date', '') >= cutoff]
    return profile

# ── Static ────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

# ── Profiles ──────────────────────────────────────────────────

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    db = load_db()
    result = []
    for pid, p in db['profiles'].items():
        result.append({'id': pid, 'name': p.get('name','User'), 'color': p.get('color','#5b8af0'),
                       'avatar': p.get('avatar',''), 'goal': p.get('profile',{}).get('goal',''),
                       'has_pin': bool(p.get('pin'))})
    return jsonify(result)

@app.route('/api/profiles', methods=['POST'])
def create_profile():
    db = load_db()
    data = request.json
    pid = 'p_' + datetime.now().strftime('%Y%m%d%H%M%S%f')
    entry = get_empty_profile()
    entry['name'] = data.get('name', 'User')
    entry['color'] = data.get('color', '#5b8af0')
    entry['avatar'] = data.get('avatar', '')
    if data.get('pin'):
        entry['pin'] = hash_pin(data['pin'])
    db['profiles'][pid] = entry
    save_db(db)
    return jsonify({'id': pid, 'name': entry['name']})

@app.route('/api/profiles/<pid>', methods=['PUT'])
def update_profile_meta(pid):
    db = load_db()
    if pid not in db['profiles']:
        return jsonify({'error': 'not found'}), 404
    data = request.json
    for k in ('name', 'color', 'avatar'):
        if k in data: db['profiles'][pid][k] = data[k]
    if 'pin' in data:
        db['profiles'][pid]['pin'] = hash_pin(data['pin']) if data['pin'] else ''
    save_db(db)
    return jsonify({'ok': True})

@app.route('/api/profiles/<pid>', methods=['DELETE'])
def delete_profile(pid):
    db = load_db()
    if pid in db['profiles']:
        del db['profiles'][pid]
        save_db(db)
    return jsonify({'ok': True})

@app.route('/api/profiles/<pid>/verify', methods=['POST'])
def verify_pin(pid):
    db = load_db()
    p = db['profiles'].get(pid)
    if not p: return jsonify({'ok': False}), 404
    if not p.get('pin'): return jsonify({'ok': True})
    return jsonify({'ok': hash_pin(request.json.get('pin','')) == p['pin']})

@app.route('/api/profiles/<pid>/data', methods=['GET'])
def get_profile_data(pid):
    db = load_db()
    p = db['profiles'].get(pid)
    if not p: return jsonify({'error': 'not found'}), 404
    return jsonify({
        'profile':  p.get('profile', {}),
        'kv':       p.get('kv', {}),
        'logs':     sorted(p.get('logs', []), key=lambda x: x.get('date',''), reverse=True),
        'food':     p.get('food', []),
        'workouts': sorted(p.get('workouts', []), key=lambda x: x.get('date',''), reverse=True)
    })

@app.route('/api/profiles/<pid>/profile', methods=['POST'])
def save_profile(pid):
    db = load_db()
    if pid not in db['profiles']: return jsonify({'error': 'not found'}), 404
    db['profiles'][pid]['profile'] = request.json
    save_db(db)
    return jsonify({'ok': True})

@app.route('/api/profiles/<pid>/kv/<key>', methods=['GET'])
def get_kv(pid, key):
    db = load_db()
    return jsonify({'value': db['profiles'].get(pid, {}).get('kv', {}).get(key)})

@app.route('/api/profiles/<pid>/kv/<key>', methods=['POST'])
def set_kv(pid, key):
    db = load_db()
    if pid not in db['profiles']: return jsonify({'error': 'not found'}), 404
    db['profiles'][pid].setdefault('kv', {})[key] = request.json.get('value')
    save_db(db)
    return jsonify({'ok': True})

# ── Logs ──────────────────────────────────────────────────────

@app.route('/api/profiles/<pid>/logs', methods=['GET'])
def get_logs(pid):
    db = load_db()
    logs = db['profiles'].get(pid, {}).get('logs', [])
    return jsonify(sorted(logs, key=lambda x: x.get('date',''), reverse=True))

@app.route('/api/profiles/<pid>/logs', methods=['POST'])
def save_log(pid):
    db = load_db()
    if pid not in db['profiles']: return jsonify({'error': 'not found'}), 404
    entry = request.json
    logs = db['profiles'][pid].get('logs', [])
    logs = [l for l in logs if l.get('date') != entry.get('date')]
    logs.append(entry)
    db['profiles'][pid]['logs'] = logs
    save_db(db)
    return jsonify({'ok': True})

# ── Food ──────────────────────────────────────────────────────

@app.route('/api/profiles/<pid>/food', methods=['GET'])
def get_food(pid):
    db = load_db()
    return jsonify(db['profiles'].get(pid, {}).get('food', []))

@app.route('/api/profiles/<pid>/food', methods=['POST'])
def add_food(pid):
    db = load_db()
    if pid not in db['profiles']: return jsonify({'error': 'not found'}), 404
    entry = request.json
    entry['created_at'] = datetime.now().isoformat()
    db['profiles'][pid].setdefault('food', []).append(entry)
    save_db(db)
    return jsonify({'ok': True})

# ── Workouts ──────────────────────────────────────────────────

@app.route('/api/profiles/<pid>/workouts', methods=['GET'])
def get_workouts(pid):
    db = load_db()
    workouts = db['profiles'].get(pid, {}).get('workouts', [])
    return jsonify(sorted(workouts, key=lambda x: x.get('date',''), reverse=True))

@app.route('/api/profiles/<pid>/workouts', methods=['POST'])
def save_workout(pid):
    db = load_db()
    if pid not in db['profiles']: return jsonify({'error': 'not found'}), 404
    entry = request.json
    entry.setdefault('id', 'w_' + datetime.now().strftime('%Y%m%d%H%M%S%f'))
    workouts = db['profiles'][pid].get('workouts', [])
    workouts = [w for w in workouts if w.get('id') != entry['id']]
    workouts.append(entry)
    db['profiles'][pid]['workouts'] = workouts
    save_db(db)
    return jsonify({'ok': True, 'id': entry['id']})

# ── GPX files ─────────────────────────────────────────────────

@app.route('/api/profiles/<pid>/gpx', methods=['POST'])
def upload_gpx(pid):
    os.makedirs(GPX_DIR, exist_ok=True)
    gpx_id = 'gpx_' + datetime.now().strftime('%Y%m%d%H%M%S%f')
    gpx_path = os.path.join(GPX_DIR, f'{pid}_{gpx_id}.gpx')
    if request.content_type and 'multipart' in request.content_type:
        f = request.files.get('file')
        if f: f.save(gpx_path)
    else:
        with open(gpx_path, 'wb') as f:
            f.write(request.get_data())
    return jsonify({'ok': True, 'gpx_id': gpx_id})

@app.route('/api/profiles/<pid>/gpx/<gpx_id>', methods=['GET'])
def get_gpx(pid, gpx_id):
    gpx_path = os.path.join(GPX_DIR, f'{pid}_{gpx_id}.gpx')
    if not os.path.exists(gpx_path):
        return jsonify({'error': 'not found'}), 404
    with open(gpx_path, 'r') as f:
        content = f.read()
    return Response(content, mimetype='application/gpx+xml')

@app.route('/api/profiles/<pid>/gpx', methods=['GET'])
def list_gpx(pid):
    os.makedirs(GPX_DIR, exist_ok=True)
    files = [f for f in os.listdir(GPX_DIR) if f.startswith(pid + '_') and f.endswith('.gpx')]
    result = []
    for fname in sorted(files, reverse=True):
        gpx_id = fname[len(pid)+1:-4]
        stat = os.stat(os.path.join(GPX_DIR, fname))
        result.append({'gpx_id': gpx_id, 'filename': fname,
                       'size_kb': round(stat.st_size/1024, 1),
                       'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()})
    return jsonify(result)

# ── Health Auto Export webhook ────────────────────────────────

@app.route('/api/profiles/<pid>/healthautoexport', methods=['POST'])
def health_auto_export(pid):
    """
    Webhook for Health Auto Export iOS app.
    In Health Auto Export: Automation > REST API > this URL
    Format: JSON v2, schedule: Hourly
    """
    db = load_db()
    if pid not in db['profiles']:
        return jsonify({'error': 'profile not found'}), 404

    payload = request.json or {}
    data = payload.get('data', payload)
    metrics = data.get('metrics', [])
    workouts = data.get('workouts', [])

    # Build metric lookup
    metric_map = {}
    for m in metrics:
        name = m.get('name', '')
        pts = m.get('data', [])
        if name and pts:
            metric_map[name] = pts

    def daily_val(names, date_str, agg='avg'):
        if isinstance(names, str):
            names = [names]
        for name in names:
            pts = metric_map.get(name, [])
            day_pts = []
            for pt in pts:
                pt_date = str(pt.get('date', pt.get('dateComponents', '')))
                if pt_date.startswith(date_str):
                    val = pt.get('qty', pt.get('value', pt.get('avg')))
                    if val is not None:
                        try: day_pts.append(float(val))
                        except: pass
            if day_pts:
                if agg == 'sum': return round(sum(day_pts), 2)
                if agg == 'max': return round(max(day_pts), 2)
                return round(sum(day_pts)/len(day_pts), 2)
        return None

    today = datetime.now().strftime('%Y-%m-%d')
    cutoff = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    all_dates = set()
    for pts in metric_map.values():
        for pt in pts:
            d = str(pt.get('date', pt.get('dateComponents', '')))
            if len(d) >= 10 and cutoff <= d[:10] <= today:
                all_dates.add(d[:10])

    logs_updated = 0
    for date_str in sorted(all_dates):
        entry = {'date': date_str, 'source': 'healthautoexport', 'ts': datetime.now().timestamp()}

        steps = daily_val(['step_count','steps','stepCount'], date_str, 'sum')
        if steps: entry['steps'] = int(steps)

        cals = daily_val(['active_energy','activeEnergyBurned','active_energy_burned'], date_str, 'sum')
        if cals: entry['calsBurned'] = int(cals)

        rhr = daily_val(['resting_heart_rate','restingHeartRate'], date_str, 'avg')
        if rhr: entry['hr'] = round(rhr, 1)
        elif not entry.get('hr'):
            hr = daily_val(['heart_rate','heartRate'], date_str, 'avg')
            if hr: entry['hr'] = round(hr, 1)

        hrv = daily_val(['heart_rate_variability_sdnn','heartRateVariabilitySDNN'], date_str, 'avg')
        if hrv: entry['hrv'] = round(hrv, 1)

        sleep = daily_val(['sleep_duration','sleepDuration','asleep','sleep'], date_str, 'sum')
        if sleep:
            if sleep > 24: sleep = round(sleep/60, 1)
            entry['sleep'] = sleep

        weight = daily_val(['body_mass','bodyMass','weight'], date_str, 'avg')
        if weight:
            if weight < 100: weight = round(weight * 2.20462, 1)
            entry['weight'] = round(weight, 1)

        spo2 = daily_val(['blood_oxygen_saturation','oxygenSaturation','spo2'], date_str, 'avg')
        if spo2:
            if spo2 < 2: spo2 = round(spo2*100, 1)
            entry['spo2'] = spo2

        dist = daily_val(['walking_running_distance','distanceWalkingRunning'], date_str, 'sum')
        if dist: entry['distanceMiles'] = round(dist * 0.621371, 2)

        flights = daily_val(['flights_climbed','flightsClimbed'], date_str, 'sum')
        if flights: entry['flightsClimbed'] = int(flights)

        stand = daily_val(['apple_stand_hour','appleStandHour'], date_str, 'sum')
        if stand: entry['standHours'] = int(stand)

        exercise = daily_val(['apple_exercise_time','appleExerciseTime'], date_str, 'sum')
        if exercise: entry['exerciseMins'] = int(exercise)

        resp = daily_val(['respiratory_rate','respiratoryRate'], date_str, 'avg')
        if resp: entry['respiratoryRate'] = round(resp, 1)

        if len({k for k in entry if k not in ('date','source','ts')}) == 0:
            continue

        logs = db['profiles'][pid].get('logs', [])
        existing = next((l for l in logs if l.get('date') == date_str), None)
        if existing:
            for k, v in entry.items():
                if k not in existing or existing.get('source') == 'healthautoexport':
                    existing[k] = v
        else:
            logs.append(entry)
        db['profiles'][pid]['logs'] = logs
        logs_updated += 1

    workouts_saved = 0
    for w in workouts:
        wid = 'hae_' + str(w.get('id', datetime.now().strftime('%Y%m%d%H%M%S%f')))
        dist_data = w.get('distance', {})
        dist_val = dist_data.get('qty') if isinstance(dist_data, dict) else dist_data
        energy_data = w.get('activeEnergy', {})
        energy_val = energy_data.get('qty') if isinstance(energy_data, dict) else energy_data
        hr_data = w.get('heartRateData', {})
        workout_entry = {
            'id': wid, 'date': str(w.get('start',''))[:10],
            'type': w.get('name','Workout'), 'duration': round(float(w.get('duration',0)), 1),
            'calories': energy_val or 0, 'distance': dist_val or 0,
            'distanceUnit': dist_data.get('units','km') if isinstance(dist_data, dict) else 'km',
            'avgHR': hr_data.get('average') if isinstance(hr_data, dict) else None,
            'maxHR': hr_data.get('max') if isinstance(hr_data, dict) else None,
            'start': w.get('start',''), 'end': w.get('end',''),
            'source': 'healthautoexport', 'has_route': bool(w.get('route'))
        }
        wlist = db['profiles'][pid].get('workouts', [])
        wlist = [x for x in wlist if x.get('id') != wid]
        wlist.append(workout_entry)
        db['profiles'][pid]['workouts'] = wlist
        workouts_saved += 1

    db['profiles'][pid] = prune_old_data(db['profiles'][pid], days=60)
    save_db(db)
    return jsonify({'ok': True, 'logs_updated': logs_updated, 'workouts_saved': workouts_saved})

# ── Export / Import ───────────────────────────────────────────

@app.route('/api/profiles/<pid>/export', methods=['GET'])
def export_profile(pid):
    db = load_db()
    p = db['profiles'].get(pid)
    if not p: return jsonify({'error': 'not found'}), 404
    safe = {k: v for k, v in p.items() if k != 'pin'}
    safe['exported'] = datetime.now().isoformat()
    return Response(json.dumps(safe, indent=2), mimetype='application/json',
                    headers={'Content-Disposition': f'attachment; filename=baseline-{p.get("name","profile")}.json'})

@app.route('/api/export', methods=['GET'])
def export_all():
    db = load_db()
    safe = {'profiles': {p: {k:v for k,v in data.items() if k!='pin'}
                         for p, data in db['profiles'].items()},
            'exported': datetime.now().isoformat()}
    return Response(json.dumps(safe, indent=2), mimetype='application/json',
                    headers={'Content-Disposition': 'attachment; filename=baseline-export.json'})

# ── Health check ──────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health_check():
    db = load_db()
    gpx_count = len([f for f in os.listdir(GPX_DIR) if f.endswith('.gpx')]) if os.path.exists(GPX_DIR) else 0
    return jsonify({'status': 'ok', 'version': '3.0.0', 'app': 'Baseline',
                    'profiles': len(db['profiles']), 'gpx_files': gpx_count, 'db': DB_FILE})

# ── Run ───────────────────────────────────────────────────────

if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(GPX_DIR, exist_ok=True)
    port = int(os.environ.get('PORT', 3000))
    print(f'\n✅ Baseline v3 running at http://0.0.0.0:{port}')
    print(f'   Database: {DB_FILE}')
    print(f'   GPX dir:  {GPX_DIR}')
    app.run(host='0.0.0.0', port=port, debug=False)
